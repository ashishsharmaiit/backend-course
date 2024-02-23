import functions_framework
from utils.openai_base import get_openai_client
from utils.llm_prompts import get_section_overview, get_lesson_content
import json
import logging
import os

##comment to test
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(current_dir, './config.json'), 'r') as infile:
	config = json.load(infile)

section_overview_test_mode = config['section_overview_test_mode']
@functions_framework.http
def process_lesson_data(request):



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

		progressStatus = courseData.get("progressStatus", {})
		logging.debug(f"Progress Status: {progressStatus}")


		detailedCoursePlan = courseData.get("detailedCoursePlan", {})
		logging.debug(f"Course Plan: {detailedCoursePlan}")
		courseOptions = courseData.get("courseOptions", {})
		logging.debug(f"courseOptions: {courseOptions}")
		courseContent = courseData.get("courseContent", {})

		topic = courseOptions.get("topic", "")
		logging.debug(f"topic: {topic}")


		sectionId = progressStatus[0].get("sectionId", 0)
		lessonId = progressStatus[0].get("lessonId", 0)
		logging.debug(f"sectionId: {sectionId}")
		logging.debug(f"lessonId: {lessonId}")

		key = f"{sectionId}.{lessonId}"


		section = detailedCoursePlan[sectionId]
		logging.debug(f"section: {section}")
		section_heading = section.get('sectionName', '')
		logging.debug(f"section_heading: {section_heading}")
		


		if 0 <= lessonId:
			lesson_plan = section.get('lessonPlan', [])
			logging.debug(f"lesson_plan: {lesson_plan}")

			lesson = lesson_plan[lessonId]
			logging.debug(f"lesson: {lesson}")

			# Get the lesson name, with a default value if not found (unlikely in this case)
			lesson_heading = lesson.get('lessonName', 'Default Lesson Name')
			logging.debug(f"lesson_heading: {lesson_heading}")
		else:
			logging.error(f"Invalid lessonId: {lessonId} for sectionId: {sectionId}")
			lesson_heading = 'Invalid Lesson'


		
		if lessonId == -1:

			section_overview_content = get_section_overview(openai_client, courseOptions, detailedCoursePlan, sectionId, section_overview_test_mode)
			logging.debug(f"section_overview_content: {section_overview_content}")
			try:
				section_overview_content_dict = json.loads(section_overview_content)
				section_overview_dict = section_overview_content_dict.get("content", "")
			except json.JSONDecodeError as e:
				logging.error(f"Failed to decode JSON: {e}")
				section_overview_dict = ""  # Fallback in case of parsing error


			response = {
				"courseContent": 
				{key: 
					{"h1": section_heading, "h2": "Module Overview", "content": section_overview_dict}
				}
			}
			return (json.dumps(response), 200, headers)			
		
		else:
			
			lesson_content = get_lesson_content(openai_client, courseOptions, detailedCoursePlan, courseContent, sectionId, lessonId)
			logging.debug(f"lesson_content: {lesson_content}")
			try:
				lesson_content_dict = json.loads(lesson_content)
				lesson_dict = lesson_content_dict.get("content", "")
			except json.JSONDecodeError as e:
				logging.error(f"Failed to decode JSON: {e}")
				section_overview_dict = ""  # Fallback in case of parsing error

			response = {
				"courseContent": 
				{key: 
					{"h1": "", "h2": lesson_heading, "content": lesson_dict}
				}
			}
			return (json.dumps(response), 200, headers)		


	except json.JSONDecodeError as json_err:
		#logging.error(f"JSON Error: {json_err}")
		return ("JSON Decode Error", 400, headers)
	except Exception as e:
		#logging.error(f"An error occurred: {e}")
		return (f"An error occurred: {str(e)}", 500, headers)

