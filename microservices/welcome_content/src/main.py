import functions_framework
from openai_base import get_openai_client
from llm_prompts import get_welcome_content,get_lesson_plan, get_lesson_content
from utils import extract_lesson_data, check_lesson_exists, generate_and_update_lesson_plan
import json
import logging
import os
from db_code import get_db_connection

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@functions_framework.http
def process_welcome_data(request):

	welcome_content_test_mode = True
	lesson_content_test_mode = False

	courses_collection = get_db_connection()
	openai_client = get_openai_client()

	if request.method == 'OPTIONS':
		headers = {
			'Access-Control-Allow-Origin': '*',
			'Access-Control-Allow-Methods': 'POST',
			'Access-Control-Allow-Headers': 'Content-Type',
			'Access-Control-Max-Age': '3600'
		}
		return ('', 204, headers)

	headers = {'Access-Control-Allow-Origin': '*'}

	try:
		if request.headers['Content-Type'] == 'application/json':
			course_data = request.get_json()
		else:
			return ('Content-Type not supported!', 415, headers)

		progress_status = course_data.get("Progress_Status", 0)
		course_id = course_data.get("course_id", "")
		course_inputs = course_data.get("course_options", {})

		course_plan = course_data.get("course_plan", {})
		logging.debug(f"Received course data: {course_plan}")

		# Initialize an empty list to hold formatted section descriptions
		formatted_sections = []

		for section in course_plan:
			# Format each section's details into a readable string
			section_str = f"Section {section.get('SectionNumber')}: {section.get('SectionName')}, Topics: {section.get('SectionTopics')}, Objective: {section.get('SectionObjective')}, Duration: {section.get('SectionTime')}."
			formatted_sections.append(section_str)

		# Join all section descriptions into a single string with line breaks or any other separator you prefer
		course_plan_str = " ".join(formatted_sections)


		inserted_id = None

		if progress_status == 0 and not course_id:
			insertion_result = courses_collection.insert_one(course_data)
			inserted_id = insertion_result.inserted_id
			
			welcome_content = get_welcome_content(openai_client, course_inputs, course_plan_str, welcome_content_test_mode)

			response = {
				"course_id": str(inserted_id),
				"course_content": welcome_content
			}

			return (json.dumps(response), 200, headers)


		if course_id:
			find_unique_lesson_num = progress_status + 1

			
			exists, sec_index, chapter_num, lesson_num = check_lesson_exists(course_plan, find_unique_lesson_num)
			logging.debug(f"Values: {exists}, {sec_index},{chapter_num},{lesson_num},")
			
			
			section_num = sec_index + 1

			
			if not exists:
				course_plan = generate_and_update_lesson_plan(openai_client, course_plan, section_num)
				logging.debug(f"New Course Plan: {course_plan}")
				exists, sec_index, chapter_num, lesson_num = check_lesson_exists(course_plan, find_unique_lesson_num)
				logging.debug(f"Values: {exists}, {sec_index},{chapter_num},{lesson_num},")
				section_num = sec_index + 1

			
			lesson_request = extract_lesson_data(course_plan, sec_index, chapter_num, lesson_num)
			logging.debug(f"lesson_request: {lesson_request}")

			
			lesson_content = get_lesson_content(openai_client, lesson_request, lesson_content_test_mode)
			logging.debug(f"lesson_content: {lesson_content}")

			
			detailed_content = lesson_content.get('plan', {})
			lesson_content_text = detailed_content.get('content', '')
			section = course_plan[sec_index]

			
			section_heading = f"Section {section_num}: {section.get('SectionName', '')}"

			chapter_heading = lesson_request['chapter_title']
			

			response = {
							"course_plan": course_plan,
							"course_content": 
							{find_unique_lesson_num: 
								{"h1": section_heading, "h2": chapter_heading, "content": lesson_content_text			
								}
							}
						}
			return (json.dumps(response), 200, headers)

	except json.JSONDecodeError as json_err:
		#logging.error(f"JSON Error: {json_err}")
		return ("JSON Decode Error", 400, headers)
	except Exception as e:
		#logging.error(f"An error occurred: {e}")
		return (f"An error occurred: {str(e)}", 500, headers)


