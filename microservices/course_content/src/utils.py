import json
from llm_prompts import get_lesson_plan
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(current_dir, '../config.json'), 'r') as infile:
	config = json.load(infile)

def load_section_details(detailedCoursePlan, sectionNumber: int):
	for index, section in enumerate(detailedCoursePlan):
		if section["sectionNumber"] == sectionNumber:
			return section, index
	return None, -1  # Return None and -1 if the section is not found

def extract_lesson_data(detailedCoursePlan, sec_index, chapter_num, lesson_num):
	try:
		# Extract the specified section
		section = detailedCoursePlan[sec_index]
		# Access the 'lessonPlan' key to get to 'chapters'
		if 'lessonPlan' in section:
			lesson_plan = section['lessonPlan']
			chapter = lesson_plan['chapters'][chapter_num]
			lesson = chapter['lessons'][lesson_num]

			# Prepare the extracted data
			extracted_data = {
				'chapterTitle': chapter['chapterTitle'],
				'lessonTitle': lesson['lessonTitle'],
				'content': lesson['content']
			}

			return extracted_data
		else:
			return {"error": "lessonPlan not found in the section"}
	except IndexError as e:
		return {"error": f"IndexError - {str(e)}"}
	except KeyError as e:
		return {"error": f"KeyError - {str(e)}"}



def check_lesson_exists(detailedCoursePlan, uniqueLessonId):
	highest_unique_lesson_num = -1  # Initialize to -1 to indicate none found
	sec_index_of_highest = -1  # Initialize to -1 to indicate none found

	for section_index, section in enumerate(detailedCoursePlan):
		if "lessonPlan" in section:
			lesson_plan = section["lessonPlan"]
			for chapter_index, chapter in enumerate(lesson_plan["chapters"]):
				for lesson_index, lesson in enumerate(chapter["lessons"]):
					current_lesson_num = lesson.get("uniqueLessonId", -1)
					# Update highest_unique_lesson_num if a higher value is found
					if current_lesson_num > highest_unique_lesson_num:
						highest_unique_lesson_num = current_lesson_num
						sec_index_of_highest = section_index
					# Check if the current lesson matches the uniqueLessonId
					if current_lesson_num == uniqueLessonId:
						# If found, return True with the location details
						return True, section_index, chapter_index, lesson_index

	# After checking all lessons, determine the return value based on the highest_unique_lesson_num found
	if highest_unique_lesson_num == -1:
		# If no lessons with a uniqueLessonId were found at all
		return False, 0, -1, -1
	else:
		# If uniqueLessonId was not found but other lessons with uniqueLessonId exist
		return False, sec_index_of_highest+1, -1, -1

def generate_and_update_lesson_plan(openai_client, detailedCoursePlan, section_num):
	# Assuming `section_num` is based on 1-indexing as per your example
	# Adjust if your indexing scheme is different
	lesson_data_test_mode = True
	section_details, section_index = load_section_details(detailedCoursePlan, section_num)
	lesson_plan_response = get_lesson_plan(openai_client, section_details, lesson_data_test_mode)
	lesson_plan_json = json.loads(lesson_plan_response.get('plan', '{}'))

	insert_unique_lesson_num = 1
	section_details = detailedCoursePlan[section_index]
	
	# Generate lesson plan (simplified example; replace with your actual implementation)
	lesson_plan_response = get_lesson_plan(openai_client, section_details, (config['lesson_data_test_mode']))
	lesson_plan_json = json.loads(lesson_plan_response.get('plan', '{}'))

	for chapter in lesson_plan_json.get('chapters', []):
		# Iterate through lessons in the chapter
		for lesson in chapter.get('lessons', []):
			# Add the uniqueLessonId to the lesson
			lesson['uniqueLessonId'] = insert_unique_lesson_num
			# Increment uniqueLessonId for the next lesson
			insert_unique_lesson_num += 1

	# Update the course plan with the new lesson plan
	detailedCoursePlan[section_index]["lessonPlan"] = lesson_plan_json

	# Return the updated course plan
	return detailedCoursePlan
