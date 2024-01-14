import random
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
import os
import time
import re
import json

app = Flask(__name__)
CORS(app)

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

users = [
    {"userid": 1, "username": "user1", "password": "pass1", "name": "Ashish"},
    {"userid": 2, "username": "user2", "password": "pass2", "name": "Anagh"},
    {"userid": 3, "username": "user3", "password": "pass3", "name": ""}
]


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    for user in users:
        if user['username'] == username and user['password'] == password:
            return jsonify({"userid": user['userid'], "name": user['name']})
    
    return jsonify({"userid": None, "name": None})

@app.route('/api/books_names', methods=['GET', 'POST'])
def books_names():

    
    # Flag for test mode
    test_mode = True  # Set to True to read from the saved file, False to make a new request

    if request.method == 'POST':

        data = request.get_json()  # Get JSON data from the request
        textBoxValue = data.get('textBoxValue', '')  # Extract textBoxValue
        print("textBoxValue received:", textBoxValue)  # Print the received textBoxValue


        if not test_mode:
            # Make a new request and save the response
            response = client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "You are a author who writes books for me."},
                    {"role": "user", "content": "Give me titles of 4 interesting books that you can write on this topic -" + textBoxValue + ". Give output in JSON in this format {\n  \"books\": [\n    \"{title1}\",\n    \"{title2}  \",\n.... Keep the language of the title simple so that I can understand the topic. Don't mention any chapter numbers in json."}
                ],
                temperature=0.7,
                max_tokens=100,
                top_p=1
            )

            # Save the new response to a file
            with open('booknames.json', 'w') as file:
                json.dump(response, file, default=lambda o: o.__dict__, indent=4)

        # Read from the saved file for processing
        with open('booknames.json', 'r') as file:
            saved_response = json.load(file)
            response_content = saved_response['choices'][0]['message']['content']
    

        if test_mode:
            time.sleep(3)  # Sleep for 3 seconds

        # Handling incomplete JSON and formatting the response
        try:
            if not response_content.strip().endswith('}'):
                response_content += '"\n]}'  # Simple fix, may need adjustments

            response_json = json.loads(response_content)
            book_titles = response_json.get('books', [])
            formatted_books = []
            for title in book_titles:
                formatted_book = {
                    "title": title,
                    "description": f"This book talks about {title}"
                }
                formatted_books.append(formatted_book)
            response = {"books": formatted_books} 
            print(response)
            return jsonify(response)

        except json.JSONDecodeError:
            return jsonify({"error": "Invalid response content"})

    else:
        return jsonify({"message": "Send me some data!"})


@app.route('/api/table_of_contents', methods=['POST'])
def table_of_contents():

    data = request.get_json()  # Get JSON data from the request
    book_title = data.get('title', '')  # Extract textBoxValue
    book_description = data.get('description')
    user_interest = data.get('userInterest')

    print(book_title, book_description, user_interest)
    
    
    test_mode = True  # Set to True to read from the saved file, False to make a new request

    if request.method == 'POST':
        if not test_mode:

            # Make a new request and save the response
            response = client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "You are a author who writes books for me."},
                    {"role": "user", "content": "Give me chapter names in chronological order for a book on -" + book_title + " - by dividing it in 10 chapters. While suggesting chapters consider that user is interested in - " + user_interest + ". Give output in JSON in this format {\n  \"chapters\": [\n    \"{chapter1_name}\",\n    \"{chapter2_name}  \",\n.... Keep the language of the chapters simple so that I can understand the topic."}
                ],
                temperature=0.7,
                max_tokens=200,
                top_p=1
            )

            # Save the new response to a file
            with open('tableofcontent.json', 'w') as file:
                json.dump(response, file, default=lambda o: o.__dict__, indent=4)

        # Read from the saved file for processing
        with open('tableofcontent.json', 'r') as file:
            saved_response = json.load(file)

            # Parse the 'content' string as JSON
            content = json.loads(saved_response['choices'][0]['message']['content'])

            # Extract chapter titles from the parsed JSON
            chapter_titles = content['chapters']
            pattern = re.compile(r'^\d+\.\s*')

            # Transform each chapter title into the required dictionary format
            # and remove chapter numbers at the beginning
            chapters = [{"chapter_name": pattern.sub('', title)} for title in chapter_titles]

        if test_mode:
            time.sleep(3)  # Sleep for 3 seconds

    response = {
        'table_of_contents': chapters
    }
    print(response)
    return jsonify(response)


@app.route('/api/get_chapter', methods=['POST'])
def get_chapter():
    data = request.get_json()
    book_title = data.get('book_title')  # Example of how you might receive the chapter number
    chapter_name = data.get('chapter_name')  # Example of how you might receive the chapter number

    test_mode = True  # Set to True to read from the saved file, False to make a new request

    if request.method == 'POST':
        if not test_mode:

            # Make a new request and save the response
            response = client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "You are a author who writes books for me."},
                    {"role": "user", "content": "You are writing a short book on - " + book_title + ". You are currently writing a chapter on - " + chapter_name + " within 200 words. Give output in JSON in this format {\n  \"content\": [\n    \"{chapter_content}\"}"}
                ],
                temperature=0.7,
                max_tokens=300,
                top_p=1
            )

            # Save the new response to a file
            with open('chaptercontent.json', 'w') as file:
                json.dump(response, file, default=lambda o: o.__dict__, indent=4)

        # Read from the saved file for processing
        with open('chaptercontent.json', 'r') as file:
            saved_response = json.load(file)

            # Parse the 'content' string as JSON
            content = json.loads(saved_response['choices'][0]['message']['content'])

            # Extract chapter titles from the parsed JSON
            chapter_content = content['content']
            print(chapter_content)

        if test_mode:
            time.sleep(3)  # Sleep for 3 seconds

    chapter_part_1 = {
    "content": "dfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdsklfdk dffkjdlkj dfkjdfljdljllklkj dffjkdlkjfl.\n\n"
               "dfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfk.\n\n"
               "dfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfk.dfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfk\n\n"
               "dfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfk.\n\n"
               "dfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfk.\n\n"
               "dfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfk.\n\n"
               "dfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfkdfjlkdfjlk dfkjdfljd dfkjdflkjdfl dfkjdfkdfk."
    }

    response = {
        'chapter_content': chapter_content
        }
    
    time.sleep(3) 

    return jsonify(response)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
