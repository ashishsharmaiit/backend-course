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


def get_welcome_content(openai_client, course_options, course_plan_str, welcome_content_test_mode):
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
			if (len(course_options.get('topic', '')) > 0):
				current_query += f"Learner wants to learn {course_options.get('topic', '')} in {course_options.get('duration', '')}."
			if (len(course_options.get('teachingStyle', '')) > 0):
				current_query += f"Learner prefers a teaching style that is {course_options.get('teachingStyle', '')}."
			if (len(course_options.get('focusOn', '')) > 0):
				current_query += f"Learner wants to focus more on {course_options.get('focusOn', '')}."
			if (len(course_options.get('previousKnowledge', '')) > 0):
				current_query += f"Learner already know about {course_options.get('previousKnowledge', '')}."
			if (len(course_options.get('purposeFor', '')) > 0):
				current_query += f"Learner wants to learn this for {course_options.get('purposeFor', '')}."
			if (len(course_options.get('otherConsiderations', '')) > 0):
				current_query += f"Some other things that you can consider are - {course_options.get('otherConsiderations', '')}."
			if (len(course_plan_str) > 0):
				current_query += f"The course plan that the learner agreed on is - {course_plan_str}."
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



