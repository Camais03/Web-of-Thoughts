import os
import sys
import json
import logging
from flask import Flask, render_template, request, jsonify
from functions import chat_with_gpt3, generate_initial_thoughts, generate_links, critique_thoughts, unify_solutions, continue_thoughts, continuing_thoughts
import asyncio
import openai

# Get the directory where the executable is located
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)

# Read the OpenAI API key from the config.json file
config_file_path = os.path.join(application_path, 'config.json')
with open(config_file_path) as config_file:
    config = json.load(config_file)
    api_key = config.get('OPENAI_API_KEY', '')

# Set the OpenAI API key
openai.api_key = api_key

# Explicitly specify the template folder path
template_folder = os.path.join(application_path, 'templates')
app = Flask(__name__, template_folder=template_folder)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate_and_link', methods=['POST'])
def generate_and_link():
    data = request.get_json()
    task = data['task']
    task_type = data['taskType']
    continue_count = int(data['continueCount']) 
    model = data['model']

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    thoughts = loop.run_until_complete(generate_initial_thoughts(task, task_type, model))
    
    linked_thoughts = []  # Initialize this somewhere appropriate in your code
    new_links = loop.run_until_complete(generate_links(thoughts, linked_thoughts, task_type, model))
    linked_thoughts += new_links
    
    critiques = loop.run_until_complete(critique_thoughts(thoughts, task_type, task, model))
    
    for i in range(continue_count):  # loop 5 times max
        # Get the thoughts to continue
        continued_thoughts_ids = loop.run_until_complete(continue_thoughts(thoughts, linked_thoughts, task_type, task, model))

        # If there are no thoughts to continue, break the loop
        if not continued_thoughts_ids:
            break

        # Continue the thoughts
        continued_thoughts = loop.run_until_complete(continuing_thoughts(continued_thoughts_ids, thoughts, linked_thoughts, task_type, task, model))
        
        # Link and critique the continued thoughts
        for continued_thought in continued_thoughts_ids:
            new_links = loop.run_until_complete(generate_links(thoughts, linked_thoughts, task_type, model, continued_thought))
            linked_thoughts += new_links

        critiques_continued = loop.run_until_complete(critique_thoughts(continued_thoughts, task_type, task, model))
        
        # Merge the continued thoughts and their links/critiques
        thoughts += continued_thoughts
    
    # print(f"continued_thoughts_ids: {continued_thoughts_ids}")

    response = {
        "thoughts": thoughts,
        "linked_thoughts": linked_thoughts,
        "critiques": critiques
    }


    unified_solution = loop.run_until_complete(unify_solutions(thoughts, critiques, linked_thoughts, task_type, task, model))
    response["unified_solution"] = unified_solution
    print(f"Unified solution: {unified_solution}")
    

    return json.dumps(response)

if __name__ == '__main__':
    app.run(debug=True)