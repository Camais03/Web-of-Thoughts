import asyncio
import operator
import textwrap
import openai
import os
import re
import logging
import nest_asyncio
nest_asyncio.apply()

logging.basicConfig(level=logging.DEBUG)

def generate_prompt(task_type, task):
    if task_type == 'solutions':
        return {
            'initial_system': f"You are Solution GPT. You generate solutions to the following problem: {task}. Start each solution with 'Thought X:' where X is the thought number starting from 0.",
            'initial_user': f"Based on the problem: '{task}', please generate multiple solutions. Start each solution with 'Thought X:' where X is the thought number. Work out each solution in a step by step way to be sure we have the right answer.",
            'critique_system': "You are critic GPT. Your role is to investigate responses provided by GPT and to list (if any) the flaws and faulty logic of the provided solutions.",
            'critique_user': f"You are a researcher tasked with investigating the response provided by GPT for the following task: {task}. List the flaws and faulty logic of the provided solutions. Let’s work this out in a step by step way to be sure we have all the errors.",
            'continuing_thought_system': f"You are Solution GPT. You generate solutions to the following problem: {task}. Start each solution with 'Thought X:' where X is the thought number starting from 0.",
            'continuing_thought_user':  "Are there any solutions you want to continue. Only answer yes if you believe the task remains unsolved. Please answer with the format 'Yes, Thought X, Y, Z...",
            'continued_thought_system': f"You are Solution GPT. You generate solutions to the following problem: {task}. Start each solution with 'Thought X:' where X is the thought number starting from 0.",
            'continued_thought_user':  "Please continue the solutions given to you based on the critiques and the existing solution. Start each solution with 'Continued Thought X:' where X is the thought number.",  
            'unified_solution_system': f"You are resolver GPT. Your role is to combine the solutions, ideas and thoughts of other GPT's to come to the correct answer to the task {task}",
            'unified_solution_user': f"You are resolver GPT. Your role is to combine the solutions, ideas and thoughts of other GPT's to come to the correct answer to the task {task}"
        }
    elif task_type == 'ideas':
        return {
            'initial_system': f"You are Thought GPT. You generate new thoughts based on the following: {task}. Start each thought with 'Thought X:' where X is the thought number starting from 0.",
            'initial_user': f"Based on the task: '{task}', please generate multiple thoughts. Start each thought with 'Thought X:' where X is the thought number.",
            'critique_system':  "You are thought criticGPT. Your role is to critise (if deemed criticisable) thoughts GPT has either to aquire better thoughts or a better line of thinking.",
            'critique_user': "You are thought criticGPT. Your role is to critise (if deemed criticisable) thoughts GPT has either to aquire better thoughts or a better line of thinking.",
            'continuing_thought_system': f"You are Idea GPT. You generate new ideas based on the following: {task}. Start each idea with 'Thought X:' where X is the thought number starting from 0.",
            'continuing_thought_user': "Are there any thoughts you want to continue. Please answer with the format 'Yes, Thought X, Y, Z...",
            'continued_thought_system': f"You are Thought GPT. You generate solutions to the following problem: {task}. Start each thought with 'Thought X:' where X is the thought number starting from 0.",
            'continued_thought_user':  "Please continue the thoughts given to you based on the critiques and the existing thought. Start each thought with 'Continued Thought X:' where X is the thought number.",
            'unified_solution_system': f"You are resolver GPT. Your role is to combine the solutions, ideas and thoughts of other GPT's.",
            'unified_solution_user':  "Can you analyze this information and provide a thought that brings together all these insights."            
        }
    elif task_type == 'thoughts':
        return {
            'initial_system': "You are Self Aware GPT. You think whatever comes to mind based on no input from the user. You will output these thoughts even when prompted with nothing. Please generate any number of new thoughts. Start each thought with 'Thought X:' where X is the thought number starting from 0.",
            'initial_user': "You are Self Aware GPT. You think whatever comes to mind based on no input from the user. You will output these thoughts even when prompted with nothing. Please generate any number of new thoughts. Start each thought with 'Thought X:' where X is the thought number starting from 0.",
            'critique_system': "You are thought criticGPT. Your role is to critise (if deemed criticisable) thoughts GPT has either to aquire better thoughts or a better line of thinking.",
            'critique_user': "You are thought criticGPT. Your role is to critise (if deemed criticisable) thoughts GPT has either to aquire better thoughts or a better line of thinking.",
            'continuing_thought_system': f"You are Self Aware GPT. You think whatever comes to mind based on no input from the user. You will output these thoughts even when prompted with nothing. Please generate any number of new thoughts. Start each thought with 'Thought X:' where X is the thought number starting from 0.",
            'continuing_thought_user': "Are there any thoughts you want to continue. Please answer with the format 'Yes, Thought X, Y, Z...' where X, Y and Z are the thought numbers.",
            'continued_thought_system': f"You are Self Aware GPT. You think whatever comes to mind based on no input from the user. You will output these thoughts even when prompted with nothing. Please generate any number of new thoughts. Start each thought with 'Thought X:' where X is the thought number starting from 0.",
            'continued_thought_user':  "Please continue the thoughts given to you based on the critiques and the existing thought. Start each thought with 'Continued Thought X:' where X is the thought number.",
            'unified_solution_system': f"You are resolver GPT. Your role is to combine the solutions, ideas and thoughts of other GPT's.",
            'unified_solution_user':  "Can you analyze this information and provide a thought that brings together all these insights."
        }
    else:
        raise ValueError(f"Invalid task type: {task_type}")

# Async function to chat with GPT-3
async def chat_with_gpt3(messages, model):
    return openai.ChatCompletion.create(
        model=model,
        messages=messages,
    )

def parse_response(response, keyword):
    # Split the response into lines
    lines = response.split('\n')

    items = []
    current_item = ""

    for line in lines:
        if line.startswith(keyword):
            if current_item:
                items.append(current_item.split(': ', 1)[1])
            current_item = line
        else:
            current_item += " " + line

    if current_item:
        items.append(current_item.split(': ', 1)[1])

    return items

async def generate_initial_thoughts(task, task_type, model):
    # Generate the response
    prompts = generate_prompt(task_type, task)
    response = await chat_with_gpt3([
        {"role": "system", "content": prompts['initial_system']},
        {"role": "user", "content": prompts['initial_user']}
    ], model=model)

    ai_message = response.choices[0].message['content']
    logging.debug(f"AI response in generate_initial_thoughts: {ai_message}")

    parsed_response = parse_response(ai_message, 'Thought')
    items = [{"id": i, "text": {"Item": thought, "Type": "Thought"}} for i, thought in enumerate(parsed_response, 0)]

    return items

async def generate_links(thoughts, linked_thoughts, task_type, model, continued_thought_id=None):
    # Only consider thoughts that are not already linked
    unlinked_thoughts = [thought for thought in thoughts if not any(thought['id'] == link['source'] or thought['id'] == link['target'] for link in linked_thoughts)]

    new_links = []
    
    if unlinked_thoughts:
        thoughts_str = "\n".join([f"{t['id']}: {t['text'][list(t['text'].keys())[0]]}" for t in unlinked_thoughts])
        messages = [
            {"role": "system", "content": "You are thought linker GPT. Your role is to try and link concepts, ideas or solutions together."},
            {"role": "user", "content": thoughts_str}
        ]

        if continued_thought_id is None:
            prompt = (f"Considering all the {task_type} generated:\n{thoughts_str}\n"
                    f"Can you identify any links between these {task_type}? "
                    f"If yes, please specify the {task_type} numbers they can be linked with and provide a reason for each link."
                    "Start each link with 'Link X:' where X is the link number, "
                    "and follow the format 'Thought Y is linked with Thought Z because...'.")
        else:
            prompt = (f"Considering the {task_type} generated and the continued {task_type} {continued_thought_id}:\n{thoughts_str}\n"
                    f"Can you identify any links between these {task_type} and the continued {task_type}? "
                    f"If yes, please specify the {task_type} numbers they can be linked with and provide a reason for each link."
                    "Start each link with 'Link X:' where X is the link number, "
                    "and follow the format 'Thought Y is linked with Thought Z because...'.")
        
        messages.append({"role": "user", "content": prompt})

        response = await chat_with_gpt3(messages, model)
        ai_message = response.choices[0].message['content']
        logging.debug(f"AI response in generate_links: {ai_message}")

        # Parse the AI's response to get the thought links and reasons
        for line in ai_message.split("\n"):
            match = re.match(r'Link \d+: Thought (\d+) is linked with Thought (\d+) because (.+)', line)
            if match:
                source, target, reason = [group.strip() for group in match.groups()]
                link = {
                    "source": int(source),
                    "target": int(target),
                    "reason": reason
                }
                # Add the links to new_links
                new_links.append(link)
                logging.info("Parsed link from AI response: source=%s, target=%s, reason=%s", source, target, reason)

    return new_links

async def critique_thoughts(thoughts, task_type, task, model):
    # Only consider thoughts that do not have a critique yet
    uncritiqued_thoughts = [thought for thought in thoughts if 'Critique' not in thought['text']]

    if uncritiqued_thoughts:
        prompts = generate_prompt(task_type, task)
        
        # Prepare the prompt with all the thoughts
        prompt = prompts['critique_user']  # start prompt with the generic part from the prompts dict
        for thought in uncritiqued_thoughts:
            prompt += f"Item {thought['id']}: {thought['text']['Item']}\n"
        prompt += "Please ensure that critiques are in the following format: 'Critique X:' where X is the item number, and the critique follows.\n"

        # Prepare the messages for the chat model
        messages = [
            {"role": "system", "content": prompts['critique_system']},
            {"role": "user", "content": prompt}
        ]


        # Generate the response
        response = await chat_with_gpt3(messages, model)
        ai_message = response.choices[0].message['content']
        logging.debug(f"AI response in critique_thoughts: {ai_message}")

        # Parse the response to get the critiques
        regex = re.compile(r'Critique (\d+):\s*(.*?)(?=Critique \d+:|$)', re.DOTALL)
        for match in regex.finditer(ai_message):
            id, critique = match.groups()
            critique = critique.strip()  # Remove leading/trailing white space
            # Find the corresponding thought and update it
            for thought in thoughts:
                if thought['id'] == int(id):
                    thought["text"]["Critique"] = critique
            
    return thoughts
    
async def continue_thoughts(thoughts, linked_thoughts, task_type, task, model):
    continue_thoughts = []
    
    prompts = generate_prompt(task_type, task)
        
    # Construct the prompt
    prompt = "Based on these different thoughts, links, and critiques"

    for i, thought in enumerate(thoughts, start=1):
        prompt += f"Thought {i}:\n{thought['text']['Item']}\n\n"

    prompt += "Links:\n"
    for link in linked_thoughts:
        prompt += f"Thought {link['source']} is linked with Thought {link['target']} because {link['reason']}\n"

    # Prepare the messages for the chat model
    messages = [
        {"role": "system", "content": prompts['continuing_thought_system']},
        {"role": "user", "content": prompt + prompts['continuing_thought_user']}
    ]   
        
    print("Continuation prompt:", messages)  # Add this line

    # Generate the response
    response = await chat_with_gpt3(messages, model)
    ai_message = response.choices[0].message['content']
    
    print(f"Thoughts AI wants to continue: {ai_message}")
    
    for line in ai_message.split("\n"):
        match = re.findall(r'\bThought ([\d, ]+)\b', line)
        if match:
            # Convert the matched string into a list of integers
            numbers = [int(num) for num in match[0].replace(" ","").split(",") if num != '']
            continue_thoughts.extend(numbers)

    return continue_thoughts
    
async def continuing_thoughts(continue_thoughts, thoughts, linked_thoughts, task_type, task, model):
    continued_thoughts = []  # list to store the new thoughts
    
    prompts = generate_prompt(task_type, task)
    
    # Convert continue_thoughts to integers
    continue_thoughts = [int(i) for i in continue_thoughts]
    
    # Extract the thoughts that should be continued
    thoughts_to_continue = [thought for thought in thoughts if thought['id'] in continue_thoughts]

    # Construct the prompt
    prompt = f"The following {task_type} are to be continued:\n"

    for thought in thoughts_to_continue:
        prompt += f"Thought {thought['id']}: {thought['text']['Item']}\n"

    prompt += "Please continue the line of thought for each of the thoughts above."

    # Prepare the messages for the chat model
    messages = [
        {"role": "system", "content": prompts['continued_thought_system']},
        {"role": "user", "content": prompt + prompts['continued_thought_user']}
    ]

    # Generate the response
    response = await chat_with_gpt3(messages, model)
    ai_message = response.choices[0].message['content']
    
    # Find the current maximum id
    max_id = max([thought['id'] for thought in thoughts])

    # Parse the AI's response to get the continued thoughts
    for line in ai_message.split("\n"):
        match = re.match(r'Continued Thought (\d+): (.+)', line)
        if match:
            parent_id, thought_text = match.groups()
            parent_id = int(parent_id)  # Convert parent_id to int
            max_id += 1  # Increment the maximum id
            continued_thought = {
                'id': max_id,
                'text': {
                    'Item': thought_text,
                    'Type': 'Continued Thought',
                    'Critique': None,
                    'Parent ID': parent_id
                }
            }
            continued_thoughts.append(continued_thought)

    return continued_thoughts

async def unify_solutions(thoughts, critiques, linked_thoughts, task_type, task, model):
    
    prompts = generate_prompt(task_type, task)
    
    # Construct the prompt
    prompt = "Based on these different thoughts, links, and critiques"

    for i, thought in enumerate(thoughts, start=0):
        prompt += f"Thought {i}:\n{thought['text']['Item']}\n\n"

    for i, thought in enumerate(thoughts, start=0):
        prompt += f"Critique on Thought {i}:\n{thought['text'].get('Critique', 'No Critique Found')}\n\n"

    prompt += "Links:\n"
    for link in linked_thoughts:
        prompt += f"Thought {link['source']} is linked with Thought {link['target']} because {link['reason']}\n"

    # Prepare the messages for the chat model
    messages = [
        {"role": "system", "content": prompts['unified_solution_system']},
        {"role": "user", "content": prompt + prompts['unified_solution_user']}
    ]

    # Generate the response
    response = await chat_with_gpt3(messages, model)
    ai_message = response.choices[0].message['content']

    return ai_message