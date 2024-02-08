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


def get_lesson_plan(openai_client, section_details: SectionDetails, lesson_data_test_mode=False):

	current_dir = os.path.dirname(os.path.abspath(__file__))

	if lesson_data_test_mode:
		# Read the lesson plan from the file in test mode
		lesson_plan_file = os.path.join(current_dir, '../lesson_data.json')
		with open(lesson_plan_file, 'r') as file:
			response = json.load(file)
		return response
	else:
		try:
			'''Load prompt instructions'''
			instructions = 'You are an AI tutor.'

			system_file = os.path.join(current_dir, '../prompt.md')
			if os.path.exists(system_file):
				with io.open(system_file, 'r', encoding='utf-8') as f:
					instructions = f.read()

			'''Construct prompt query based on SectionDetails'''
			current_query = (
				f"Create a chapter and lesson plan for a section titled '{section_details['sectionName']}' "
				f"covering the topics '{section_details['sectionTopics']}'. "
				f"The objective of this section is to '{section_details['sectionObjective']}'. "
				f"The total time allocated for this section is {section_details['sectionTime']}. "
				f"Organize the content into multiple chapters and within each chapter include multiple lessons. "
				f"Format the output as JSON. For example: "
				f"{{\"chapters\": [{{\"chapterTitle\": \"Example Chapter 1\", \"lessons\": [{{\"lessonTitle\": \"<Lesson Title>\", \"content\": \"...\"}}, {{\"lessonTitle\": \"<Lesson Title>\", \"content\": \"...\"}}]}}]}}"
				)


			lesson_plan = ask_llm(openai_client, instructions, current_query)
			response = {'plan': lesson_plan,
						'status': 200,
						'error': None,
						'timestamp': int(time.time())
			}

			# Save the lesson plan to a JSON file
			lesson_plan_file = os.path.join(current_dir, '../lesson_data.json')
			with open(lesson_plan_file, 'w') as file:
				json.dump(response, file, indent=4)
			return response

		except Exception as e:
			print('Error in get_lesson_plan function')
			traceback.print_exc()  # printing stack trace
			response = {'plan': None,
						'status': 400,
						'error': str(e),
						'timestamp': int(time.time())
			}


def get_lesson_content(openai_client, lesson_request, lesson_content_test_mode=False):

	current_dir = os.path.dirname(os.path.abspath(__file__))

	if lesson_content_test_mode:
		# Read the lesson plan from the file in test mode
		lesson_plan_file = os.path.join(current_dir, '../content.json')
		with open(lesson_plan_file, 'r') as file:
			response = json.load(file)
		return response
	else:
		try:
			'''Load prompt instructions'''
			instructions = 'You are an AI tutor.'
			system_file = os.path.join(current_dir, '../prompt.md')
			if os.path.exists(system_file):
				with io.open(system_file, 'r', encoding='utf-8') as f:
					instructions = f.read()
			'''Construct prompt query based on SectionDetails'''
			current_query = (
				f"Create a 700 words content for the lesson titled '{lesson_request['lessonTitle']}' "
				f"which is within the chapter of '{lesson_request['chapterTitle']}'. "
				f". The objective of this content is '{lesson_request['content']}'. "
				f"The content should not be less than 700 words. The language should be informal, empathetic and should try to take the learner along you by explaining well. Use as many emojis as possible, and structure the content well for easier understanding. Format the output as JSON. For example: "
				f"{{\"content\": \"<lesson_content>\"}}"
				)


			content = ask_llm(openai_client, instructions, current_query)
			logging.debug(f"content in llm request: {content}")

			#escaped_content = content.replace('\n', '\\n')
			#logging.debug(f"escaped content: {escaped_content}")

			try:
				parsed_content = json.loads(content)
				logging.debug(f"parsed_content: {parsed_content}")

				response = {'plan': parsed_content, 'status': 200, 'error': None, 'timestamp': int(time.time())}
			except json.JSONDecodeError as json_err:
				logging.debug(f"JSON parsing error: {json_err}")
				response = {'plan': {}, 'status': 200, 'error': "Failed to parse lesson content as JSON.", 'timestamp': int(time.time())}
			
			# Save the lesson plan to a JSON file
			lesson_content_file = os.path.join(current_dir, '../content.json')
			with open(lesson_content_file, 'w') as file:
				json.dump(response, file, indent=4)
			return response

		except Exception as e:
			logging.debug('Error in get_lesson_content function')
			traceback.print_exc()  # printing stack trace
			response = {'plan': None,
						'status': 400,
						'error': str(e),
						'timestamp': int(time.time())
			}
