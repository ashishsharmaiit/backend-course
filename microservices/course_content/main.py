import json
import os
from pymongo import MongoClient
from urllib.parse import quote_plus

current_dir = os.path.dirname(os.path.abspath(__file__))

# Load MongoDB credentials
with open(os.path.join(current_dir, 'credentials.json'), 'r') as infile:
    mongo_config = json.load(infile)

# MongoDB setup
username = quote_plus(mongo_config['mongo_user'])
password = quote_plus(mongo_config['mongo_pass'])
cluster_url = mongo_config['mongo_cluster_url']
mongo_uri = f"mongodb+srv://{username}:{password}@{cluster_url}"

mongo_client = MongoClient(mongo_uri)
db = mongo_client["SocratiQ"]
courses_collection = db["course_metadata"]

# Load course data from JSON file
with open(os.path.join(current_dir, 'test_data.json'), 'r') as course_file:
    course_data = json.load(course_file)

# Insert the data into the collection
insertion_result = courses_collection.insert_one(course_data)

# Retrieve and print the ID of the inserted document
inserted_id = insertion_result.inserted_id
print(f"Course data has been inserted into MongoDB with _id: {inserted_id}")
