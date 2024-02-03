import io
import json
import time
import os
from typing_extensions import TypedDict, Required
import random
import traceback
import tiktoken # type: ignore
from openai_base import ask_llm

def get_welcome_content(openai_client, course_options, welcome_content_test_mode):
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
			current_query += "Give a fun fact about the topic that the learner wants to learn within 200 words, and give a brief introduction about the importance of learning this topic within 500 words, so that the learner feels encouraged about continue learning it. Give this input in JSON input such as {{\"fun_fact\": \"<fun_fact_content>\", \"intro\": \"<intro_content>\" }}"



			lesson_content = ask_llm(openai_client, instructions, current_query)
			response = {'plan': lesson_content,
						'status': 200,
						'error': None,
						'timestamp': int(time.time())
			}

			welcome_content_test_file = os.path.join(current_dir, '../welcome_content_test_file.json')
			with open(welcome_content_test_file, 'w') as file:
				json.dump(response, file, indent=4)
			return response

		except Exception as e:
			print('Error in get_lesson_content function')
			traceback.print_exc()  # printing stack trace
			response = {'plan': None,
						'status': 400,
						'error': str(e),
						'timestamp': int(time.time())
			}



