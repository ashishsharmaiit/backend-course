import io
import json
import os
from pymongo import MongoClient
import time
import openai
from openai import OpenAI
from urllib.parse import quote_plus
from typing_extensions import TypedDict, Required
import random
import traceback
import tiktoken # type: ignore



model_name="gpt-3.5-turbo"
encoding = tiktoken.encoding_for_model(model_name)


current_dir = os.path.dirname(os.path.abspath(__file__))

# Load MongoDB credentials
with open(os.path.join(current_dir, 'credentials.json'), 'r') as infile:
    credentials = json.load(infile)

os.environ['OPENAI_API_KEY'] = credentials['openai_key_primary']

openai_client = OpenAI(
  organization="org-9ckxNJxqNOipkJbzJDpgoyA6",
  api_key=os.environ['OPENAI_API_KEY'],
)

# MongoDB setup
username = quote_plus(credentials['mongo_user'])
password = quote_plus(credentials['mongo_pass'])
cluster_url = credentials['mongo_cluster_url']
mongo_uri = f"mongodb+srv://{username}:{password}@{cluster_url}"

mongo_client = MongoClient(mongo_uri)
db = mongo_client["SocratiQ"]
courses_collection = db["course_metadata"]

class SectionDetails(TypedDict):
	SectionNumber: Required[str]
	SectionName: Required[str]
	SectionTopics: Required[str]
	SectionObjective: Required[str]
	SectionTime: Required[str]


def ask_llm(instructions: str, query: str, model_engine="gpt-3.5-turbo", response_format={"type": "json_object"}, max_tokens=1024, temperature=0.2, use_assistants=False, openai_assistant=None, thread_id=None) -> str:
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

def get_lesson_plan(section_details: SectionDetails):
    try:
        '''Load prompt instructions'''
        instructions = 'You are an AI tutor.'
        system_file = os.path.join(current_dir, 'prompt.md')
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


        lesson_plan = ask_llm(instructions, current_query)
        response = {'plan': lesson_plan,
                    'status': 200,
                    'error': None,
                    'timestamp': int(time.time())
        }
    except Exception as e:
        print('Error in get_lesson_plan function')
        traceback.print_exc()  # printing stack trace
        response = {'plan': None,
                    'status': 400,
                    'error': str(e),
                    'timestamp': int(time.time())
        }
    return response



# Load course data from JSON file
with open(os.path.join(current_dir, 'test_data.json'), 'r') as course_file:
    course_data = json.load(course_file)

# Insert the data into the collection
insertion_result = courses_collection.insert_one(course_data)

# Retrieve and print the ID of the inserted document
inserted_id = insertion_result.inserted_id
print(f"Course data has been inserted into MongoDB with _id: {inserted_id}")


def load_section_details(section_number: int):
    for section in course_data["Course Plan"]:
        if section["SectionNumber"] == section_number:
            return section
    return None  # Return None if the section is not found

# Load details for section 1
section_1_details = load_section_details(1)

if section_1_details:
    lesson_plan_response = get_lesson_plan(section_1_details)
    print(lesson_plan_response)
    try:
        lesson_plan_json = json.loads(lesson_plan_response['plan'])
    except json.JSONDecodeError as e:
        print("Error parsing lesson plan JSON:", e)
        lesson_plan_json = {}
else:
    print("Section 1 details not found.")


section_number = section_1_details["SectionNumber"]

# MongoDB update operation
update_result = courses_collection.update_one(
    {"Course Plan.SectionNumber": section_number},
    {"$set": {"Course Plan.$.LessonPlan": lesson_plan_json}}
)

print(f"Updated {update_result.modified_count} document(s) in MongoDB.")

