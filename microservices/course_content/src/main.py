import functions_framework
from openai_base import get_openai_client
from llm_prompts import get_welcome_content,get_lesson_plan, get_lesson_content
from utils import extract_lesson_data, check_lesson_exists, generate_and_update_lesson_plan
import json
import logging
import os
from db_code import get_db_connection

##comment to test
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@functions_framework.http
def process_lesson_data(request):

	welcome_content_test_mode = True
	lesson_content_test_mode = True

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
			courseData = request.get_json()
		else:
			return ('Content-Type not supported!', 415, headers)
		
		logging.debug(f"Received input: {courseData}")

		progressStatus = courseData.get("progressStatus", 0)
		courseId = courseData.get("courseId", "")
		courseOptions = courseData.get("courseOptions", {})

		detailedCoursePlan = courseData.get("detailedCoursePlan", {})

		# Initialize an empty list to hold formatted section descriptions
		formatted_sections = []

		for section in detailedCoursePlan:
			# Format each section's details into a readable string
			section_str = f"Section {section.get('sectionNumber')}: {section.get('sectionName')}, Topics: {section.get('sectionTopics')}, Objective: {section.get('sectionObjective')}, Duration: {section.get('sectionTime')}."
			formatted_sections.append(section_str)

		# Join all section descriptions into a single string with line breaks or any other separator you prefer
		detailedCoursePlan_str = " ".join(formatted_sections)
		
		logging.debug(f"detailedCoursePlan_str: {detailedCoursePlan_str}")


		inserted_id = None

		if progressStatus == 0 and not courseId:
			insertion_result = courses_collection.insert_one(courseData)
			inserted_id = insertion_result.inserted_id
			logging.debug(f"inserted_id: {inserted_id}")
	
			welcome_content = get_welcome_content(openai_client, courseOptions, detailedCoursePlan_str, welcome_content_test_mode)
			logging.debug(f"welcome_content: {welcome_content}")


			response = {
				"courseId": str(inserted_id),
				"courseContent": welcome_content
			}
			logging.debug(f"response: {response}")

			return (json.dumps(response), 200, headers)


		if courseId:
			find_unique_lesson_num = progressStatus + 1

			logging.debug("courseId", courseId, "progressStatus", progressStatus)

			exists, sec_index, chapter_num, lesson_num = check_lesson_exists(detailedCoursePlan, find_unique_lesson_num)
			logging.debug(f"Values: {exists}, {sec_index},{chapter_num},{lesson_num},")
			
			
			section_num = sec_index + 1

			
			if not exists:
				detailedCoursePlan = generate_and_update_lesson_plan(openai_client, detailedCoursePlan, section_num)
				logging.debug(f"New Course Plan: {detailedCoursePlan}")
				exists, sec_index, chapter_num, lesson_num = check_lesson_exists(detailedCoursePlan, find_unique_lesson_num)
				logging.debug(f"Values: {exists}, {sec_index},{chapter_num},{lesson_num},")
				section_num = sec_index + 1

			
			lesson_request = extract_lesson_data(detailedCoursePlan, sec_index, chapter_num, lesson_num)
			logging.debug(f"lesson_request: {lesson_request}")

			
			lesson_content = get_lesson_content(openai_client, lesson_request, lesson_content_test_mode)
			logging.debug(f"lesson_content: {lesson_content}")

			
			detailed_content = lesson_content.get('plan', {})
			logging.debug(f"detailed_content: {detailed_content}")

			lesson_content_text = detailed_content.get('content', '')
			logging.debug(f"lesson_content_text: {lesson_content_text}")

			section = detailedCoursePlan[sec_index]
			logging.debug(f"section: {section}")

			
			section_heading = f"Section {section_num}: {section.get('sectionName', '')}"
			logging.debug(f"section_heading: {section_heading}")

			chapter_heading = lesson_request['chapterTitle']
			
			logging.debug(f"chapter_heading: {chapter_heading}")

			response = {
							"detailedCoursePlan": detailedCoursePlan,
							"courseContent": 
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


