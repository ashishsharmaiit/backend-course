import openai
import os
import json

def get_openai_client():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_dir, '../credentials.json'), 'r') as infile:
        credentials = json.load(infile)

    os.environ['OPENAI_API_KEY'] = credentials['openai_key_primary']
    return openai.OpenAI(organization="org-9ckxNJxqNOipkJbzJDpgoyA6", 
                         api_key=os.environ['OPENAI_API_KEY'])
