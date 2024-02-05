import io
import os
import json
import time
import openai
from openai import OpenAI
import random
import regex
import traceback
import functions_framework # type: ignore
import tiktoken # type: ignore
from typing_extensions import NotRequired, Required, TypedDict
import logging

model_name="gpt-3.5-turbo-1106"
encoding = tiktoken.encoding_for_model(model_name)
current_dir = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


with open(os.path.join(current_dir, 'openai_key.json'), 'r') as infile:
	key_document = json.load(infile)
	os.environ['OPENAI_API_KEY'] = key_document['openai_key_primary']
	
openai_client = OpenAI(
  organization="org-9ckxNJxqNOipkJbzJDpgoyA6",
  api_key=os.environ['OPENAI_API_KEY'],
)

class CourseOptions(TypedDict):
	topic: Required[str]
	duration: Required[str]
	teachingStyle: Required[str]
	focusOn: NotRequired[str]
	purposeFor: NotRequired[str]
	previousKnowledge: NotRequired[str]
	otherConsiderations: NotRequired[str]
	
@functions_framework.http
def http_course_plan(request):
	course_plan_test_mode = False
	run_job = False
	if request.method == 'OPTIONS':
		headers = {
			'Access-Control-Allow-Origin': '*',
			'Access-Control-Allow-Methods': 'POST',
			'Access-Control-Allow-Headers': 'Content-Type',
			'Access-Control-Max-Age': '3600'
		}
		return ('', 204, headers)

	headers = {'Access-Control-Allow-Origin': '*'}
	request_json = request.get_json()
	request_args = request.args

	try:
		if request.headers['Content-Type'] == 'application/json':
			course_options: CourseOptions = request_json.get('course_options', {})
			run_job = True
		elif request_args:
			course_options: CourseOptions = request_args.get('course_options', {})
			run_job = True
		else:
			return ('Content-Type not supported!', 415, headers)

		if run_job:
			print("Course plan query for user @ {}".format(time.time()))
			res = main_course_plan(course_options, course_plan_test_mode)
			return (res, 200, headers)
		res = {'plan': None,
			'options': None,
			'status': 500,
			'error': 'Invalid query arguments',
			'timestamp': int(time.time())
		}
		return (res, 200, headers)
	
	except json.JSONDecodeError as json_err:
		#logging.error(f"JSON Error: {json_err}")
		return ("JSON Decode Error", 400, headers)
	except Exception as e:
		#logging.error(f"An error occurred: {e}")
		return (f"An error occurred: {str(e)}", 500, headers)
	

def ask_llm(instructions: str, query: str, model_engine="gpt-3.5-turbo-1106", max_tokens=1024, temperature=0.2, response_format={"type": "json_object"}, use_assistants=False, openai_assistant=None, thread_id=None) -> str:
	messages = []
	msg_content = None
	if not use_assistants:
		# add instructions for chat completion api
		messages = [
			{"role": "system", "content": instructions}
		]
	messages = messages + [
		{"role": "user", "content": query}
	]
	if use_assistants:
		'''assistants api only accepts user messages currently'''
		if openai_assistant is None:
			openai_assistant = openai_client.beta.assistants.create(
				instructions=instructions,
				model=model_engine,
			)

		if thread_id is None:
			thread = openai_client.beta.threads.create(
				messages=messages
			)
			thread_id = thread.id
		else:
			'''add message to thread'''
			message = openai_client.beta.threads.messages.create(
				thread_id=thread_id,
				role="user",
				content= query
			)
		run = openai_client.beta.threads.runs.create(
			thread_id=(thread_id if thread_id is not None else thread.id),
			assistant_id=openai_assistant.id
		)
		while run.status == "in_progress" or run.status == "queued":
			time.sleep(1)
			run = openai_client.beta.threads.runs.retrieve(
				thread_id=(thread_id if thread_id is not None else thread.id),
				run_id=run.id
			)
			if run.status == "completed":
				response = openai_client.beta.threads.messages.list(
					limit=1,
					thread_id=(thread_id if thread_id is not None else thread.id)
				)
				msg_content = response.data[0].content[0].text.value
				break
			if run.status == "requires_action":
				break
	else:
		# retrial logic else fail gracefully
		for delay_secs in (2**x for x in range(0, 3)):
			try:
				response = openai_client.chat.completions.create(
					model=model_engine,
					n=1,
					response_format=response_format,
					max_tokens=max_tokens,
					temperature=temperature,
					messages=messages)
				msg_content = response.choices[0].message.content
				break
			except openai.OpenAIError as e:
				print(e)
				randomness_collision_avoidance = random.randint(0, 1000) / 1000.0
				sleep_dur = delay_secs + randomness_collision_avoidance
				time.sleep(sleep_dur)
				continue
	if msg_content is None:
		raise Exception('Open AI Error')
	return msg_content

def main_course_plan(course_options: CourseOptions, course_plan_test_mode):
	if course_plan_test_mode:
		# Read the lesson plan from the file in test mode
		course_plan_file = os.path.join(current_dir, './course_plan_file.json')
		with open(course_plan_file, 'r') as file:
			response = json.load(file)
		return response
	try:
		'''Load prompt instructions'''
		instructions = 'You are an AI tutor.'
		system_file = os.path.join(current_dir, 'prompt.md')
		if os.path.exists(system_file):
			with io.open(system_file, 'r', encoding='utf-8') as f:
				instructions = f.read()
		'''Construct prompt query'''
		current_query = ''
		if (len(course_options.get('topic', '')) > 0):
			current_query += f"I want to learn about {course_options.get('topic', '')}."
		if course_options.get('durationInHours', 0) > 0:
			current_query += f"in {course_options.get('durationInHours')} hours."
		if (len(course_options.get('teachingStyle', '')) > 0):
			current_query += f"I prefer a teaching style that is {course_options.get('teachingStyle', '')}."
		if (len(course_options.get('focusOn', '')) > 0):
			current_query += f"I want to focus more on {course_options.get('focusOn', '')}."
		if (len(course_options.get('previousKnowledge', '')) > 0):
			current_query += f"I already know about {course_options.get('previousKnowledge', '')}."
		if (len(course_options.get('purposeFor', '')) > 0):
			current_query += f"I want to learn this for {course_options.get('purposeFor', '')}."
		if (len(course_options.get('otherConsiderations', '')) > 0):
			current_query += f"Some other things that you can consider - {course_options.get('otherConsiderations', '')}."
		current_query += "Please create a course plan for me in the JSON format."
		plan_json = ask_llm(instructions, current_query)
		response = {'response': plan_json,
			'status': 200,
			'error': None,
			'timestamp': int(time.time())
		}
		course_plan_file = os.path.join(current_dir, './course_plan_file.json')
		with open(course_plan_file, 'w') as file:
			json.dump(response, file, indent=4)

	except Exception as e:
		print('Google cloud function error')
		traceback.print_exc() # printing stack trace
		response = {'plan': None,
			'options': None,
			'status': 400,
			'error': str(e),
			'timestamp': int(time.time())
		}
	return response
