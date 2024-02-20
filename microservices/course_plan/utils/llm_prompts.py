import io
import json
import time
import os
from typing_extensions import TypedDict, Required
import traceback
from .openai_base import ask_llm
import logging
import math

logging.basicConfig(level=logging.DEBUG)

class SectionDetails(TypedDict):
	sectionNumber: Required[str]
	sectionName: Required[str]
	sectionTopics: Required[str]
	sectionObjective: Required[str]
	sectionTime: Required[str]


def get_lesson_plan(openai_client, courseOptions, detailedCoursePlan, section_detail, lesson_plan_test_mode):

	current_dir = os.path.dirname(os.path.abspath(__file__))
	
	logging.debug(f"test mode: {lesson_plan_test_mode}")

	if lesson_plan_test_mode:
		logging.debug(f"code inside test mode")
		welcome_content_test_file = os.path.join(current_dir, '../test_json/lesson_plan.json')
		with open(welcome_content_test_file, 'r') as file:
			response = json.load(file)
		return response
	else:

		try:
			'''Load prompt instructions'''
			instructions = 'You are an AI tutor.'

			system_file = os.path.join(current_dir, '../prompts/prompt_lesson_plan.md')
			if os.path.exists(system_file):
				with io.open(system_file, 'r', encoding='utf-8') as f:
					instructions = f.read()

			time_str = section_detail.get("sectionTime", 0)

			try:
				# Check if the value is already a number (int or float)
				if isinstance(time_str, (int, float)):
					time = float(time_str)
				elif isinstance(time_str, str):
					# Attempt conversion from string to float
					time = float(time_str)
				else:
					raise TypeError("sectionTime must be a string or a number.")
			except ValueError:
				print(f"Could not convert sectionTime '{time_str}' to a float.")
				time = 0  # or some other default value or handling as appropriate
			except TypeError as e:
				print(e)
				time = 0

			print(f"Time for section: {time} hours")
			number_of_lessons = math.ceil(time * 20)

			'''Construct prompt query based on SectionDetails'''
			current_query = (
				f"courseInputs: {courseOptions}, "
				f"coursePlan: {detailedCoursePlan}, "
				f"section_detail: {section_detail}, "
				f"number_of_lessons = {number_of_lessons}."
				)


			lesson_plan = ask_llm(openai_client, instructions, current_query, max_tokens = 4000, temperature=0.4, model_engine="gpt-4-0125-preview")
			logging.debug(f"Output received from LLM: {lesson_plan}")
			
			try:
				lesson_plan_dict = json.loads(lesson_plan)
			except json.JSONDecodeError:
				logging.error("Failed to decode JSON from LLM response")
				lesson_plan_dict = {}  # Fallback to an empty dictionary in case of decoding error

			lessonPlan = lesson_plan_dict.get("lessonPlan", [])
			logging.debug(f"Lesson Plan Received from LLM: {lessonPlan}")
			'''
			lesson_plan_file = os.path.join(current_dir, '../test_json/lesson_plan.json')
			with open(lesson_plan_file, 'w') as file:
				json.dump(lessonPlan, file, indent=4)
			'''
			return lessonPlan

		except Exception as e:
			print('Error in get_lesson_plan function')
			traceback.print_exc()  # printing stack trace
			response = {'plan': None,
						'status': 400,
						'error': str(e),
						'timestamp': int(time.time())
			}


def get_section_plan(openai_client, section_plan_narrative, section_plan_test_mode):

	current_dir = os.path.dirname(os.path.abspath(__file__))
	
	logging.debug(f"test mode: {section_plan_test_mode}")

	if section_plan_test_mode:
		logging.debug(f"code inside test mode")
		welcome_content_test_file = os.path.join(current_dir, '../test_json/section_plan.json')
		with open(welcome_content_test_file, 'r') as file:
			response = json.load(file)
		return response
	else:

		try:
			'''Load prompt instructions'''
			instructions = 'You are an AI tutor.'

			system_file = os.path.join(current_dir, '../prompts/prompt_section_plan.md')
			if os.path.exists(system_file):
				with io.open(system_file, 'r', encoding='utf-8') as f:
					instructions = f.read()

			'''Construct prompt query based on SectionDetails'''
			current_query = (
				f"text:  {section_plan_narrative} "
				)


			section_plan = ask_llm(openai_client, instructions, current_query)
			logging.debug(f"Section Plan Received from llm: {section_plan}")
			'''
			section_plan_file = os.path.join(current_dir, '../test_json/section_plan.json')
			with open(section_plan_file, 'w') as file:
				json.dump(section_plan, file, indent=4)
			'''
			return section_plan

		except Exception as e:
			print('Error in get_lesson_plan function')
			traceback.print_exc()  # printing stack trace
			response = {'plan': None,
						'status': 400,
						'error': str(e),
						'timestamp': int(time.time())
			}

