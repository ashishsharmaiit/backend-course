import functions_framework
from db_code import get_db_connection, update_lesson_content
from openai_client import get_openai_client
from llm_requests import get_lesson_plan, get_lesson_content
from utils import load_section_details, extract_lesson_data
import json
import logging
import os

logging.basicConfig(level=logging.DEBUG)

@functions_framework.http
def process_course_data(request):
	# Initialize test mode flags and setup
	welcome_content_test_mode=False
	lesson_data_test_mode = True  
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
			course_data = request.get_json()
			#logging.debug(f"Received course data: {course_data}")
		else:
			return ('Content-Type not supported!', 415, headers)

		progress_status = course_data.get("Progress_Status", {})
		course_id = course_data.get("course_id", "")
		inserted_id = None

		if progress_status.get("section_status") == 0 and not course_id:
			current_dir = os.path.dirname(os.path.abspath(__file__))
			welcome_content = get_welcome_content(openai_client, course_data, )
			return (json.dumps(welcome_content), 200, headers)

		if lesson_data_test_mode:
			insertion_result = courses_collection.insert_one(course_data)
			inserted_id = insertion_result.inserted_id

			section_1_details = load_section_details(course_data, 1)

			if section_1_details:
				# Get lesson plan
				lesson_plan_response = get_lesson_plan(openai_client, section_1_details, lesson_data_test_mode)
				lesson_plan_json = json.loads(lesson_plan_response.get('plan', '{}'))

				# Update lesson plan in MongoDB
				courses_collection.update_one(
					{"_id": inserted_id, "Course Plan.SectionNumber": section_1_details["SectionNumber"]},
					{"$set": {"Course Plan.$.LessonPlan": lesson_plan_json}}
				)

				# Get and update lesson content
				chapter_num, lesson_num = 0, 0
				lesson_request = extract_lesson_data(lesson_plan_json, chapter_num, lesson_num)
				lesson_content = get_lesson_content(openai_client, lesson_request, lesson_content_test_mode)
				detailed_content = lesson_content.get('plan', '')
				update_lesson_content(courses_collection, inserted_id, section_1_details["SectionNumber"], chapter_num, lesson_num, detailed_content)

				# Prepare response data
				response_data = {
					"inserted_id": str(inserted_id),
					"lesson_plan": lesson_plan_json,
					"detailed_content": detailed_content
				}
				return (json.dumps(response_data), 200, headers)
		else:
			return ("Section details not found", 404)

	except json.JSONDecodeError as json_err:
		#logging.error(f"JSON Error: {json_err}")
		return ("JSON Decode Error", 400, headers)
	except Exception as e:
		#logging.error(f"An error occurred: {e}")
		return (f"An error occurred: {str(e)}", 500, headers)


