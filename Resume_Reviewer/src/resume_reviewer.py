import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel
from read_resume_from_pdf import read_resume_text
from glob import glob

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

resume_list = glob("D:/Ai-Engineer/Resume_Reviewer/src/resumes/*")


class Experience(BaseModel):
    company : str | None
    role : str | None
    duration : str | None
    responsibilities : str | None

class Resume(BaseModel):
    summary :str | None
    skills : list[str] | None
    projects: list[str] | None
    experience: list[Experience] | None
    education: list[str]
    match : str

class JobD(BaseModel):
    role : str
    required_skills : list[str]
    preferred_skills : list[str]
    minimum_experience : float | None
    education_requirements : list[str]
    responsibilities : list[str]

class MatchResume(BaseModel):
    score : float
    details: dict
    final_verdict: str

load_dotenv()
my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    print("Please provide the GROQ_API_KEY in the .env file.")
    exit(1)

client = Groq(api_key=my_api_key)
model = "openai/gpt-oss-120b"
role = "user"

job_description = '''
Description
Are you passionate about enabling millions of customers around to world buy anything, anywhere, anytime? Can you work on large cross-team projects? Do you want to take the best e-commerce platform in the world to the next level?

We, the Multi company ordering platform(MCOP) team, need a strong Software Development Engineer to enable our multi-year large initiatives. You will design, architect and innovative technology solutions that will reduce time to market, standardize execution and scale for expansion globally. You will build, operate and play a key role in the evolution of our platform to solve the world's most complex technical challenges in Information extraction, Large-scale computing, Distributed systems, Web applications, Data mining, Scalability, Security, and Algorithms to name a few. You’ll strive for simplicity, and demonstrate significant creativity and high judgment.


The job is simple: make everything available to everyone all the time at the best possible price. The requirements are almost as simple - we’re looking for leaders and trailblazers who aren’t afraid of tackling massive scale, layered complexity and ambiguous requirements to empower our customers to shop the World. No two features are ever the same and our customers are hungry for every single one!

What to expect day-to-day:
· Facilitate the design of the architecture of these distributed and highly scalable systems.
· Solve complex problems through data, rapidly.
· Design and develop state of the art software systems that address these complex and ambiguous problems.
· Own the inputs and the business outcome through cultivating a culture of relentless auditing and metric monitoring, automatically where possible

Key job responsibilities
Basic qualifications

3+ years of non-internship professional software development experience
2+ years of non-internship design or architecture (design patterns, reliability and scaling) of new and existing systems experience
Experience programming with at least one software programming language

Preferred qualifications

3+ years of full software development life cycle, including coding standards, code reviews, source control management, build processes, testing, and operations experience
Bachelor's degree in computer science or equivalent

Our inclusive culture empowers Amazonians to deliver the best results for our customers. If you have a disability and need a workplace accommodation or adjustment during the application and hiring process, including support for the interview or onboarding process, please visit https://amazon.jobs/content/en/how-we-hire/accommodations for more information. If the country/region you’re applying in isn’t listed, please contact your Recruiting Partner.

Basic Qualifications
- 3+ years of non-internship professional software development experience
- 2+ years of non-internship design or architecture (design patterns, reliability and scaling) of new and existing systems experience
- Experience programming with at least one software programming language
- 3+ years of contributing to new and current systems architecture and design (architecture, design patterns, reliability and scaling) experience

Preferred Qualifications
- 3+ years of full software development life cycle, including coding standards, code reviews, source control management, build processes, testing, and operations experience
- Bachelor's degree in computer science or equivalent

Our inclusive culture empowers Amazonians to deliver the best results for our customers. If you have a disability and need a workplace accommodation or adjustment during the application and hiring process, including support for the interview or onboarding process, please visit https://amazon.jobs/content/en/how-we-hire/accommodations for more information. If the country/region you’re applying in isn’t listed, please contact your Recruiting Partner.
'''

def resume_parser(resume_text: str) -> dict:
    schema = Resume.model_json_schema()
    response_format = {"type":"json_object"}
    system_prompt=f"""
    Act as a expert resume parser
    Return json matching {schema} after extracting necessary information from the job description

    Do not invent information.
    """

    user_prompt = f'''   
    Analyse the following resume:
    {resume_text}
    '''
    message_system = {
        "role": "system",
        "content": system_prompt
    }
    messages = {
        "role":"user",
        "content":user_prompt
    }
    
    messages = [message_system, messages]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format = response_format
    )
    resume_json = response.choices[0].message.content
    return resume_json   

def final_score(job_description: str, resume: dict) -> dict:
    schema = MatchResume.model_json_schema()
    response_format = {"type":"json_object"}
    system_prompt=f"""
    Act as a expert resume scorer
    Return json matching {schema} after calculating the match score between the job description and the resume
    

    Do not invent information.
    And Give me :
    1)Name
    2)Matching Skills
    3)Missing Important Skills
    4)Match Percentage
    5)Short Final Verdict
    """

    user_prompt = f'''   
    Analyse the following Job Description:
    {job_description}
    
    And the following Resume:
    {resume}
    '''
    message_system = {
        "role": "system",
        "content": system_prompt
    }
    messages = {
        "role":"user",
        "content":user_prompt
    }
    
    messages = [message_system, messages]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format = response_format
    )
    score_json = response.choices[0].message.content
    return score_json   
import time
results = []
for file_path in resume_list:
    if file_path.endswith(".pdf") or file_path.endswith(".docx"):
        resume_text = read_resume_text(file_path)
        resume_json = resume_parser(resume_text)
        time.sleep(5)
        score = final_score(job_description, resume_json)
        time.sleep(5)
        results.append(score)
print(results)
#results.sort(key=lambda x: x["score"], reverse=True)
# print(results[0])
