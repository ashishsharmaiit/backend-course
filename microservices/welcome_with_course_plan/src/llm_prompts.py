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

def get_welcome_content(openai_client, topic):
	try:
		instructions = 'You are an AI tutor.'

		system_file = os.path.join(current_dir, '../prompt.md')
		if os.path.exists(system_file):
			with io.open(system_file, 'r', encoding='utf-8') as f:
				instructions = f.read()

		current_query = ''
		current_query += f"Learner wants to learn about {topic} and has just given this input so far."
		current_query += "You now need to welcome the learner to the platform LearnwithAI. You then need to give a little reaffirmation on the importance of what learner is learning, and how you can help the learner with your knowledge base, ability to customize content and answering queries. Then give a suggested course plan that can work for them. Then at the end, ask them whether they will like to customize this course plan based on what they already know, or the areas they want to focus on, or if they have any application in mind for learning this, or any other changes they will like to make to the course. Use many emojis to make the content looks interesting. Use an informal language that can embark trust, and don't use a verbose language. Give your response in this JSON format: {{\"content\": \"<welcome_content>\"}}"

		welcome_content = ask_llm(openai_client, instructions, current_query)
		logging.debug(f"welcome_content: {welcome_content}")
		
		welcome_content_dict = json.loads(welcome_content)

		response_pre = f"{welcome_content_dict['content']}"

		response = {0: {"h1": "Welcome!", "h2": "", "content": response_pre}}
		logging.debug(f"response being sent from llm prompt: {response}")

		return response

	except Exception as e:
		print('Error in get_welcome_content function')
		traceback.print_exc()  # printing stack trace
		response = {'plan': None,
					'status': 400,
					'error': str(e),
					'timestamp': int(time.time())
		}

