import functions_framework
from openai_base import get_openai_client
from llm_prompts import get_lesson_plan, get_section_plan
import json
from utils import update_lesson_plan
import logging
import os

##comment to test
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(current_dir, '../config.json'), 'r') as infile:
	config = json.load(infile)

section_plan_test_mode = config['section_plan_test_mode']
lesson_plan_test_mode = config['lesson_plan_test_mode']

@functions_framework.http
def create_course_plan(request):

	

	if request.method == 'OPTIONS':
		headers = {
			'Access-Control-Allow-Origin': '*',
			'Access-Control-Allow-Methods': 'POST',
			'Access-Control-Allow-Headers': 'Content-Type',
			'Access-Control-Max-Age': '3600'
		}
		return ('', 204, headers)

	headers = {'Access-Control-Allow-Origin': '*'}
	
	openai_client = get_openai_client()

	try:
		if request.headers['Content-Type'] == 'application/json':
			courseData = request.get_json()
		else:
			return ('Content-Type not supported!', 415, headers)
		
		logging.debug(f"Received input: {courseData}")

		detailedCoursePlan = courseData.get('detailedCoursePlan', '')
		courseOptions = courseData.get('courseOptions', '')
		courseContent = courseData.get('courseContent', {})
		section_plan_narrative = courseContent['-1.-4']

		# Check if detailedCoursePlan is blank and courseContent with key -1.-4 exists
		if not detailedCoursePlan and '-1.-4' in courseContent and section_plan_narrative:
			# Your logic here when detailedCoursePlan is blank and -1.-4 has content
			response = get_section_plan(openai_client, section_plan_narrative, section_plan_test_mode)
			logging.debug(f"response: {response}")
		elif detailedCoursePlan:
			section_id = 0
			section_detail = detailedCoursePlan[section_id]
			lessonPlan = section_detail.get('lessonPlan', {})
			if not lessonPlan:
				response_pre = get_lesson_plan(openai_client, courseOptions, detailedCoursePlan, section_detail, lesson_plan_test_mode)
				logging.debug(f"response_pre: {response_pre}")

				updated_course_plan = update_lesson_plan(detailedCoursePlan, response_pre, section_id)
				response = {"detailedCoursePlan": updated_course_plan}
				logging.debug(f"newDetailedCoursePlan: {response}")

			else:
				response = {"lesson plan exists": "blank"}

		return (json.dumps(response), 200, headers)		


	except json.JSONDecodeError as json_err:
		#logging.error(f"JSON Error: {json_err}")
		return ("JSON Decode Error", 400, headers)
	except Exception as e:
		#logging.error(f"An error occurred: {e}")
		return (f"An error occurred: {str(e)}", 500, headers)


