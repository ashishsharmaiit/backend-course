import io
import json
import time
import os
from typing_extensions import TypedDict, Required
import random
import traceback
import tiktoken # type: ignore

class SectionDetails(TypedDict):
	SectionNumber: Required[str]
	SectionName: Required[str]
	SectionTopics: Required[str]
	SectionObjective: Required[str]
	SectionTime: Required[str]


def ask_llm(openai_client, instructions: str, query: str, model_engine="gpt-3.5-turbo", response_format={"type": "json_object"}, max_tokens=1024, temperature=0.2, use_assistants=False, openai_assistant=None, thread_id=None) -> str:
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

def get_lesson_plan(openai_client, section_details: SectionDetails, lesson_data_test_mode=False):

	current_dir = os.path.dirname(os.path.abspath(__file__))

	if test_mode:
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
				f"Create a chapter and lesson plan for a section titled '{section_details['SectionName']}' "
				f"covering the topics '{section_details['SectionTopics']}'. "
				f"The objective of this section is to '{section_details['SectionObjective']}'. "
				f"The total time allocated for this section is {section_details['SectionTime']}. "
				f"Organize the content into multiple chapters and within each chapter include multiple lessons. "
				f"Format the output as JSON. For example: "
				f"{{\"Chapters\": [{{\"ChapterTitle\": \"Example Chapter 1\", \"Lessons\": [{{\"LessonTitle\": \"Lesson 1\", \"Content\": \"...\"}}, {{\"LessonTitle\": \"Lesson 2\", \"Content\": \"...\"}}]}}]}}"
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