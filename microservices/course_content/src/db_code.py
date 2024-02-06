from pymongo import MongoClient
from urllib.parse import quote_plus
import json
import os

def get_db_connection():
	current_dir = os.path.dirname(os.path.abspath(__file__))
	with open(os.path.join(current_dir, '../config.json'), 'r') as infile:
		config = json.load(infile)

	username = quote_plus(config['mongo_user'])
	password = quote_plus(config['mongo_pass'])
	cluster_url = config['mongo_cluster_url']
	mongo_uri = f"mongodb+srv://{username}:{password}@{cluster_url}"

	mongo_client = MongoClient(mongo_uri)
	db = mongo_client["SocratiQ"]
	return db["course_metadata"]

