import json
from llm_prompts import get_lesson_plan

def load_section_details(course_plan, section_number: int):
	for index, section in enumerate(course_plan):
		if section["SectionNumber"] == section_number:
			return section, index
	return None, -1  # Return None and -1 if the section is not found

def extract_lesson_data(course_plan, sec_index, chapter_num, lesson_num):
	try:
		# Extract the specified section
		section = course_plan[sec_index]
		# Access the 'LessonPlan' key to get to 'Chapters'
		if 'LessonPlan' in section:
			lesson_plan = section['LessonPlan']
			chapter = lesson_plan['Chapters'][chapter_num]
			lesson = chapter['Lessons'][lesson_num]

			# Prepare the extracted data
			extracted_data = {
				'chapter_title': chapter['ChapterTitle'],
				'lesson_title': lesson['LessonTitle'],
				'lesson_content': lesson['Content']
			}

			return extracted_data
		else:
			return {"error": "LessonPlan not found in the section"}
	except IndexError as e:
		return {"error": f"IndexError - {str(e)}"}
	except KeyError as e:
		return {"error": f"KeyError - {str(e)}"}



def check_lesson_exists(course_plan, unique_lesson_num):
	highest_unique_lesson_num = -1  # Initialize to -1 to indicate none found
	sec_index_of_highest = -1  # Initialize to -1 to indicate none found

	for section_index, section in enumerate(course_plan):
		if "LessonPlan" in section:
			lesson_plan = section["LessonPlan"]
			for chapter_index, chapter in enumerate(lesson_plan["Chapters"]):
				for lesson_index, lesson in enumerate(chapter["Lessons"]):
					current_lesson_num = lesson.get("unique_lesson_num", -1)
					# Update highest_unique_lesson_num if a higher value is found
					if current_lesson_num > highest_unique_lesson_num:
						highest_unique_lesson_num = current_lesson_num
						sec_index_of_highest = section_index
					# Check if the current lesson matches the unique_lesson_num
					if current_lesson_num == unique_lesson_num:
						# If found, return True with the location details
						return True, section_index, chapter_index, lesson_index

	# After checking all lessons, determine the return value based on the highest_unique_lesson_num found
	if highest_unique_lesson_num == -1:
		# If no lessons with a unique_lesson_num were found at all
		return False, 0, -1, -1
	else:
		# If unique_lesson_num was not found but other lessons with unique_lesson_num exist
		return False, sec_index_of_highest+1, -1, -1

def generate_and_update_lesson_plan(openai_client, course_plan, section_num):
	# Assuming `section_num` is based on 1-indexing as per your example
	# Adjust if your indexing scheme is different
	lesson_data_test_mode = True
	section_details, section_index = load_section_details(course_plan, section_num)
	lesson_plan_response = get_lesson_plan(openai_client, section_details, lesson_data_test_mode)
	lesson_plan_json = json.loads(lesson_plan_response.get('plan', '{}'))

	insert_unique_lesson_num = 1
	section_details = course_plan[section_index]
	lesson_data_test_mode = True
	# Generate lesson plan (simplified example; replace with your actual implementation)
	lesson_plan_response = get_lesson_plan(openai_client, section_details, lesson_data_test_mode)
	lesson_plan_json = json.loads(lesson_plan_response.get('plan', '{}'))

	for chapter in lesson_plan_json.get('Chapters', []):
		# Iterate through lessons in the chapter
		for lesson in chapter.get('Lessons', []):
			# Add the unique_lesson_num to the lesson
			lesson['unique_lesson_num'] = insert_unique_lesson_num
			# Increment unique_lesson_num for the next lesson
			insert_unique_lesson_num += 1

	# Update the course plan with the new lesson plan
	course_plan[section_index]["LessonPlan"] = lesson_plan_json

	# Return the updated course plan
	return course_plan
