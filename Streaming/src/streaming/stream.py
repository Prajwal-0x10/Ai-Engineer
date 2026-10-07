from sys import platform
import sys
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel
from glob import glob 

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

class Feedback(BaseModel):
    Question : str | None
    Your_Answer : str | None
    Score : int
    Feedback_on_Answer : str | None
    Improvement_Suggestion : str | None

class Question(BaseModel):
    Question : str | None

class Final_Feedback(BaseModel):
    Total_Score : int 
    Strengths : str
    Weakness : str

load_dotenv()
MY_API_KEY = os.getenv("GROQ_API_KEY")

if not MY_API_KEY:
    print("Please provide the GROQ_API_KEY in the .env file.")
    exit(1)

client = Groq(api_key=MY_API_KEY)
model = "openai/gpt-oss-120b"
prompt = "Explain how machine works"
message = {
    "role" : "user",
    "content" : prompt
}
messages = [message]
stream = client.chat.completions.create(
    model = model,
    messages = messages,
    stream = True,
)
for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="", flush=True)
    else:
        print("\n")
    