from pymongo import MongoClient
from urllib.parse import quote_plus
import json
import os

def get_db_connection():
	current_dir = os.path.dirname(os.path.abspath(__file__))
	with open(os.path.join(current_dir, '../credentials.json'), 'r') as infile:
		credentials = json.load(infile)

	username = quote_plus(credentials['mongo_user'])
	password = quote_plus(credentials['mongo_pass'])
	cluster_url = credentials['mongo_cluster_url']
	mongo_uri = f"mongodb+srv://{username}:{password}@{cluster_url}"

	mongo_client = MongoClient(mongo_uri)
	db = mongo_client["SocratiQ"]
	return db["course_metadata"]


def update_lesson_content(collection, document_id, section_num, chapter_num, lesson_num, new_content):
    try:
        # Construct the path to the lesson content
        detailed_content_path = f"Course Plan.$[section].LessonPlan.Chapters.{chapter_num}.Lessons.{lesson_num}.detailed_content"

        # Perform the update operation
        update_result = collection.update_one(
            {"_id": document_id, "Course Plan.SectionNumber": section_num},
            {"$set": {detailed_content_path: new_content}},
            array_filters=[{"section.SectionNumber": section_num}]
        )

        # Check if the update was successful
        if update_result.modified_count > 0:
            print(f"Updated lesson content successfully in document {document_id}.")
        else:
            print(f"No changes made to the document {document_id}.")

    except Exception as e:
        print(f"An error occurred while updating the lesson content: {e}")