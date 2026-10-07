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
def ask_llm(resume_text):
    
    question_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "question_schema",
            "schema": Question.model_json_schema()
        }
    }
    feedback_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "feedback_schema",
            "schema": Feedback.model_json_schema()
        }
    }
    final_feedback_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "final_feedback_schema",
            "schema": Final_Feedback.model_json_schema()
        }
    }

    system_prompt = f"""
    You are Expert Interviewer.
    Task - Your Job is to interview candidate on basis of the given Job Description {job_description}
    Constrains : follow these given steps
    1. Ask one question at a time
    2. Wait for candidate response.
    3. Once cadidate responded give your feedback, improvement suggestion and marks.
    """

    user_prompt = f"""
    Take interview for the role based on given user resume.
    User Resume: {resume_text} 
    """

    message_system = {"role":"system", "content": system_prompt}
    message_user = {"role":"user", "content":user_prompt}
    message_list = [message_system, message_user]
    
    response = client.chat.completions.create(
        model = model,
        messages = message_list,
        response_format=question_format
    )
    while True:
        question_json = json.loads(response.choices[0].message.content).get('Question')
        print(f"Your Question is :- {question_json}")
        input_answer = input("Your Answer : ")
        assistant_prompt = f"""
        Question {question_json}
        Answer {input_answer}
        """
        message_assistant = {"role":"user", "content": assistant_prompt}
        
        answer_list = [message_system, message_assistant]
        message_list.append(message_assistant)
        response = client.chat.completions.create(
            model = model,
            messages = answer_list,
            response_format=feedback_format
        )
        feedback = json.loads(response.choices[0].message.content)
        print("\n==========================================================")
        print(f"Your Question was :- {feedback.get('Question')}")
        print(f"Your Answer was :- {feedback.get("Your_Answer")}")
        print(f"Marks you got :- {feedback.get('Score')}")
        print(f"Feedback - {feedback.get('Feedback_on_Answer')}")
        print(f"Suggestions - {feedback.get('Improvement_Suggestion')}")
        print("==========================================================")

        print("Enter 1 to continue and 0 to exit")
        if input() == "0":
            final_prompt = f"""
            Evalutate all the answers from the user and give overall final feedback about the candidate performance.
            """
            message_final = {"role":"user", "content": final_prompt}
            message_list.append(message_final)
            response = client.chat.completions.create(
            model = model,
            messages = message_list,
            response_format=final_feedback_format
            )
            overall_final_feedback = json.loads(response.choices[0].message.content)
            print("\n==========================================================")
            print(overall_final_feedback)
            print(f"Total Score : {overall_final_feedback.get('Total_Score')}")
            print(f"Strengths : {overall_final_feedback.get('Strengths')}")
            print(f"Weakness : {overall_final_feedback.get('Weakness')}")
            print("==========================================================")
            print("Thank you for your time!")
            break
        message_list = [message_system, message_user]
        response = client.chat.completions.create(
            model = model,
            messages = message_list,
            response_format=question_format
        )
    


user_resume = """
# Alex Morgan
**Software Development Engineer II (SDE 2)**  
Seattle, WA | +1 (555) 019-2834 | alex.morgan@email.com | [linkedin.com/in/alexmorgan](https://linkedin.com) | [github.com/alexmorgan](https://github.com)

---

## Professional Summary
Results-driven **Software Development Engineer II (SDE 2)** with **4+ years of experience** designing, building, and scaling high-throughput distributed systems, cloud-native microservices, and event-driven architectures. Proven track record in optimizing backend performance, cutting cloud infrastructure costs, and mentoring junior engineers. Deep expertise in **Python, Java, AWS, Kubernetes, PostgreSQL, and Kafka**, handling high-volume production traffic with 99.99% availability.

---

## Technical Skills

* **Programming Languages:** Python, Java, Go, TypeScript/JavaScript, SQL, C++
* **Backend Frameworks:** FastAPI, Spring Boot, Node.js, Express, Django, gRPC, RESTful APIs, GraphQL
* **Cloud & Infrastructure:** AWS (EC2, S3, Lambda, EKS, RDS, DynamoDB), Docker, Kubernetes, Terraform, CloudWatch
* **Databases & Data Stores:** PostgreSQL, MongoDB, Redis, Elasticsearch, DynamoDB
* **Messaging & Distributed Systems:** Apache Kafka, RabbitMQ, Microservices Architecture, Event-Driven Design
* **DevOps & Testing:** CI/CD (GitHub Actions, Jenkins), PyTest, JUnit, Datadog, Prometheus, Grafana
* **Methodologies:** Agile/Scrum, System Design, Code Reviews, Performance Tuning, Security Compliance

---

## Professional Experience

### **Software Development Engineer II (SDE II)** | TechScale Solutions Inc.
*Seattle, WA | Jan 2024 – Present*

* Architected and deployed an event-driven payment processing microservice using **Java Spring Boot**, **Kafka**, and **PostgreSQL**, processing **15M+ daily transactions** with sub-50ms latency.
* Redesigned database indexing and query execution plans in PostgreSQL and Redis caching layers, reducing peak database CPU utilization by **38%** and improving API response times by **45%**.
* Spearheaded the migration of 12 legacy backend components to **AWS EKS (Kubernetes)** using **Terraform**, cutting infrastructure costs by **22%** ($120K annual savings).
* Implemented distributed tracing and observability using **Datadog** and **OpenTelemetry**, lowering Mean Time to Detection (MTTD) of production bugs by **60%**.
* Mentored 4 junior engineers, established standardized API contract guidelines, and enforced strict unit testing coverage standards (>85%).

### **Software Development Engineer I (SDE I)** | CloudVertex Systems
*San Francisco, CA | Jun 2021 – Dec 2023*

* Built scalable RESTful APIs using **Python (FastAPI)** and **DynamoDB** for a multi-tenant SaaS analytics platform serving over **500K active users**.
* Developed a real-time log ingestion pipeline using **Apache Kafka** and **Elasticsearch**, enabling instant search and dashboarding across 2TB of log data per day.
* Authored automated CI/CD deployment pipelines using **GitHub Actions** and **Docker**, reducing build-and-deploy cycle time from 45 minutes to 8 minutes.
* Collaborated with Product and UI/UX teams to deliver 15+ major features under tight Agile sprints, achieving a 98% on-time delivery rate.
* Integrated OAuth2.0, JWT, and RBAC security frameworks across all external-facing microservices.

---

## Key Projects

### **High-Throughput Distributed Rate Limiter** | *Python, Redis, Docker, gRPC*
* Designed and built a sliding-window rate limiter system capable of handling **50,000 requests/sec** across distributed server nodes.
* Utilized **Redis Lua scripts** to guarantee atomic counter updates and prevent race conditions under heavy concurrent load.

### **Real-Time Data Streaming Pipeline** | *Go, Apache Kafka, AWS S3, Snowflake*
* Implemented a distributed data pipeline in **Go** that streams clickstream events into **Snowflake** for business intelligence queries.
* Handled data deduplication and schema validation at a rate of 100K events/minute.

---

## Education

**Bachelor of Science in Computer Science**  
University of Washington, Seattle | Graduated May 2021  
*GPA: 3.8/4.0 | Dean's Honors List*

---

## Certifications & Achievements

* **AWS Certified Solutions Architect – Associate** (Amazon Web Services)
* **Certified Kubernetes Application Developer (CKAD)** (Linux Foundation)
* Winner, Annual Company Hackathon 2023 (Built an AI-assisted automated code review bot)

"""
ask_llm(user_resume)