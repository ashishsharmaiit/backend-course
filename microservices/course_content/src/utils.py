import json

def load_section_details(course_data, section_number: int):
	for section in course_data["Course Plan"]:
		if section["SectionNumber"] == section_number:
			return section
	return None  # Return None if the section is not found

def extract_lesson_data(plan_data, chapter_num, lesson_num):
	try:
		# Extract the specified chapter and lesson
		chapter = plan_data['Chapters'][chapter_num]
		lesson = chapter['Lessons'][lesson_num]

		# Prepare the extracted data
		extracted_data = {
			'chapter_title': chapter['ChapterTitle'],
			'lesson_title': lesson['LessonTitle'],
			'lesson_content': lesson['Content']
		}

		return extracted_data

	except (IndexError, KeyError, json.JSONDecodeError) as e:
		print("Error extracting lesson data:", e)
		return json.dumps({'error': str(e)})
