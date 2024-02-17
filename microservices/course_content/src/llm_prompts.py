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
import math

logging.basicConfig(level=logging.DEBUG)

class SectionDetails(TypedDict):
	sectionNumber: Required[str]
	sectionName: Required[str]
	sectionTopics: Required[str]
	sectionObjective: Required[str]
	sectionTime: Required[str]



def get_section_overview(openai_client, topic, detailedCoursePlan, sectionId):

	current_dir = os.path.dirname(os.path.abspath(__file__))

	try:
		'''Load prompt instructions'''
		instructions = 'You are an AI tutor.'

		system_file = os.path.join(current_dir, '../prompt_section_overview.md')
		if os.path.exists(system_file):
			with io.open(system_file, 'r', encoding='utf-8') as f:
				instructions = f.read()

		current_query = (
			f"Learner is trying to learn '{topic}' "
			f"with the following course plan {detailedCoursePlan}"
			f"Give the JSON output for section index = {sectionId}. "
			)


		section_overview_content = ask_llm(openai_client, instructions, current_query, max_tokens = 4000, temperature=0.4)
		logging.debug(f"Lesson Plan Received from llm: {section_overview_content}")

		return section_overview_content

	except Exception as e:
		print('Error in get_lesson_plan function')
		traceback.print_exc()  # printing stack trace
		response = {'plan': None,
					'status': 400,
					'error': str(e),
					'timestamp': int(time.time())
		}

def get_lesson_content(openai_client, topic, detailedCoursePlan, courseContent, sectionId, lessonId):

	current_dir = os.path.dirname(os.path.abspath(__file__))

	try:
		'''Load prompt instructions'''
		instructions = 'You are an AI tutor.'

		system_file = os.path.join(current_dir, '../prompt_lesson_content.md')
		if os.path.exists(system_file):
			with io.open(system_file, 'r', encoding='utf-8') as f:
				instructions = f.read()

		current_query = (
			f"Learner is trying to learn '{topic}' "
			f"with the following course plan {detailedCoursePlan}"
			f"with the content that learner has so far seen is {courseContent}"
			f"Give the JSON output for section index = {sectionId} and lesson index = {lessonId}. "
			)


		lesson_content = ask_llm(openai_client, instructions, current_query, max_tokens = 4000, temperature=0.4)
		logging.debug(f"lesson_content Received from llm: {lesson_content}")

		return lesson_content

	except Exception as e:
		print('Error in get_lesson_plan function')
		traceback.print_exc()  # printing stack trace
		response = {'plan': None,
					'status': 400,
					'error': str(e),
					'timestamp': int(time.time())
		}
