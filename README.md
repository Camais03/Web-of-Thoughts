


# Web-of-Thoughts

## Overview:
Web of thoughts is a web app that using the OpenAI API to generate mindmaps based on a given prompt. These mindmaps will first generate initial thoughts, link those thoughts, critique those thoughts and finally try to resolve these thoughts into a final answer.

## Setting up:
To set up simply open the config and paste in your OpenAI API key. Then just run app.exe and a localhost:5000 will open up in your browser.

## How to use:
To generate a mindmap click the start button and you will be prompted to enter a prompt. 

### Types:
You have the options to get GPT to look for solutions, generate ideas, or think on it's own. The "Thoughts" selection will get GPT to generate thoughts based on no input from the user so inputting a task will not impact it's reply at all.

### Continues:
You can also choose how many thoughts you want GPT to continue. For example, setting this to 1 will ask GPT if there are any thoughts it wants to continue (either to solve a problem or to explore a thought more). If it doesn't deem it necessary or doesn't want to continue any thoughts it won't.

Continuing a thought can get expensive as we run through the process of linking and critiquing thoughts again.

### Model Type:
You can select the model type based on the models you have access to.

### Features:
When loaded the you can drag any of the mindmap nodes around and click on a thought to get a sidebar with more information (linked thoughts, continued thoughts, etc.).

You can save and load mindmaps in a JSON format.
