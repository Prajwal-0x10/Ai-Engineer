import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from time import sleep
import re

load_dotenv()
my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    print("Please provide the GROQ_API_KEY in the .env file.")
    exit(1)

client = Groq(api_key=my_api_key)
model ="openai/gpt-oss-120b"

## Tool
def get_product_price(product: str):
    if product == "shoes":
        return 100
    elif product == "Watch":
        return 200
    elif product == "T-shirt":
        return 300
    else:
        return 400

def calculator(expression):
    try:
        return eval(expression)
    except:
        return "Calculation Error"

tools = {
    "get_product_price" : get_product_price,
    "calculator" : calculator
}


system_prompt = """
You are a shopping assistant.

You have these tools
get_product_price(product)
calculator(expression)

#IMPORTANT
Call tools exactly like these examples:
Action: get_product_price("shoes")
Action:calculator("1000-100")

Never  Write:
get_product_price(product="shoes")

follow these rules:
1) Decide what you to do next.
2) Call only one tool at a time.
3) After writing a action stop immediately
4) Never guess or invent tool result
5) Wait until you receive an observation
6) Then decide next action
7) when the task is completed give final answer

format :
Thought: What you need to do
Action: Tool_Name(argument)

when finished:
Final Answer: Your Answer

"""

def run_agent(question):

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": question
        }
    ]

    for step in range(5):
        print(messages)
        print("\n------------------")
        print("STEP", step + 1)
        print("------------------")

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0
        )

        answer = response.choices[0].message.content

        print(answer)

        # Agent has finished
        if "Final Answer:" in answer:
            break


        # Find the Action
        match = re.search(
            r"Action:\s*(\w+)\((.*?)\)",
            answer
        )


        if match:

            tool_name = match.group(1)

            tool_input = match.group(2)

            tool_input = tool_input.strip()

            tool_input = tool_input.strip('"')


            # Run the tool
            if tool_name in tools:

                tool = tools[tool_name]

                observation = tool(tool_input)

            else:

                observation = "Tool not found"


            print(
                "Observation:",
                observation
            )


            # Add LLM response to memory
            messages.append({
                "role": "assistant",
                "content": answer
            })


            # Give tool result back to LLM
            messages.append({
                "role": "user",
                "content":
                    "Observation: "
                    + str(observation)
            })
            sleep(5)

prompt =""" i have 1000 what is price of shoes and how much i will left with after buying 2 shoes"""
run_agent(prompt)