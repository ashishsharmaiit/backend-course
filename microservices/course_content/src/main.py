from db_code import get_db_connection, update_lesson_content
from openai_client import get_openai_client
from llm_requests import get_lesson_plan, get_lesson_content
from utils import load_section_details, extract_lesson_data
import json

#test modes flags
lesson_data_test_mode = True  
lesson_content_test_mode = True

# MongoDB and OpenAI setup
courses_collection = get_db_connection()
openai_client = get_openai_client()

# Load course data from JSON file
try:
	with open('../test_data.json', 'r') as course_file:
		course_data = json.load(course_file)
except FileNotFoundError:
	print("File test_data.json not found.")
	exit()

# Insert the data into the collection
insertion_result = courses_collection.insert_one(course_data)
inserted_id = insertion_result.inserted_id
print(f"Course data has been inserted into MongoDB with _id: {inserted_id}")


# Load details for section 1
section_1_details = load_section_details(course_data, 1)


if section_1_details:
	lesson_plan_response = get_lesson_plan(openai_client, section_1_details, lesson_data_test_mode)
	print(lesson_plan_response)

	try:
		lesson_plan_json = json.loads(lesson_plan_response.get('plan', '{}'))
	except json.JSONDecodeError as e:
		print("Error parsing lesson plan JSON:", e)
		lesson_plan_json = {}

	section_number = section_1_details["SectionNumber"]

	update_result = courses_collection.update_one(
		{"_id": inserted_id, "Course Plan.SectionNumber": section_number},
		{"$set": {"Course Plan.$.LessonPlan": lesson_plan_json}}
	)

	print(f"Updated {update_result.modified_count} document(s) in MongoDB.")
else:
	print("Section 1 details not found.")

chapter_num = 0  # Assuming you want to update the first chapter
lesson_num = 0  # Assuming you want to update the first lesson
lesson_request = extract_lesson_data(lesson_plan_json, chapter_num, lesson_num)

lesson_content = get_lesson_content(openai_client, lesson_request, lesson_content_test_mode)

print(lesson_content)

lesson_db_entry = lesson_content.get('plan', '{}')

# Check if lesson_db_entry is a string and convert it to a dictionary
if isinstance(lesson_db_entry, str):
    lesson_db_entry = json.loads(lesson_db_entry)

# Extract the detailed content if it exists
if 'content' in lesson_db_entry:
    detailed_content = lesson_db_entry['content']
else:
    detailed_content = ''

# Call the function to update the lesson content in MongoDB with detailed_content
update_lesson_content(courses_collection, inserted_id, section_1_details["SectionNumber"], chapter_num, lesson_num, detailed_content)
