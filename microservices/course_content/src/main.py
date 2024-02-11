import functions_framework
from openai_base import get_openai_client
from llm_prompts import get_lesson_plan, get_section_overview, get_lesson_content
import json
import logging
import os
from db_code import get_db_connection

##comment to test
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(current_dir, '../config.json'), 'r') as infile:
	config = json.load(infile)


@functions_framework.http
def process_lesson_data(request):


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


		if sectionId != -1:
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
			lesson_heading = lesson.get('lesson_name', 'Default Lesson Name')
			logging.debug(f"lesson_heading: {lesson_heading}")
		else:
			logging.error(f"Invalid lessonId: {lessonId} for sectionId: {sectionId}")
			lesson_heading = 'Invalid Lesson'


		'''
		courseContent = courseData.get("courseContent", {})

		if str(progressStatus) in courseContent:
			find_unique_lesson_num = progressStatus+1
		else:
			find_unique_lesson_num = progressStatus

		lesson_exists, sec_index, chapter_num, lesson_num = check_lesson_exists(detailedCoursePlan, find_unique_lesson_num)
		logging.debug(f"Values: {lesson_exists}, {sec_index},{chapter_num},{lesson_num},")
		
		
		section_num = sec_index + 1
		'''
		
		if lessonId == -1:
			try:
				lesson_plan = get_lesson_plan(openai_client, topic, detailedCoursePlan, sectionId)
				logging.debug(f"Lesson Plan Received: {lesson_plan}")

				lesson_plan_json = json.loads(lesson_plan)
				# Directly update the section with the lesson plan content, avoiding the nested 'lessonPlan' key
				if 'lessonPlan' in detailedCoursePlan[sectionId]:
					# If there's already a lessonPlan, you might want to update or append to it
					# This example assumes you want to replace it
					detailedCoursePlan[sectionId]['lessonPlan'] = lesson_plan_json['lessonPlan']
				else:
					detailedCoursePlan[sectionId].update(lesson_plan_json)

				logging.debug(f"Updated Course Plan: {detailedCoursePlan}")

			except json.JSONDecodeError:
				logging.error("Failed to decode lessonPlan JSON.")
				return ('Invalid lessonPlan format', 400, headers)

			section_overview_content = get_section_overview(openai_client, topic, detailedCoursePlan, sectionId)
			logging.debug(f"section_overview_content: {section_overview_content}")
			try:
				section_overview_content_dict = json.loads(section_overview_content)
				section_overview_dict = section_overview_content_dict.get("content", "")
			except json.JSONDecodeError as e:
				logging.error(f"Failed to decode JSON: {e}")
				section_overview_dict = ""  # Fallback in case of parsing error


			response = {
				"detailedCoursePlan": detailedCoursePlan,
				"courseContent": 
				{key: 
					{"h1": section_heading, "h2": "Section Overview", "content": section_overview_dict}
				}
			}
			return (json.dumps(response), 200, headers)			
		
		else:
			
			lesson_content = get_lesson_content(openai_client, topic, detailedCoursePlan, courseContent, sectionId, lessonId)
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
			'''
			exists, sec_index, chapter_num, lesson_num = check_lesson_exists(detailedCoursePlan, find_unique_lesson_num)
			logging.debug(f"Values: {exists}, {sec_index},{chapter_num},{lesson_num},")
			section_num = sec_index + 1
			
			
			subsection_index = 0
			lesson_index = 0
			
			lesson_request = extract_lesson_data(detailedCoursePlan, sectionId, subsection_index, lesson_index)
			logging.debug(f"lesson_request: {lesson_request}")

			
			lesson_content = get_lesson_content(openai_client, lesson_request, config['lesson_content_test_mode'])
			logging.debug(f"lesson_content: {lesson_content}")

			
			detailed_content = lesson_content.get('plan', {})
			logging.debug(f"detailed_content: {detailed_content}")

			lesson_content_text = detailed_content.get('content', '')
			logging.debug(f"lesson_content_text: {lesson_content_text}")

			section = detailedCoursePlan[sec_index]
			logging.debug(f"section: {section}")

			

			chapter_heading = lesson_request['chapterTitle']
			
			logging.debug(f"chapter_heading: {chapter_heading}")
			'''


	except json.JSONDecodeError as json_err:
		#logging.error(f"JSON Error: {json_err}")
		return ("JSON Decode Error", 400, headers)
	except Exception as e:
		#logging.error(f"An error occurred: {e}")
		return (f"An error occurred: {str(e)}", 500, headers)


