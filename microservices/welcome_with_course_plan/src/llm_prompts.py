import io
import json
import time
import os
from typing_extensions import TypedDict, Required
import random
import traceback
import tiktoken # type: ignore
from openai_base import ask_llm
import logging

logging.basicConfig(level=logging.DEBUG)

class SectionDetails(TypedDict):
	sectionNumber: Required[str]
	sectionName: Required[str]
	sectionTopics: Required[str]
	sectionObjective: Required[str]
	sectionTime: Required[str]

current_dir = os.path.dirname(os.path.abspath(__file__))

def asking_background(openai_client, topic, welcome_content_test_mode):

	logging.debug(f"test mode: {welcome_content_test_mode}")

	if welcome_content_test_mode:
		logging.debug(f"code inside test mode")
		welcome_content_test_file = os.path.join(current_dir, '../test_json/welcome_content_test_file.json')
		with open(welcome_content_test_file, 'r') as file:
			response = json.load(file)
		return response
	else:

		try:
			instructions = 'You are an AI tutor.'

			system_file = os.path.join(current_dir, '../prompts/prompt.md')
			if os.path.exists(system_file):
				with io.open(system_file, 'r', encoding='utf-8') as f:
					instructions = f.read()

			current_query = ''
			current_query += f"topic: {topic}"

			welcome_content = ask_llm(openai_client, instructions, current_query, max_tokens=3000, temperature = 0.4)
			logging.debug(f"welcome_content: {welcome_content}")
			
			welcome_content_dict = json.loads(welcome_content)

			response_pre = f"{welcome_content_dict['content']}"

			response = {"courseContent": {"-1.-1": {"h1": "Welcome!", "h2": "", "content": response_pre}}}
			logging.debug(f"response being sent from llm prompt: {response}")

			welcome_content_test_file = os.path.join(current_dir, '../test_json/welcome_content_test_file.json')
			with open(welcome_content_test_file, 'w') as file:
				json.dump(response, file, indent=4)

			return response

		except Exception as e:
			print('Error in get_welcome_content function')
			traceback.print_exc()  # printing stack trace
			response = {'plan': None,
						'status': 400,
						'error': str(e),
						'timestamp': int(time.time())
			}


def asking_purpose(openai_client, topic, background, asking_purpose_test_mode):

	logging.debug(f"test mode: {asking_purpose_test_mode}")

	if asking_purpose_test_mode:
		logging.debug(f"code inside test mode")
		welcome_content_test_file = os.path.join(current_dir, '../test_json/background_content_test_file.json')
		with open(welcome_content_test_file, 'r') as file:
			response = json.load(file)
		return response
	else:

		try:
			instructions = 'You are an AI tutor.'

			system_file = os.path.join(current_dir, '../prompts/prompt_asking_purpose.md')
			if os.path.exists(system_file):
				with io.open(system_file, 'r', encoding='utf-8') as f:
					instructions = f.read()

			current_query = ''
			current_query += f"topic: {topic}, background: {background}"

			welcome_content = ask_llm(openai_client, instructions, current_query, max_tokens=3000, temperature = 0.4)
			logging.debug(f"welcome_content: {welcome_content}")
			
			welcome_content_dict = json.loads(welcome_content)

			response_pre = f"{welcome_content_dict['content']}"

			response = {"courseContent": {"-1.0": {"h1": "", "h2": "", "content": response_pre}}}
			logging.debug(f"response being sent from llm prompt: {response}")

			welcome_content_test_file = os.path.join(current_dir, '../test_json/background_content_test_file.json')
			with open(welcome_content_test_file, 'w') as file:
				json.dump(response, file, indent=4)

			return response

		except Exception as e:
			print('Error in get_welcome_content function')
			traceback.print_exc()  # printing stack trace
			response = {'plan': None,
						'status': 400,
						'error': str(e),
						'timestamp': int(time.time())
			}

def asking_duration(openai_client, topic, background, purposeOfLearning, asking_duration_test_mode):

	logging.debug(f"test mode: {asking_duration_test_mode}")

	if asking_duration_test_mode:
		logging.debug(f"code inside test mode")
		welcome_content_test_file = os.path.join(current_dir, '../test_json/asking_duration.json')
		with open(welcome_content_test_file, 'r') as file:
			response = json.load(file)
		return response
	else:

		try:
			instructions = 'You are an AI tutor.'

			system_file = os.path.join(current_dir, '../prompts/prompt_asking_duration.md')
			if os.path.exists(system_file):
				with io.open(system_file, 'r', encoding='utf-8') as f:
					instructions = f.read()

			current_query = ''
			current_query += f"topic: {topic}, background: {background}, purposeOfLearning: {purposeOfLearning}"

			welcome_content = ask_llm(openai_client, instructions, current_query, max_tokens=3000, temperature = 0.4)
			logging.debug(f"welcome_content: {welcome_content}")
			
			welcome_content_dict = json.loads(welcome_content)

			response_pre = f"{welcome_content_dict['content']}"

			response = {"courseContent": {"-1.1": {"h1": "", "h2": "", "content": response_pre}}}
			logging.debug(f"response being sent from llm prompt: {response}")

			welcome_content_test_file = os.path.join(current_dir, '../test_json/asking_duration.json')
			with open(welcome_content_test_file, 'w') as file:
				json.dump(response, file, indent=4)

			return response

		except Exception as e:
			print('Error in get_welcome_content function')
			traceback.print_exc()  # printing stack trace
			response = {'plan': None,
						'status': 400,
						'error': str(e),
						'timestamp': int(time.time())
			}


def giving_course_plan(openai_client, topic, background, purposeOfLearning, durationInHours, giving_course_plan_test_mode):

	logging.debug(f"test mode: {giving_course_plan_test_mode}")

	if giving_course_plan_test_mode:
		logging.debug(f"code inside test mode")
		welcome_content_test_file = os.path.join(current_dir, '../test_json/giving_course_plan_test.json')
		with open(welcome_content_test_file, 'r') as file:
			response = json.load(file)
		return response
	else:

		try:
			instructions = 'You are an AI tutor.'

			system_file = os.path.join(current_dir, '../prompts/prompt_giving_lesson_plan.md')
			if os.path.exists(system_file):
				with io.open(system_file, 'r', encoding='utf-8') as f:
					instructions = f.read()

			current_query = ''
			current_query += f"topic: {topic}, background: {background}, purposeOfLearning: {purposeOfLearning}, durationInHours: {durationInHours}"

			welcome_content = ask_llm(openai_client, instructions, current_query, max_tokens=4000, temperature = 0.6, model_engine="gpt-4-0125-preview")
			logging.debug(f"welcome_content: {welcome_content}")
			
			welcome_content_dict = json.loads(welcome_content)

			response_pre = f"{welcome_content_dict['content']}"

			response = {"courseContent": {"-1.2": {"h1": "Course Plan", "h2": "", "content": response_pre}}}
			logging.debug(f"response being sent from llm prompt: {response}")

			welcome_content_test_file = os.path.join(current_dir, '../test_json/giving_course_plan_test.json')
			with open(welcome_content_test_file, 'w') as file:
				json.dump(response, file, indent=4)

			return response

		except Exception as e:
			print('Error in get_welcome_content function')
			traceback.print_exc()  # printing stack trace
			response = {'plan': None,
						'status': 400,
						'error': str(e),
						'timestamp': int(time.time())
			}
