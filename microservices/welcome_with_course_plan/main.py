import functions_framework
from utils.openai_base import get_openai_client
from utils.llm_prompts import asking_background, asking_purpose, asking_duration, giving_course_plan
import json
import logging
import os

##comment to test
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(current_dir, './config.json'), 'r') as infile:
	config = json.load(infile)


openai_client = get_openai_client()

@functions_framework.http
def welcome_with_plan(request):

	if request.method == 'OPTIONS':
		headers = {
			'Access-Control-Allow-Origin': '*',
			'Access-Control-Allow-Methods': 'POST',
			'Access-Control-Allow-Headers': 'Content-Type',
			'Access-Control-Max-Age': '3600'
		}
		return ('', 204, headers)

	headers = {'Access-Control-Allow-Origin': '*'}
	welcome_content_test_mode = config['welcome_content_test_mode']
	asking_purpose_test_mode = config['asking_purpose_test_mode']
	asking_duration_test_mode = config['asking_duration_test_mode']
	giving_course_plan_test_mode =config['giving_course_plan_test_mode']

	try:
		if request.headers['Content-Type'] == 'application/json':
			courseData = request.get_json()
		else:
			return ('Content-Type not supported!', 415, headers)
		
		logging.debug(f"Received input: {courseData}")

		courseOptions = courseData.get("courseOptions", {})
		topic = courseOptions.get("topic", "")
		
		logging.debug(f"extracted topic: {topic}")

		background = courseOptions.get("background", "")

		logging.debug(f"extracted background: {background}")

		purposeOfLearning = courseOptions.get("purposeOfLearning", "")
		logging.debug(f"purposeOfLearning: {purposeOfLearning}")

		durationInHours = courseOptions.get("durationInHours", "")
		logging.debug(f"durationInHours: {durationInHours}")


		if not background:
			response = asking_background(openai_client, topic, welcome_content_test_mode)
			logging.debug(f"asking_background response: {response}")
		elif not purposeOfLearning:
			response = asking_purpose(openai_client, topic, background, asking_purpose_test_mode)
			logging.debug(f"asking_purpose: {response}")
		elif not durationInHours:
			response = asking_duration(openai_client, topic, background, purposeOfLearning, asking_duration_test_mode)
			logging.debug(f"asking_duration: {response}")
		else:
			response = giving_course_plan(openai_client, topic, background, purposeOfLearning, durationInHours, giving_course_plan_test_mode)
			logging.debug(f"giving_course_plan: {response}")


		return (json.dumps(response), 200, headers)

	except json.JSONDecodeError as json_err:
		#logging.error(f"JSON Error: {json_err}")
		return ("JSON Decode Error", 400, headers)
	except Exception as e:
		#logging.error(f"An error occurred: {e}")
		return (f"An error occurred: {str(e)}", 500, headers)


