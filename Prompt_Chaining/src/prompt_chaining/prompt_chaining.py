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
  

JD = """
We are hiring a backend developer:
Requirements:
- Python Programming,
- Problem-solving,
- Data structures and algorithms,
- Django framework,
- Good understanding of RESTful APIs,
"""

RESUME = """
Name: Alex Morgan
Title: Senior Sales Manager
Experience: 7+ Years
Skills:
- B2B Sales Strategy
- Key Account Management
- Sales Pipeline & Revenue Forecasting
- Team Leadership & Performance Coaching
- Contract Negotiation & Deal Closing
- CRM Software (Salesforce, HubSpot)
- Lead Generation & Business Development
- Customer Relationship Management
"""

def ask_llm(system_prompt, user_prompt):
    sys_msg = {
        "role": "system",
        "content": system_prompt
    }
    user_msg = {
        "role": "user",
        "content": user_prompt
    }

    messages = [sys_msg, user_msg]

    response = client.chat.completions.create(model=model, messages=messages)
    answer = response.choices[0].message.content

    return answer

def step1_RESUME_extraction():
    system_prompt = """ 
    You are Professional Assistant, Extract skills from the resume and return only list , do not invent any information. 
    """
    user_prompt = f"""
    Extract Skills from this resume {RESUME}
    """
    return ask_llm(system_prompt, user_prompt)

def step2_JD_extraction():
    system_prompt = """ 
    You are Professional Assistant, Extract skills from the JD and return only list , do not invent any information. 
    """
    user_prompt = f"""
    Extract Skills from this JD {JD}
    """
    return ask_llm(system_prompt, user_prompt)

def step3_match(candidate, jd):
    system_prompt = """ 
    You are Professional Assistant,Comapre the skills of candidate and skills required in JD and produce a final score from 1 to 100 , also give short final verdict on then candidate"""
    user_prompt = f"""
    Comapre and match Skills from this 
    JD {JD} 
    with 
    Candidate Skills {candidate}
    """
    return ask_llm(system_prompt, user_prompt)


candidate = step1_RESUME_extraction()   
jd = step2_JD_extraction()
print(step3_match(candidate, jd))