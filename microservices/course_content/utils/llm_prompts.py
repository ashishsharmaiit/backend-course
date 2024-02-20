import io
import json
import time
import os
from typing_extensions import TypedDict, Required
import traceback
from .openai_base import ask_llm
import logging
from .utils import getPreviousContent

logging.basicConfig(level=logging.DEBUG)

class SectionDetails(TypedDict):
	sectionNumber: Required[str]
	sectionName: Required[str]
	sectionTopics: Required[str]
	sectionObjective: Required[str]
	sectionTime: Required[str]


def get_lesson_content(openai_client, courseOptions, detailedCoursePlan, courseContent, sectionId, lessonId):

	current_dir = os.path.dirname(os.path.abspath(__file__))

	try:
		'''Load prompt instructions'''
		instructions = 'You are an AI tutor.'

		system_file = os.path.join(current_dir, '../prompts/prompt_lesson_content.md')
		if os.path.exists(system_file):
			with io.open(system_file, 'r', encoding='utf-8') as f:
				instructions = f.read()

			sectionNumber = sectionId + 1
			section = detailedCoursePlan[sectionId]
			sectionName = section.get('SectionName', '')
			lessonNumber = lessonId + 1
			lessonPlan = section.get('lessonPlan', [])
			lessonDetails = lessonPlan[lessonId]
			previousContent = getPreviousContent(courseContent, sectionId, lessonId)
			current_query = (
				f"courseInputs: {courseOptions}, "
				f"coursePlan {detailedCoursePlan}, "
				f"Number and Name of Module: {sectionNumber} and {sectionName}."
				f"Number, Name and Topics of the Module: {lessonNumber} and {lessonDetails}."
				f"Previous content that the learner has already learnt: {previousContent}"
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

def get_section_overview(openai_client, courseOptions, detailedCoursePlan, sectionId, section_overview_test_mode):

	current_dir = os.path.dirname(os.path.abspath(__file__))

	if section_overview_test_mode:
		logging.debug(f"code inside test mode")
		section_overview_file = os.path.join(current_dir, '../test_json/section_overview.json')
		with open(section_overview_file, 'r') as file:
			response = json.load(file)
		return response
	else:
		try:
			'''Load prompt instructions'''
			instructions = 'You are an AI tutor.'

			system_file = os.path.join(current_dir, '../prompts/prompt_section_overview.md')
			if os.path.exists(system_file):
				with io.open(system_file, 'r', encoding='utf-8') as f:
					instructions = f.read()

			sectionNumber = sectionId + 1
			section = detailedCoursePlan[sectionId]
			sectionName = section.get('SectionName', '')
			current_query = (
				f"courseInputs: {courseOptions}, "
				f"coursePlan {detailedCoursePlan}, "
				f"Number and Name of Section for Overview Generation: {sectionNumber} and {sectionName}."
				)

			section_overview_content = ask_llm(openai_client, instructions, current_query)
			logging.debug(f"section_overview_content Received from llm: {section_overview_content}")
			'''
			section_overview_file = os.path.join(current_dir, '../test_json/section_overview.json')
			with open(section_overview_file, 'w') as file:
				json.dump(section_overview_content, file, indent=4)
			'''
			return section_overview_content

		except Exception as e:
			print('Error in get_lesson_plan function')
			traceback.print_exc()  # printing stack trace
			response = {'plan': None,
						'status': 400,
						'error': str(e),
						'timestamp': int(time.time())
			}
