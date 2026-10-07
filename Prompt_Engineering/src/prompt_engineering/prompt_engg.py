from pydantic.json_schema import Examples
import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    print("Please provide the GROQ_API_KEY in the .env file.")
    exit(1)

client = Groq(api_key=my_api_key)
model = "openai/gpt-oss-120b"


def llm_call(prompt):
    messages =[{
    "role":"user",
    "content":prompt
    }]

    response = client.chat.completions.create(
    model=model,
    messages=messages
    )
    return response.choices[0].message.content


bad_prompt = "This is user complaint Mobile is not working Clasify This"
good_prompt = """ Role :You are a helpful assistant that classifies user complaints. 
Task : Clasify issue in category
Constraint : Clasify only 5 categories billing, technical, return , refund , delivery
User Complaint : i m not happy with my office work. 
Output Format : Give me one word output only and that should be category of the issue
Example : if user complaint says refund is not initiated yet then refund 
Fallback: if issue is unrelated to any category from contrains give output as Others"""

print(llm_call(good_prompt))