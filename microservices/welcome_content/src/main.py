import functions_framework
from openai_base import get_openai_client
from llm_prompts import get_welcome_content
import json
import logging
import os
from db_code import get_db_connection

logging.basicConfig(level=logging.DEBUG)

@functions_framework.http
def process_welcome_data(request):

	welcome_content_test_mode = True
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

		progress_status = course_data.get("Progress_Status", {})
		course_id = course_data.get("course_id", "")
		course_inputs = course_data.get("course_options", {})
		section_progress = progress_status.get("section_status")

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

		if section_progress == 0 and not course_id:
			insertion_result = courses_collection.insert_one(course_data)
			inserted_id = insertion_result.inserted_id
			
			welcome_content = get_welcome_content(openai_client, course_inputs, course_plan_str, welcome_content_test_mode)

			response = {
				"course_id": str(inserted_id),
				"welcome_content": welcome_content
			}
			return (json.dumps(response), 200, headers)

	except json.JSONDecodeError as json_err:
		#logging.error(f"JSON Error: {json_err}")
		return ("JSON Decode Error", 400, headers)
	except Exception as e:
		#logging.error(f"An error occurred: {e}")
		return (f"An error occurred: {str(e)}", 500, headers)

