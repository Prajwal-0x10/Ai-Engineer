from pydantic import AnyWebsocketUrl
import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel


class Ticket(BaseModel):
    name :str
    location : str
    email: str
    issue: str


load_dotenv()
my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    print("Please provide the GROQ_API_KEY in the .env file.")
    exit(1)

client = Groq(api_key=my_api_key)
model = "openai/gpt-oss-120b"
role = "user"
sample_text = "Hi, how are you? My Name is Prajwalfrom Mumbai"
prompt = f'''
This is Customer Ticket {sample_text},
Please extract personal information from this.
'''

schema = Ticket.model_json_schema()
response_format = {"type":"json_object"}
system_prompt=f"""
Extract personal information and response should be strictly based on given json schema
{schema}
"""
message_system = {
    "role": "system",
    "content": system_prompt
}
messages = {
    "role":role,
    "content":prompt
}
 
messages = [message_system, messages]
response = client.chat.completions.create(
    model=model,
    messages=messages,
    response_format = response_format
)
answer = response.choices[0].message.content


import json
raw_json = answer
data_file = json.loads(raw_json)
ticket = Ticket(**data_file)
print(ticket.name)
print(ticket.email)
print(ticket.location)