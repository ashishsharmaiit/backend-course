import functions_framework
from openai_base import get_openai_client
from llm_prompts import get_welcome_content
import json
import logging
import os

##comment to test
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(current_dir, '../config.json'), 'r') as infile:
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
	logging.debug(f"extracted topic: {welcome_content_test_mode}")

	try:
		if request.headers['Content-Type'] == 'application/json':
			courseData = request.get_json()
		else:
			return ('Content-Type not supported!', 415, headers)
		
		logging.debug(f"Received input: {courseData}")

		courseOptions = courseData.get("courseOptions", {})
		topic = courseOptions.get("topic", "")
		
		logging.debug(f"extracted topic: {topic}")

		welcome_content_with_plan = get_welcome_content(openai_client, topic, welcome_content_test_mode)
		logging.debug(f"welcome_content_with_plan: {welcome_content_with_plan}")

		return (json.dumps(welcome_content_with_plan), 200, headers)

	except json.JSONDecodeError as json_err:
		#logging.error(f"JSON Error: {json_err}")
		return ("JSON Decode Error", 400, headers)
	except Exception as e:
		#logging.error(f"An error occurred: {e}")
		return (f"An error occurred: {str(e)}", 500, headers)


