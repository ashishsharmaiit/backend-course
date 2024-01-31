import functions_framework
from db_code import get_db_connection, update_lesson_content
from openai_client import get_openai_client
from llm_requests import get_lesson_plan, get_lesson_content
from utils import load_section_details, extract_lesson_data
import json

@functions_framework.http
def process_course_data(request):
    # Initialize test mode flags and setup
    lesson_data_test_mode = True  
    lesson_content_test_mode = True
    courses_collection = get_db_connection()
    openai_client = get_openai_client()

    try:
        # Load course data from JSON file
        with open('../test_data.json', 'r') as course_file:
            course_data = json.load(course_file)
        
        # Insert the data into the collection
        insertion_result = courses_collection.insert_one(course_data)
        inserted_id = insertion_result.inserted_id

        # Load details for section 1
        section_1_details = load_section_details(course_data, 1)

        if section_1_details:
            # Get lesson plan
            lesson_plan_response = get_lesson_plan(openai_client, section_1_details, lesson_data_test_mode)
            lesson_plan_json = json.loads(lesson_plan_response.get('plan', '{}'))

            # Update lesson plan in MongoDB
            courses_collection.update_one(
                {"_id": inserted_id, "Course Plan.SectionNumber": section_1_details["SectionNumber"]},
                {"$set": {"Course Plan.$.LessonPlan": lesson_plan_json}}
            )

            # Get and update lesson content
            chapter_num, lesson_num = 0, 0
            lesson_request = extract_lesson_data(lesson_plan_json, chapter_num, lesson_num)
            lesson_content = get_lesson_content(openai_client, lesson_request, lesson_content_test_mode)
            detailed_content = lesson_content.get('plan', '')
            update_lesson_content(courses_collection, inserted_id, section_1_details["SectionNumber"], chapter_num, lesson_num, detailed_content)

            # Prepare response data
            response_data = {
                "inserted_id": str(inserted_id),
                "lesson_plan": lesson_plan_json,
                "detailed_content": detailed_content
            }
            return (json.dumps(response_data), 200, {'Content-Type': 'application/json'})
        else:
            return ("Section details not found", 404)

    except Exception as e:
        return (f"An error occurred: {str(e)}", 500)

