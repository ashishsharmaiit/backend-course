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

def get_welcome_content(openai_client, courseOptions, detailedCoursePlan, welcome_content_test_mode):
	current_dir = os.path.dirname(os.path.abspath(__file__))

	if welcome_content_test_mode:
		# Read the lesson plan from the file in test mode
		welcome_content_test_file = os.path.join(current_dir, '../welcome_content_test_file.json')
		with open(welcome_content_test_file, 'r') as file:
			response = json.load(file)
		return response
	else:

		try:
			instructions = 'You are an AI tutor.'

			system_file = os.path.join(current_dir, '../prompt.md')
			if os.path.exists(system_file):
				with io.open(system_file, 'r', encoding='utf-8') as f:
					instructions = f.read()

			current_query = ''
			if (len(courseOptions.get('topic', '')) > 0):
				current_query += f"Learner wants to learn {courseOptions.get('topic', '')} in {courseOptions.get('durationInHours', '')} hours."
			if (len(courseOptions.get('teachingStyle', '')) > 0):
				current_query += f"Learner prefers a teaching style that is {courseOptions.get('teachingStyle', '')}."
			if (len(courseOptions.get('focusOn', '')) > 0):
				current_query += f"Learner wants to focus more on {courseOptions.get('focusOn', '')}."
			if (len(courseOptions.get('previousKnowledge', '')) > 0):
				current_query += f"Learner already know about {courseOptions.get('previousKnowledge', '')}."
			if (len(courseOptions.get('purposeFor', '')) > 0):
				current_query += f"Learner wants to learn this for {courseOptions.get('purposeFor', '')}."
			if (len(courseOptions.get('otherConsiderations', '')) > 0):
				current_query += f"Some other things that you can consider are - {courseOptions.get('otherConsiderations', '')}."
			if (len(detailedCoursePlan) > 0):
				current_query += f"The course plan that the learner agreed on is - {detailedCoursePlan}."
			current_query += "You now need to welcome the learner with a welcome message, welcoming the learner to this course. Give a little fun fact about what the learner is trying to learn, little reaffirmation the importance of what learner is learning and give a little detail about the course plan and how you will teach the user with the course plan. Then at the end, have a sentence to connect to the first section after this welcome message. Have this entire messae within 500 words. The narrative should be exciting. Underline, bold, number and bullet points the content wherever it is applicable for easy reading. Have the content in JSON format such as {{\"content\": \"<welcome_content>\"}}"

			welcome_content = ask_llm(openai_client, instructions, current_query)
			logging.debug(f"welcome_content: {welcome_content}")

			welcome_content_escaped = welcome_content.replace('\n', '\\n').replace('\r', '\\r')
			logging.debug(f"welcome_content_escaped: {welcome_content_escaped}")

			welcome_content_dict = json.loads(welcome_content_escaped)

			response_pre = f"{welcome_content_dict['content']}"

			# Replace escaped newline characters with actual newlines
			#response = response_pre.replace('\\n', '\n')

			response = {0: {"h1": "Welcome!", "h2": "", "content": response_pre}}
			
			welcome_content_test_file = os.path.join(current_dir, '../welcome_content_test_file.json')
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
				f"Format the output as JSON. For example: "
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
