import io
import openai
import os
import json
import time
import random
import functions_framework

import traceback
import tiktoken # type: ignore
from typing_extensions import Required, TypedDict, List

model_name="gpt-3.5-turbo-1106"
encoding = tiktoken.encoding_for_model(model_name)
current_dir = os.path.dirname(os.path.abspath(__file__))

class Lesson(TypedDict):
	content: Required[str]
	lessonTitle: Required[str]
	uniqueLessonId: Required[int]
	
class Chapter(TypedDict):
	lessons: List[Lesson]
	chapterTitle: Required[str]

class CourseContent(TypedDict):
	h1: Required[str]
	h2: Required[str]
	content: Required[str]

def get_openai_client():
	with open(os.path.join(current_dir, 'config.json'), 'r') as infile:
		config = json.load(infile)
		os.environ['OPENAI_API_KEY'] = config['openai_key_primary']

	return openai.OpenAI(organization="org-9ckxNJxqNOipkJbzJDpgoyA6", 
						 api_key=os.environ['OPENAI_API_KEY'])

openai_client = get_openai_client()


def ask_llm(openai_client, instructions: str, query: str, model_engine="gpt-3.5-turbo-1106", max_tokens=1024, temperature=0.2, use_assistants=False, openai_assistant=None, thread_id=None) -> str:
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


@functions_framework.http
def http_query_resolver(request):
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
			user_query: str = request_json.get('query', '')
			course_content: CourseContent = request_json.get('course_content', {})
			run_job = True
		elif request_args:
			user_query: str = request_args.get('query', '')
			course_content: CourseContent = request_args.get('course_content', {})
			run_job = True
		else:
			return ('Content-Type not supported!', 415, headers)

		if run_job:
			print("Course plan query for user @ {}".format(time.time()))
			res = main_query_resolver(user_query, course_content)
			return (res, 200, headers)
		res = {'response': None,
			'status': 500,
			'error': 'Invalid query arguments',
			'timestamp': int(time.time())
		}
		return (res, 200, headers)
	
	except json.JSONDecodeError as json_err:
		return ("JSON Decode Error", 400, headers)
	except Exception as e:
		return (f"An error occurred: {str(e)}", 500, headers)
	
def main_query_resolver(user_query: str, course_content: CourseContent):
	try:
		'''Load prompt instructions'''
		instructions = 'You are an AI tutor.'
		system_file = os.path.join(current_dir, 'prompt.md')
		if os.path.exists(system_file):
			with io.open(system_file, 'r', encoding='utf-8') as f:
				instructions = f.read()

		instructions += "Here's the relevant chapter context information for user queries: \n\n"
		if len(course_content.get('h1', '')) > 0:
			instructions += f"{course_content['h1']} \n\n"
		if len(course_content.get('h2', '')) > 0:
			instructions += f"{course_content['h2']} \n\n"
		if len(course_content.get('content', '')) > 0:
			instructions += f"{course_content['content']} \n\n"

		response = ask_llm(openai_client, instructions, user_query)
		response = {'response': response,
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
			'status': 400,
			'error': str(e),
			'timestamp': int(time.time())
		}
	return response
	
