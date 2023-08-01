# Web-of-Thoughts v0.1

![](https://github.com/Camais03/Web-of-Thoughts/blob/main/readme/Main%20Page.PNG)

## Overview:
Web of thoughts is a web app that using the OpenAI API to generate mindmaps based on a given prompt. These mindmaps will first generate initial thoughts, link those thoughts, critique those thoughts and finally try to resolve these thoughts into a final answer.

It can be a bit buggy so apologies if any errors occur.

![](https://github.com/Camais03/Web-of-Thoughts/blob/main/readme/Unified%20Solution.PNG)

## Setting up:
To set up simply open the config and paste in your OpenAI API key. Then just run app.exe and type localhost:5000 to access in your browser (or copy the server address).

If you have all the dependencies installed then you can also run Web of Thoughts.bat

## How to use:
To generate a mindmap click the start button and you will be prompted to enter a prompt. 

### Types:
You have the options to get GPT to look for solutions, generate ideas, or think on it's own. The "Thoughts" selection will get GPT to generate thoughts based on no input from the user so inputting a task will not impact it's reply at all.

![](https://github.com/Camais03/Web-of-Thoughts/blob/main/readme/type.gif)

### Continues:
You can also choose how many thoughts you want GPT to continue. For example, setting this to 1 will ask GPT if there are any thoughts it wants to continue (either to solve a problem or to explore a thought more). If it doesn't deem it necessary or doesn't want to continue any thoughts it won't.

Continuing a thought can get expensive as we run through the process of linking and critiquing thoughts again. Be careful setting this to high values.

![](https://github.com/Camais03/Web-of-Thoughts/blob/main/readme/continues.gif)

### Model:
You can select the model based on the models you have access to.

![](https://github.com/Camais03/Web-of-Thoughts/blob/main/readme/model.gif)

## Examples:
There are some examples inside the examples folder. I tested the 1st 10 questions of formal logic from the MMLU test dataset avaliable here: https://huggingface.co/datasets/cais/mmlu/viewer/formal_logic/test

I didn't observe much of an improvement from GPT 3.5 but did find that it got question 2 right when ChatGPT never did. However, it would get questions wrong that ChatGPT never did as well.

It could be considered an improvement given that when testing ChatGPT it averaged 4/10 and my Web of Thoughts got 7/10 but this isn't an average and is just what it got combining the results of the 3 continue test and the 5 continue test. I need to do more tests so nothing here is conclusive at all. COT is included in my prompt which I haven't tested with ChatGPT so the improved performance could be due to that.

I would've like to have tested GPT 4 but I was charged 99 cents so 1 cent off what was required to be given access. If anyone does want to test it out with GPT 4 please let me know your results :)

You can find the questions I used in /Formal-Logic-Questions. They are formatted so you can just copy and paste them.

![](https://github.com/Camais03/Web-of-Thoughts/blob/main/readme/overview.gif)

## Control:
When loaded the you can drag any of the mindmap nodes around and click on a thought to get a sidebar with more information (linked thoughts, continued thoughts, etc.).

![](https://github.com/Camais03/Web-of-Thoughts/blob/main/readme/dragging.gif)

![](https://github.com/Camais03/Web-of-Thoughts/blob/main/readme/sidebar.gif)

You can move the mindmap around and scale it up and down by using the scroll wheel or zoom in/out buttons. Double clicking also zooms in. (Currently if a mindmap exceeds the width of the webpage you can scroll left, still trying to fix).

You can save and load mindmaps in a JSON format.

## Issues:
Currently there are some bugs. 

- Loading a Mindmap when another is already loaded will load the mindmap below. I recommend refreshing the page before loading a new mindmap.
- Sometimes, GPT may continue the same thought causing an overlap. You can just move these out the way.
- Currently can't scroll left when the mindmap that is bigger than the browser window loads. You can still drag the mindmap the the right.
- Occasionally the controls get's pushed off screen. You can zoom out (ctrl - ) and it should come back in view.
- Occasionally the mindmap doesn't generate correctly. Needs fixing, unified solution should still work though.

## Future Features:
Depending on the popularity of the project I have these features planned:

- Big Refractor of code. (I used GPT-4 to help me with most of this but am aware that the code is quite messy currently).
- Ability to choose to continue any thoughts and add own input to GPT.
- Get GPT to organise thoughts into concepts or ideas for even larger mindmaps.
- Ability to use other models.
- Ability to use plugins like Wolfram Alpha to further improve perfromance.
- Better UI, bug fixes, and better usability.
