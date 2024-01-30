from db_connection import get_db_connection
from openai_client import get_openai_client
from llm_requests import get_lesson_plan
import json

lesson_data_test_mode = False  # or False, depending on your testing scenario

# MongoDB setup
courses_collection = get_db_connection()

# OpenAI client setup
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


def load_section_details(section_number: int):
    for section in course_data["Course Plan"]:
        if section["SectionNumber"] == section_number:
            return section
    return None  # Return None if the section is not found

# Load details for section 1
section_1_details = load_section_details(1)


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
