import os
import uvicorn
import json
import random
import re
import time
import base64
import asyncio
import io
import torch
import cv2
import numpy as np
import pandas as pd
import plotly.express as px
import string
import glob
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from fastapi import FastAPI, HTTPException, Request, Form, UploadFile, File, Response, Query, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse, FileResponse  
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from email.mime.text import MIMEText
import plotly
import smtplib
from PIL import Image
import torchvision
import torchvision.transforms as transforms
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from sklearn.feature_extraction.text import TfidfVectorizer 
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer, util
from datetime import datetime as dt
import hashlib
import ollama

# Helper Function: Email Sending
def send_email(to_address, subject, message):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "125150054@sastra.ac.in"
    sender_password = "ksdd eqpj rtqv ytfz"  # Use environment variables in production!
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_address
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, [to_address], msg.as_string())
        server.quit()
        print(f"Email successfully sent to {to_address}")
    except Exception as e:
        print(f"Failed to send email to {to_address}: {e}")

# Helper Function: Generate Timetable
def generate_timetable(candidate_emails: List[str], from_time: str, to_time: str, interview_date: str) -> tuple[str, List[dict]]:
    try:
        start_datetime = datetime.strptime(f"{interview_date} {from_time}", "%Y-%m-%d %H:%M")
        end_datetime = datetime.strptime(f"{interview_date} {to_time}", "%Y-%m-%d %H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date or time format")
    
    total_duration = (end_datetime - start_datetime).total_seconds() / 60
    if total_duration <= 0:
        raise HTTPException(status_code=400, detail="To time must be after from time")
    
    num_candidates = len(candidate_emails)
    slot_duration = total_duration // num_candidates
    
    timetable = []
    current_time = start_datetime
    for i, email in enumerate(candidate_emails):
        slot_start = current_time
        slot_end = current_time + timedelta(minutes=slot_duration)
        timetable.append({
            "candidate_email": email,
            "start_time": slot_start.strftime("%H:%M"),
            "end_time": slot_end.strftime("%H:%M"),
            "date": interview_date
        })
        current_time = slot_end
    
    table_text = "Candidate Email       | Interview Date | Start Time | End Time\n"
    table_text += "---------------------|----------------|------------|---------\n"
    for slot in timetable:
        email = slot['candidate_email']
        date = slot['date']
        start = slot['start_time']
        end = slot['end_time']
        table_text += f"{email:<20} | {date:<14} | {start:<10} | {end}\n"
    
    return table_text, timetable

# Helper Function: Load HR Questions
def load_hr_questions():
    with open("HR.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    context = data["data"][0]["paragraphs"][0]["context"]
    questions = [q.strip() for q in context.split("\n") if q.strip()]
    return questions

import os
import uvicorn
import json
import random
import re
import time
import base64
import asyncio
import io
import torch
import cv2
import numpy as np
import pandas as pd
import plotly.express as px
import string
import glob
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from fastapi import FastAPI, HTTPException, Request, Form, UploadFile, File, Response, Query, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse, FileResponse  
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from email.mime.text import MIMEText
import smtplib
from PIL import Image
import torchvision
import torchvision.transforms as transforms
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from sklearn.feature_extraction.text import TfidfVectorizer 
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer, util
import hashlib
import ollama

# Helper Function: Email Sending
def send_email(to_address, subject, message):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "125150054@sastra.ac.in"
    sender_password = "ksdd eqpj rtqv ytfz"  # Use environment variables in production!
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_address
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, [to_address], msg.as_string())
        server.quit()
        print(f"Email successfully sent to {to_address}")
    except Exception as e:
        print(f"Failed to send email to {to_address}: {e}")

# Helper Function: Generate Timetable
def generate_timetable(candidate_emails: List[str], from_time: str, to_time: str, interview_date: str) -> tuple[str, List[dict]]:
    try:
        start_datetime = datetime.strptime(f"{interview_date} {from_time}", "%Y-%m-%d %H:%M")
        end_datetime = datetime.strptime(f"{interview_date} {to_time}", "%Y-%m-%d %H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date or time format")
    
    total_duration = (end_datetime - start_datetime).total_seconds() / 60
    if total_duration <= 0:
        raise HTTPException(status_code=400, detail="To time must be after from time")
    
    num_candidates = len(candidate_emails)
    slot_duration = total_duration // num_candidates
    
    timetable = []
    current_time = start_datetime
    for i, email in enumerate(candidate_emails):
        slot_start = current_time
        slot_end = current_time + timedelta(minutes=slot_duration)
        timetable.append({
            "candidate_email": email,
            "start_time": slot_start.strftime("%H:%M"),
            "end_time": slot_end.strftime("%H:%M"),
            "date": interview_date
        })
        current_time = slot_end
    
    table_text = "Candidate Email       | Interview Date | Start Time | End Time\n"
    table_text += "---------------------|----------------|------------|---------\n"
    for slot in timetable:
        email = slot['candidate_email']
        date = slot['date']
        start = slot['start_time']
        end = slot['end_time']
        table_text += f"{email:<20} | {date:<14} | {start:<10} | {end}\n"
    
    return table_text, timetable

# Helper Function: Load HR Questions
def load_hr_questions():
    with open("HR.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    context = data["data"][0]["paragraphs"][0]["context"]
    questions = [q.strip() for q in context.split("\n") if q.strip()]
    return questions

# Helper Function: Evaluate Answer with Llama Model
import ollama

def evaluate_answer_with_llama(question: str, candidate_answer: str) -> float:
    """
    Evaluates a candidate's answer to a question using the Llama model and returns a score between 0 and 5.
    
    Args:
        question (str): The question asked to the candidate.
        candidate_answer (str): The candidate's response to the question.
    
    Returns:
        float: A score between 0.0 and 5.0 reflecting the quality and relevance of the answer.
    """
    # Construct the prompt for the Llama model
    prompt = f"""
Evaluate the following answer to the question and provide a score out of 5. 
If the candidate repeats the question, the score is 0. 
If the answer doesn’t match the question, give a score of 0. 
For a medium-level answer, give a score of 2. 
For an excellent answer, give a score of 5. 
Respond with only the numerical score.

Question: {question}
Answer: {candidate_answer}

Score:
"""
    
    # Send the prompt to the Llama model and get the response
    response = ollama.generate(model="llama3.2:1b", prompt=prompt)
    
    # Extract and process the score from the response
    try:
        score_text = response["response"].strip()
        score = float(score_text)
        # Clamp the score to ensure it’s between 0 and 5
        return min(max(score, 0.0), 5.0)
    except (KeyError, ValueError):
        # Return 0.0 if the response is invalid or cannot be converted to a float
        return 0.0

# Helper Functions for Admin Registration
def load_registered_admins():
    if os.path.exists("register.json"):
        with open("register.json", "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        default_admins = []
        with open("register.json", "w", encoding="utf-8") as f:
            json.dump(default_admins, f, ensure_ascii=False, indent=4)
        return default_admins

def save_registered_admins(admins):
    with open("register.json", "w", encoding="utf-8") as f:
        json.dump(admins, f, ensure_ascii=False, indent=4)

# Configuration and Template Setup
TEMPLATE_DIR = "templates"
if not os.path.exists(TEMPLATE_DIR):
    os.makedirs(TEMPLATE_DIR)

templates_data = {
    "index.html": """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Elegant Interview System</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {
      background: linear-gradient(135deg, #e3f2fd, #bbdefb);
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      min-height: 100vh;
      margin: 0;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .hero {
      text-align: center;
      padding: 40px;
      background: rgba(255, 255, 255, 0.9);
      border-radius: 15px;
      box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
      animation: fadeIn 1s ease-in;
    }
    .hero h1 {
      font-size: 2.5rem;
      color: #0d47a1;
      margin-bottom: 20px;
    }
    .hero p {
      font-size: 1.2rem;
      color: #1565c0;
      margin-bottom: 30px;
    }
    .btn-custom {
      padding: 12px 30px;
      font-size: 1.1rem;
      border-radius: 25px;
      transition: transform 0.3s, box-shadow 0.3s;
    }
    .btn-custom:hover {
      transform: translateY(-3px);
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body>
  <div class="hero">
    <h1>Elegant Interview System</h1>
    <p>Choose your role to begin</p>
    <a href="/candidate/login" class="btn btn-primary btn-custom mx-2">Candidate Login</a>
    <a href="/admin/login" class="btn btn-secondary btn-custom mx-2">Admin Login</a>
  </div>
</body>
</html>
""",
    "admin_login.html": """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Admin Login</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {
      background: linear-gradient(to right, #eceff1, #cfd8dc);
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .login-container {
      background: #fff;
      padding: 40px;
      border-radius: 15px;
      box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
      max-width: 450px;
      width: 100%;
      animation: slideUp 0.8s ease-out;
    }
    h2 {
      color: #37474f;
      margin-bottom: 30px;
      font-weight: 600;
    }
    .form-label {
      color: #455a64;
      font-weight: 500;
    }
    .form-control {
      border-radius: 10px;
      padding: 12px;
      transition: border-color 0.3s;
    }
    .form-control:focus {
      border-color: #1976d2;
      box-shadow: 0 0 5px rgba(25, 118, 210, 0.5);
    }
    .btn-login {
      background: #1976d2;
      border: none;
      padding: 12px;
      border-radius: 10px;
      font-size: 1.1rem;
      transition: background 0.3s, transform 0.3s;
    }
    .btn-login:hover {
      background: #1565c0;
      transform: translateY(-2px);
    }
    .forgot-link, .register-link {
      display: block;
      text-align: center;
      margin-top: 15px;
      color: #1976d2;
      text-decoration: none;
    }
    .forgot-link:hover, .register-link:hover {
      text-decoration: underline;
    }
    @keyframes slideUp {
      from { opacity: 0; transform: translateY(50px); }
      to { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body>
  <div class="login-container">
    <h2 class="text-center">Admin Login</h2>
    <form action="/admin/login" method="post">
      <div class="mb-4">
        <label for="email" class="form-label">Email Address</label>
        <input type="email" class="form-control" id="email" name="email" placeholder="Enter your email" required value="{{ email if email else '' }}">
      </div>
      <div class="mb-4">
        <label for="password" class="form-label">Password</label>
        <input type="password" class="form-control" id="password" name="password" placeholder="Enter your password" required>
      </div>
      <button type="submit" class="btn btn-login w-100">Login</button>
      <a href="/admin/forgot_password" class="forgot-link">Forgot Password?</a>
    </form>
    <p class="register-link">Don't have an account? <a href="/admin/register">Register here</a></p>
    {% if message %}
      <div class="alert alert-danger mt-3">
        {{ message }}
      </div>
    {% endif %}
  </div>
</body>
</html>
""",
    "admin_register.html": """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Admin Registration</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {
      background: linear-gradient(to right, #eceff1, #cfd8dc);
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .login-container {
      background: #fff;
      padding: 40px;
      border-radius: 15px;
      box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
      max-width: 450px;
      width: 100%;
      animation: slideUp 0.8s ease-out;
    }
    h2 {
      color: #37474f;
      margin-bottom: 30px;
      font-weight: 600;
    }
    .form-label {
      color: #455a64;
      font-weight: 500;
    }
    .form-control {
      border-radius: 10px;
      padding: 12px;
      transition: border-color 0.3s;
    }
    .form-control:focus {
      border-color: #1976d2;
      box-shadow: 0 0 5px rgba(25, 118, 210, 0.5);
    }
    .btn-login {
      background: #1976d2;
      border: none;
      padding: 12px;
      border-radius: 10px;
      font-size: 1.1rem;
      transition: background 0.3s, transform 0.3s;
    }
    .btn-login:hover {
      background: #1565c0;
      transform: translateY(-2px);
    }
    @keyframes slideUp {
      from { opacity: 0; transform: translateY(50px); }
      to { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body>
  <div class="login-container">
    <h2 class="text-center">Admin Registration</h2>
    <form action="/admin/register" method="post">
      <div class="mb-4">
        <label for="name" class="form-label">Name</label>
        <input type="text" class="form-control" id="name" name="name" placeholder="Enter your name" required value="{{ name if name else '' }}">
      </div>
      <div class="mb-4">
        <label for="email" class="form-label">Email Address</label>
        <input type="email" class="form-control" id="email" name="email" placeholder="Enter your email" required value="{{ email if email else '' }}">
      </div>
      <div class="mb-4">
        <label for="password" class="form-label">Password</label>
        <input type="password" class="form-control" id="password" name="password" placeholder="Enter your password" required>
      </div>
      <button type="submit" class="btn btn-login w-100">Register</button>
    </form>
    <p class="login-link mt-3 text-center">Already have an account? <a href="/admin/login">Login here</a></p>
    {% if message %}
      <div class="alert {% if message_type == 'success' %}alert-success{% else %}alert-danger{% endif %} mt-3">
        {{ message }}
        {% if message_type == 'success' %}
          <br><a href="/admin/login" class="btn btn-primary mt-2">Go to Login</a>
        {% endif %}
      </div>
    {% endif %}
  </div>
</body>
</html>
""",
    "admin_forgot_password.html": """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Forgot Password</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {
      background: linear-gradient(to right, #eceff1, #cfd8dc);
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .login-container {
      background: #fff;
      padding: 40px;
      border-radius: 15px;
      box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
      max-width: 450px;
      width: 100%;
      animation: slideUp 0.8s ease-out;
    }
    h2 {
      color: #37474f;
      margin-bottom: 30px;
      font-weight: 600;
    }
    .form-label {
      color: #455a64;
      font-weight: 500;
    }
    .form-control {
      border-radius: 10px;
      padding: 12px;
      transition: border-color 0.3s;
    }
    .form-control:focus {
      border-color: #1976d2;
      box-shadow: 0 0 5px rgba(25, 118, 210, 0.5);
    }
    .btn-login {
      background: #1976d2;
      border: none;
      padding: 12px;
      border-radius: 10px;
      font-size: 1.1rem;
      transition: background 0.3s, transform 0.3s;
    }
    .btn-login:hover {
      background: #1565c0;
      transform: translateY(-2px);
    }
    @keyframes slideUp {
      from { opacity: 0; transform: translateY(50px); }
      to { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body>
  <div class="login-container">
    <h2 class="text-center">Forgot Password</h2>
    <form action="/admin/forgot_password" method="post">
      <div class="mb-4">
        <label for="email" class="form-label">Email Address</label>
        <input type="email" class="form-control" id="email" name="email" placeholder="Enter your email" required value="{{ email if email else '' }}">
      </div>
      <button type="submit" class="btn btn-login w-100">Send Password</button>
    </form>
    <p class="login-link mt-3 text-center"><a href="/admin/login">Back to Login</a></p>
    {% if message %}
      <div class="alert {% if message_type == 'success' %}alert-success{% else %}alert-danger{% endif %} mt-3">
        {{ message }}
      </div>
    {% endif %}
  </div>
</body>
</html>
""",
    "admin_panel.html": """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Admin Panel</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {
      background: #f4f6f9;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      min-height: 100vh;
      padding: 20px;
    }
    .panel-container {
      background: #fff;
      padding: 30px;
      border-radius: 15px;
      box-shadow: 0 8px 30px rgba(0, 0, 0, 0.05);
      max-width: 800px;
      margin: 0 auto;
      animation: fadeIn 0.8s ease-in;
    }
    h2 {
      color: #263238;
      text-align: center;
      margin-bottom: 30px;
      font-weight: 600;
    }
    .form-label {
      color: #455a64;
      font-weight: 500;
    }
    .form-control, .form-select {
      border-radius: 10px;
      padding: 12px;
      transition: border-color 0.3s;
    }
    .form-control:focus, .form-select:focus {
      border-color: #0288d1;
      box-shadow: 0 0 5px rgba(2, 136, 209, 0.5);
    }
    .btn-primary {
      background: #0288d1;
      border: none;
      padding: 12px;
      border-radius: 10px;
      font-size: 1.1rem;
      transition: background 0.3s, transform 0.3s;
    }
    .btn-primary:hover {
      background: #0277bd;
      transform: translateY(-2px);
    }
    .btn-info {
      background: #4fc3f7;
      border: none;
      padding: 10px;
      border-radius: 10px;
      transition: background 0.3s, transform 0.3s;
    }
    .btn-info:hover {
      background: #29b6f6;
      transform: translateY(-2px);
    }
    .btn-secondary {
      background: #6c757d;
      border: none;
      padding: 10px;
      border-radius: 10px;
      transition: background 0.3s, transform 0.3s;
    }
    .btn-secondary:hover {
      background: #5a6268;
      transform: translateY(-2px);
    }
    .form-check-label {
      margin-left: 10px;
    }
    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }
  </style>
</head>
<body>
 <div class="panel-container">
  <h2>Schedule Interview</h2>
  <form action="/admin/schedule" method="post">
    <div class="mb-3">
      <label for="level" class="form-label">Interview Level</label>
      <select class="form-select" id="level" name="level" required onchange="updateFields()">
        <option value="">-- Select Level --</option>
        <option value="1">Level 1 (Aptitude Test)</option>
        <option value="2">Level 2 (Q&A Interview)</option>
        <option value="3">Level 3 (Google Meet)</option>
      </select>
    </div>
    <div class="mb-3">
      <label for="job_title" class="form-label">Job Title</label>
      <input type="text" class="form-control" id="job_title" name="job_title" placeholder="Enter job title" required />
    </div>
    <div class="mb-3" id="job_desc_group" style="display:none;">
      <label for="job_description" class="form-label">Job Description</label>
      <textarea class="form-control" id="job_description" name="job_description" rows="3" placeholder="Enter job description"></textarea>
    </div>
      <div class="mb-3" id="cand_email_group" style="display:none;">
        <label for="candidate_emails" class="form-label">Candidate Emails (comma separated)</label>
        <input type="text" class="form-control" id="candidate_emails" name="candidate_emails" placeholder="e.g., email1@example.com, email2@example.com" required />
      </div>
      <div class="mb-3" id="intv_date_group" style="display:none;">
        <label for="interview_datetime" class="form-label">Interview Date and Time</label>
        <input type="datetime-local" class="form-control" id="interview_datetime" name="interview_datetime" />
      </div>
      <div class="mb-3" id="hr_available_group" style="display:none;">
        <label class="form-label">Is HR Available?</label>
        <div class="form-check form-check-inline">
          <input class="form-check-input" type="radio" name="hr_available" id="hr_yes" value="yes" onclick="toggleHRFields(true)">
          <label class="form-check-label" for="hr_yes">Yes</label>
        </div>
        <div class="form-check form-check-inline">
          <input class="form-check-input" type="radio" name="hr_available" id="hr_no" value="no" onclick="toggleHRFields(false)">
          <label class="form-check-label" for="hr_no">No</label>
        </div>
      </div>
      <div id="hr_fields" style="display:none;">
        <div class="mb-3">
          <label for="hr_emails" class="form-label">HR Emails</label>
          <input type="text" class="form-control" id="hr_emails" name="hr_emails" placeholder="e.g., hr1@example.com, hr2@example.com">
        </div>
        <div class="mb-3">
          <label for="viewer_emails" class="form-label">Viewers' Emails (Optional)</label>
          <input type="text" class="form-control" id="viewer_emails" name="viewer_emails" placeholder="e.g., viewer1@example.com">
        </div>
        <div class="mb-3">
          <label for="from_time" class="form-label">From Time</label>
          <input type="time" class="form-control" id="from_time" name="from_time">
        </div>
        <div class="mb-3">
          <label for="to_time" class="form-label">To Time</label>
          <input type="time" class="form-control" id="to_time" name="to_time">
        </div>
        <div class="mb-3">
          <label for="hr_date" class="form-label">Interview Date</label>
          <input type="date" class="form-control" id="hr_date" name="hr_date">
        </div>
      </div>
      <button type="submit" class="btn btn-primary w-100 mb-3">Schedule Interview</button>
      <a href="/admin/dashboard" class="btn btn-info w-100">View Dashboard</a>
    </form>
    <div class="text-center mt-4">
      <a href="/" class="btn btn-secondary">Back to Home</a>
    </div>
  </div>
  <script>
    function updateFields() {
      const level = document.getElementById("level").value;
      document.getElementById("job_desc_group").style.display = "none";
      document.getElementById("cand_email_group").style.display = "none";
      document.getElementById("intv_date_group").style.display = "none";
      document.getElementById("hr_available_group").style.display = "none";
      document.getElementById("hr_fields").style.display = "none";
      if (level === "1" || level === "2") {
        document.getElementById("cand_email_group").style.display = "block";
        document.getElementById("intv_date_group").style.display = "block";
        if (level === "2") document.getElementById("job_desc_group").style.display = "block";
      } else if (level === "3") {
        document.getElementById("cand_email_group").style.display = "block";
        document.getElementById("hr_available_group").style.display = "block";
      }
    }
    function toggleHRFields(show) {
      const hrFields = document.getElementById("hr_fields");
      hrFields.style.display = show ? "block" : "none";
      document.getElementById("intv_date_group").style.display = show ? "none" : "block";
    }
  </script>
</body>
</html>
""",
    "candidate_login.html": """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Candidate Login</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {
      background: linear-gradient(to right, #e1f5fe, #b3e5fc);
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .login-container {
      background: #fff;
      padding: 40px;
      border-radius: 15px;
      box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
      max-width: 450px;
      width: 100%;
      animation: slideUp 0.8s ease-out;
    }
    h2 {
      color: #0277bd;
      margin-bottom: 30px;
      font-weight: 600;
    }
    .form-label {
      color: #455a64;
      font-weight: 500;
    }
    .form-control {
      border-radius: 10px;
      padding: 12px;
      transition: border-color 0.3s;
    }
    .form-control:focus {
      border-color: #0288d1;
      box-shadow: 0 0 5px rgba(2, 136, 209, 0.5);
    }
    .btn-login {
      background: #0288d1;
      border: none;
      padding: 12px;
      border-radius: 10px;
      font-size: 1.1rem;
      transition: background 0.3s, transform 0.3s;
    }
    .btn-login:hover {
      background: #0277bd;
      transform: translateY(-2px);
    }
    @keyframes slideUp {
      from { opacity: 0; transform: translateY(50px); }
      to { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body>
  <div class="login-container">
    <h2 class="text-center">Candidate Login</h2>
    <form action="/candidate/login" method="post">
      <div class="mb-4">
        <label for="email" class="form-label">Email Address</label>
        <input type="email" class="form-control" id="email" name="email" placeholder="Enter your email" required>
      </div>
      <div class="mb-4">
        <label for="password" class="form-label">Password</label>
        <input type="password" class="form-control" id="password" name="password" placeholder="Enter your password" required>
      </div>
      <button type="submit" class="btn btn-login w-100">Login</button>
    </form>
    {% if message %}
      <div class="alert alert-danger mt-3">
        {{ message }}
      </div>
    {% endif %}
  </div>
</body>
</html>
""",  
    "interview.html": """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Candidate Interview</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {
      background: #f5f7fa;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      min-height: 100vh;
      padding: 20px;
    }
    .interview-container {
      background: #fff;
      padding: 30px;
      border-radius: 15px;
      box-shadow: 0 8px 30px rgba(0, 0, 0, 0.05);
      max-width: 900px;
      margin: 0 auto;
      position: relative;
      animation: fadeIn 0.8s ease-in;
    }
    .illustration-container {
      text-align: center;
      margin-bottom: 20px;
    }
    .illustration-container img {
      max-width: 100%;
      height: auto;
      border-radius: 10px;
    }
    .bubble {
      padding: 15px;
      border-radius: 15px;
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
      max-width: 300px;
      position: absolute;
      transition: opacity 0.5s;
    }
    .question-bubble {
      background: #e3f2fd;
      top: 20px;
      right: 20px;
    }
    .answer-bubble {
      background: #fff3e0;
      top: 100px;
      left: 20px;
    }
    #hidden-video {
      width: 100%;
      max-width: 400px;
      border-radius: 10px;
      margin: 20px auto;
      display: block;
    }
    #timer {
      font-weight: bold;
      color: #d32f2f;
    }
    #warning-message {
      color: #d32f2f;
      font-weight: 500;
      margin-top: 10px;
    }
    .btn-next {
      background: #1976d2;
      border: none;
      padding: 10px 20px;
      border-radius: 10px;
      transition: background 0.3s, transform 0.3s;
    }
    .btn-next:hover {
      background: #1565c0;
      transform: translateY(-2px);
    }
    .section {
      margin-top: 20px;
      padding: 20px;
      background: #fafafa;
      border-radius: 10px;
    }
    #question-section {
      position: relative;
    }
    #next-btn {
      position: absolute;
      bottom: 20px;
      right: 20px;
    }
    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }
  </style>
</head>
<body>
  <div class="interview-container">
    <div id="illustration-container" class="illustration-container" style="display:none;">
      <img src="/static/image.gif" alt="Interview Illustration">
    </div>
    <div id="question-bubble" class="bubble question-bubble" style="display:none;">
      <p id="question-text" class="h5 mb-0"></p>
    </div>
    <div id="answer-bubble" class="bubble answer-bubble" style="display:none;">
      <p>Your Answer: <span id="candidate-answer"></span></p>
    </div>
    <div id="precheck" class="section text-center">
      <p class="lead">Please allow camera and microphone access for precheck.</p>
      <video id="hidden-video" autoplay muted></video>
      <canvas id="video-canvas" width="320" height="240" style="display:none;"></canvas>
      <p id="precheck-status" class="mt-3">Checking...</p>
      <button id="start-interview" class="btn btn-primary mt-3" disabled>Start Interview</button>
    </div>
    <div id="question-section" class="section" style="display:none;">
      <p>Time Remaining: <span id="timer">30</span> seconds</p>
      <p id="warning-message"></p>
      <button id="next-btn" class="btn btn-next">Next Question</button>
    </div>
    <div id="result-section" class="section text-center" style="display:none;">
      <h3>Interview Completed</h3>
      <p id="total-score"></p>
      <pre id="evaluations" class="text-start"></pre>
    </div>
  </div>
  <script>
    const email = "{{ email }}";
    let qas = {{ qas|tojson }};
    let currentQuestionIndex = 0;
    let responses = [];
    const timeLimit = 30;
    let detectionInterval;
    let warnings = 0;
    const maxWarnings = 3;
    let candidateStream;
    let mediaRecorder;
    let recordedChunks = [];
    let skipRequested = false;
    let currentRecognition = null;

    async function recognizeSpeechForPrecheck() {
      return new Promise((resolve, reject) => {
        if (!("mediaDevices" in navigator && "getUserMedia" in navigator.mediaDevices)) {
          return reject("getUserMedia is not supported.");
        }
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) return reject("Speech Recognition not supported");
        const recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.interimResults = true;
        recognition.maxAlternatives = 1;
        let transcript = "";
        recognition.onresult = (event) => {
          for (let i = event.resultIndex; i < event.results.length; i++) {
            if (event.results[i].isFinal) {
              transcript += event.results[i][0].transcript + " ";
              if (transcript.toLowerCase().includes("hello")) {
                recognition.stop();
              }
            }
          }
          document.getElementById('candidate-answer').innerText = transcript;
        };
        recognition.onerror = (event) => { console.error("Speech recognition error:", event.error); };
        recognition.onend = () => { resolve(transcript.trim()); };
        recognition.start();
      });
    }

    async function recognizeSpeechForDuration() {
      return new Promise((resolve, reject) => {
        if (!("mediaDevices" in navigator && "getUserMedia" in navigator.mediaDevices)) {
          return reject("getUserMedia is not supported.");
        }
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) return reject("Speech Recognition not supported");
        const recognition = new SpeechRecognition();
        currentRecognition = recognition;
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.maxAlternatives = 1;
        let finalTranscript = "";
        let lastResultTime = Date.now();
        let minDurationPassed = false;

        setTimeout(() => {
          minDurationPassed = true;
        }, 30000); // Minimum 30 seconds

        const checkSilence = setInterval(() => {
          if (minDurationPassed && (Date.now() - lastResultTime > 2000)) {
            recognition.stop();
          }
        }, 1000);

        recognition.onresult = (event) => {
          lastResultTime = Date.now();
          let interimTranscript = "";
          for (let i = event.resultIndex; i < event.results.length; i++) {
            if (event.results[i].isFinal) {
              finalTranscript += event.results[i][0].transcript + " ";
            } else {
              interimTranscript += event.results[i][0].transcript + " ";
            }
          }
          document.getElementById('candidate-answer').innerText = finalTranscript + interimTranscript;
        };
        recognition.onerror = (event) => {
          clearInterval(checkSilence);
          console.error("Speech recognition error:", event.error);
          reject(event.error);
        };
        recognition.onend = () => {
          clearInterval(checkSilence);
          currentRecognition = null;
          resolve(finalTranscript.trim());
        };
        recognition.start();
      });
    }

    async function updateCanvasWithDetection() {
      try {
        const video = document.getElementById('hidden-video');
        if (!video.videoWidth || !video.videoHeight) return;
        const canvas = document.createElement("canvas");
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const blob = await new Promise(resolve => canvas.toBlob(resolve, "image/jpeg"));
        const formData = new FormData();
        formData.append("email", "precheck");
        formData.append("file", blob, "frame.jpg");
        const res = await fetch("/interview/detect_frame", { method: "POST", body: formData });
        const data = await res.json();
        document.getElementById('warning-message').innerText = data.message;
        const match = data.message.match(/Warning\((\d)\/3\)/);
        if(match) {
          let newWarningCount = parseInt(match[1]);
          if(newWarningCount > warnings) {
            warnings = newWarningCount;
            if(warnings >= maxWarnings) {
              alert("Interview terminated due to repeated violations.");
              clearInterval(detectionInterval);
              window.location.href = "/candidate/login";
              return;
            }
          }
        }
      } catch (err) {
        console.error("Detection error:", err);
      }
    }

    async function startPrecheck() {
      try {
        if (!("mediaDevices" in navigator && "getUserMedia" in navigator.mediaDevices)) {
          document.getElementById('precheck-status').innerText = "getUserMedia not supported.";
          return;
        }
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        candidateStream = stream;
        if (!stream || stream.getVideoTracks().length === 0) {
          document.getElementById('precheck-status').innerText = "Enable your camera.";
          return;
        }
        const video = document.getElementById('hidden-video');
        video.srcObject = stream;
        video.onloadedmetadata = async () => {
          video.play();
          await new Promise(resolve => setTimeout(resolve, 2000));
          const precheckDetectionInterval = setInterval(updateCanvasWithDetection, 2000);
          const transcript = await recognizeSpeechForPrecheck();
          clearInterval(precheckDetectionInterval);
          if (transcript.toLowerCase().includes("hello")) {
            document.getElementById('precheck-status').innerText = "Precheck successful.";
            document.getElementById('start-interview').disabled = false;
          } else {
            document.getElementById('precheck-status').innerText = "Voice detection failed. Refreshing...";
            setTimeout(() => { window.location.reload(); }, 2000);
          }
        };
      } catch (err) {
        document.getElementById('precheck-status').innerText = "Precheck failed: " + err;
      }
    }

    async function askQuestion() {
      skipRequested = false;
      document.getElementById('question-bubble').style.display = "block";
      document.getElementById('answer-bubble').style.display = "block";
      document.getElementById('illustration-container').style.display = "block";
      if (currentQuestionIndex >= qas.length) {
        submitInterview();
        return;
      }
      document.getElementById('candidate-answer').innerText = "";
      const currentQA = qas[currentQuestionIndex];
      document.getElementById('question-text').innerText = currentQA.question;
      let synth = window.speechSynthesis;
      synth.speak(new SpeechSynthesisUtterance(currentQA.question));
      let remainingTime = timeLimit;
      document.getElementById('timer').innerText = remainingTime;
      document.getElementById('question-section').style.display = "block";
      let timerIntervalLocal = setInterval(() => { 
         remainingTime--; 
         document.getElementById('timer').innerText = remainingTime; 
         if (remainingTime <= 0) clearInterval(timerIntervalLocal);
      }, 1000);
      const answer = await recognizeSpeechForDuration();
      clearInterval(timerIntervalLocal);
      const candidateAnswer = document.getElementById('candidate-answer').innerText;
      responses.push({ question: currentQA.question, candidate_answer: candidateAnswer });
      document.getElementById('candidate-answer').innerText = "";
      currentQuestionIndex++;
      if (currentQuestionIndex < qas.length) {
        askQuestion();
      } else {
        clearInterval(detectionInterval);
        submitInterview();
      }
    }

    async function uploadRecording(blob) {
      const formData = new FormData();
      formData.append("file", blob, "recording.webm");
      formData.append("email", email);
      try {
        const res = await fetch("/interview/upload_recording", { method: "POST", body: formData });
        const data = await res.json();
        console.log("Upload response:", data.message);
      } catch (err) {
        console.error("Error uploading recording:", err);
      }
    }

    async function submitInterview() {
      if (mediaRecorder && mediaRecorder.state !== "inactive") {
        mediaRecorder.stop();
        mediaRecorder.onstop = async () => {
          const blob = new Blob(recordedChunks, { type: "video/webm" });
          await uploadRecording(blob);
          finalizeSubmission();
        };
      } else {
        finalizeSubmission();
      }
    }

    function finalizeSubmission() {
      const payload = { email: email, responses: responses };
      fetch("/interview/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }).then(() => {
        window.location.href = "/candidate/submit_name?email=" + encodeURIComponent(email);
      });
    }

    document.getElementById('next-btn').addEventListener('click', () => {
      if (currentRecognition) {
        currentRecognition.stop();
      }
      skipRequested = true;
    });

    document.getElementById('start-interview').addEventListener('click', () => {
      if (candidateStream) {
        recordedChunks = [];
        mediaRecorder = new MediaRecorder(candidateStream);
        mediaRecorder.ondataavailable = event => { if (event.data.size > 0) { recordedChunks.push(event.data); } };
        mediaRecorder.start();
      }
      document.getElementById('precheck').style.display = "none";
      detectionInterval = setInterval(detectFrame, 2000);
      askQuestion();
    });

    async function detectFrame() {
      const video = document.getElementById('hidden-video');
      if (!video.videoWidth || !video.videoHeight) return;
      const canvas = document.createElement("canvas");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      const blob = await new Promise(resolve => canvas.toBlob(resolve, "image/jpeg"));
      const formData = new FormData();
      formData.append("email", email);
      formData.append("file", blob, "frame.jpg");
      try {
        const res = await fetch("/interview/detect_frame", { method: "POST", body: formData });
        const data = await res.json();
        document.getElementById('warning-message').innerText = data.message;
        const match = data.message.match(/Warning\((\d)\/3\)/);
        if(match) {
          let newWarningCount = parseInt(match[1]);
          if(newWarningCount > warnings) {
            warnings = newWarningCount;
            if(warnings >= maxWarnings) {
              alert("Interview terminated due to repeated violations.");
              clearInterval(detectionInterval);
              window.location.href = "/candidate/login";
              return;
            }
            clearInterval(detectionInterval);
            setTimeout(() => {
              detectionInterval = setInterval(detectFrame, 2000);
            }, 5000);
          }
        }
      } catch(err) {
        console.error("Detection error:", err);
      }
    }

    window.onload = function() {
      startPrecheck();
    };
  </script>
</body>
</html>
""",
    "aptitude.html": """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Aptitude Test</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {
      background: #f5f7fa;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      min-height: 100vh;
      padding: 20px;
    }
    .aptitude-container {
      background: #fff;
      padding: 30px;
      border-radius: 15px;
      box-shadow: 0 8px 30px rgba(0, 0, 0, 0.05);
      max-width: 1200px;
      margin: 0 auto;
      display: flex;
      animation: fadeIn 0.8s ease-in;
    }
    .main-content {
      flex: 1;
      padding-right: 20px;
    }
    .sidebar {
      width: 80px;
      background: #fafafa;
      padding: 15px;
      border-radius: 10px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 10px;
    }
    .question-number {
      width: 40px;
      height: 40px;
      line-height: 40px;
      border-radius: 50%;
      text-align: center;
      font-weight: bold;
      border: 2px solid #1976d2;
      color: #1976d2;
      background: #fff;
      cursor: pointer;
      transition: all 0.3s;
    }
    .question-number.active {
      background: #1976d2;
      color: #fff;
    }
    .question-number.answered {
      background: #2e7d32;
      border-color: #2e7d32;
      color: #fff;
    }
    .question-area {
      margin-top: 20px;
    }
    .question {
      font-size: 1.3rem;
      color: #263238;
      margin-bottom: 15px;
    }
    .options li {
      margin-bottom: 15px;
      padding: 10px;
      border-radius: 8px;
      transition: background 0.3s;
    }
    .options li:hover {
      background: #e3f2fd;
    }
    .timer {
      font-size: 1.2rem;
      color: #d32f2f;
      font-weight: bold;
    }
    #live-warning-message {
      color: #d32f2f;
      font-weight: 500;
    }
    .btn-nav {
      padding: 10px 20px;
      border-radius: 10px;
      transition: background 0.3s, transform 0.3s;
    }
    .btn-nav:hover {
      transform: translateY(-2px);
    }
    #hidden-video {
      width: 100%;
      max-width: 400px;
      border-radius: 10px;
      margin: 20px auto;
      display: block;
    }
    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }
  </style>
</head>
<body>
  <div class="aptitude-container">
    <div class="main-content">
      <div id="precheck" class="text-center">
        <p class="lead">Please allow camera and microphone access for precheck.</p>
        <video id="hidden-video" autoplay muted></video>
        <canvas id="video-canvas" width="320" height="240" style="display:none;"></canvas>
        <p id="precheck-status" class="mt-3">Checking...</p>
        <button id="start-test" class="btn btn-primary mt-3" disabled>Start Test</button>
        <p id="warning-message"></p>
      </div>
      <div id="test-area" class="question-area" style="display:none;">
        <div class="timer">Time: <span id="timer">50.00</span></div>
        <p id="live-warning-message"></p>
        <div id="question-container">
          <div class="question" id="questionText"></div>
          <ul class="options list-unstyled" id="optionsContainer"></ul>
        </div>
        <div class="navigation mt-4 text-center">
          <button class="btn btn-secondary btn-nav" id="prevBtn" onclick="prevQuestion()" style="display:none;">Previous</button>
          <button class="btn btn-secondary btn-nav mx-2" id="nextBtn" onclick="nextQuestion()">Next</button>
          <button class="btn btn-primary btn-nav" id="submitBtn" onclick="submitAnswers()">Submit</button>
        </div>
      </div>
    </div>
    <div class="sidebar" id="questionList"></div>
  </div>
  <script>
    const email = "{{ email }}";
    let questions = {{ questions|tojson }};
    let currentIndex = 0;
    let userAnswers = {};
    let totalTime = 0;
    let timerInterval = null;
    let detectionInterval;
    let warnings = 0;
    const maxWarnings = 3;
    let candidateStream;
    let mediaRecorder;
    let recordedChunks = [];

    function renderQuestion() {
      if (questions.length === 0) return;
      const currentQuestion = questions[currentIndex];
      document.getElementById('questionText').innerText = (currentIndex + 1) + ". " + currentQuestion.question;
      let optionsContainer = document.getElementById('optionsContainer');
      optionsContainer.innerHTML = "";
      currentQuestion.options.forEach(opt => {
        let li = document.createElement('li');
        let label = document.createElement('label');
        let radio = document.createElement('input');
        radio.type = 'radio';
        radio.name = 'option';
        radio.value = opt;
        if (userAnswers[currentQuestion.id] === opt) {
          radio.checked = true;
        }
        label.appendChild(radio);
        label.appendChild(document.createTextNode(" " + opt));
        li.appendChild(label);
        optionsContainer.appendChild(li);
      });
      updateQuestionCircles();
      // Button visibility logic
      document.getElementById('prevBtn').style.display = currentIndex === 0 ? 'none' : 'inline-block';
      document.getElementById('nextBtn').style.display = currentIndex === questions.length - 1 ? 'none' : 'inline-block';
      document.getElementById('submitBtn').style.display = 'inline-block';
    }

    function saveCurrentAnswer() {
      const currentQuestion = questions[currentIndex];
      const radios = document.getElementsByName('option');
      let answered = false;
      for (let r of radios) {
        if (r.checked) {
          userAnswers[currentQuestion.id] = r.value;
          answered = true;
          break;
        }
      }
      const circles = document.getElementsByClassName('question-number');
      if (answered) {
        circles[currentIndex].classList.add('answered');
      } else {
        circles[currentIndex].classList.remove('answered');
      }
    }

    function nextQuestion() {
      saveCurrentAnswer();
      if (currentIndex < questions.length - 1) {
        currentIndex++;
        renderQuestion();
      }
    }

    function prevQuestion() {
      saveCurrentAnswer();
      if (currentIndex > 0) {
        currentIndex--;
        renderQuestion();
      }
    }

    function updateQuestionCircles() {
      const circles = document.getElementsByClassName('question-number');
      for (let i = 0; i < circles.length; i++) {
        circles[i].classList.remove('active');
        if (i === currentIndex) {
          circles[i].classList.add('active');
        }
      }
    }

    function buildQuestionCircles() {
      const questionListDiv = document.getElementById('questionList');
      questionListDiv.innerHTML = "";
      for (let i = 0; i < questions.length; i++) {
        const circle = document.createElement('div');
        circle.className = 'question-number';
        circle.textContent = i + 1;
        circle.onclick = () => {
          saveCurrentAnswer();
          currentIndex = i;
          renderQuestion();
          updateQuestionCircles();
        };
        questionListDiv.appendChild(circle);
      }
    }

    function submitAnswers() {
      clearInterval(timerInterval);
      clearInterval(detectionInterval);
      saveCurrentAnswer();
      fetch('/ap1/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email, answers: userAnswers })
      })
      .then(res => res.json())
      .then(result => {
        window.location.href = "/candidate/submit_name?email=" + encodeURIComponent(email);
      });
    }

    function startTimer() {
      const maxTime = 50 * 60; // 50 minutes in seconds
      let remainingTime = maxTime;
      timerInterval = setInterval(() => {
        if (remainingTime <= 0) {
          clearInterval(timerInterval);
          submitAnswers();
        } else {
          const minutes = Math.floor(remainingTime / 60);
          const seconds = remainingTime % 60;
          document.getElementById('timer').textContent = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
          remainingTime--;
        }
      }, 1000);
    }

    async function updateCanvasWithDetection() {
      try {
        const video = document.getElementById('hidden-video');
        if (!video.videoWidth || !video.videoHeight) return;
        const canvas = document.createElement("canvas");
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const blob = await new Promise(resolve => canvas.toBlob(resolve, "image/jpeg"));
        const formData = new FormData();
        formData.append("email", "precheck");
        formData.append("file", blob, "frame.jpg");
        const res = await fetch("/interview/detect_frame", { method: "POST", body: formData });
        const data = await res.json();
        document.getElementById('warning-message').innerText = data.message;
        const match = data.message.match(/Warning\((\d)\/3\)/);
        if(match) {
          let newWarningCount = parseInt(match[1]);
          if(newWarningCount > warnings) {
            warnings = newWarningCount;
            if(warnings >= maxWarnings) {
              alert("Test terminated due to repeated violations.");
              clearInterval(detectionInterval);
              window.location.href = "/candidate/login";
              return;
            }
          }
        }
      } catch (err) {
        console.error("Detection error:", err);
      }
    }

    async function startPrecheck() {
      try {
        if (!("mediaDevices" in navigator && "getUserMedia" in navigator.mediaDevices)) {
          document.getElementById('precheck-status').innerText = "getUserMedia not supported.";
          return;
        }
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        candidateStream = stream;
        if (!stream || stream.getVideoTracks().length === 0) {
          document.getElementById('precheck-status').innerText = "Enable your camera.";
          return;
        }
        const video = document.getElementById('hidden-video');
        video.srcObject = stream;
        video.onloadedmetadata = async () => {
          video.play();
          await new Promise(resolve => setTimeout(resolve, 2000));
          const precheckDetectionInterval = setInterval(updateCanvasWithDetection, 2000);
          const transcript = await recognizeSpeechForPrecheck();
          clearInterval(precheckDetectionInterval);
          if (transcript.toLowerCase().includes("hello")) {
            document.getElementById('precheck-status').innerText = "Precheck successful.";
            document.getElementById('start-test').disabled = false;
          } else {
            document.getElementById('precheck-status').innerText = "Voice detection failed. Refreshing...";
            setTimeout(() => { window.location.reload(); }, 2000);
          }
        };
      } catch (err) {
        document.getElementById('precheck-status').innerText = "Precheck failed: " + err;
      }
    }

    async function recognizeSpeechForPrecheck() {
      return new Promise((resolve, reject) => {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) return reject("Speech Recognition not supported");
        const recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.interimResults = true;
        recognition.maxAlternatives = 1;
        let transcript = "";
        recognition.onresult = (event) => {
          for (let i = event.resultIndex; i < event.results.length; i++) {
            if (event.results[i].isFinal) {
              transcript += event.results[i][0].transcript + " ";
              if (transcript.toLowerCase().includes("hello")) {
                recognition.stop();
              }
            }
          }
        };
        recognition.onerror = (event) => { console.error("Speech recognition error:", event.error); };
        recognition.onend = () => { resolve(transcript.trim()); };
        recognition.start();
      });
    }

    document.getElementById('start-test').addEventListener('click', () => {
      if (candidateStream) {
        recordedChunks = [];
        mediaRecorder = new MediaRecorder(candidateStream);
        mediaRecorder.ondataavailable = event => { if (event.data.size > 0) { recordedChunks.push(event.data); } };
        mediaRecorder.start();
      }
      document.getElementById('precheck').style.display = "none";
      document.getElementById('test-area').style.display = "block";
      buildQuestionCircles();
      renderQuestion();
      startTimer();
      detectionInterval = setInterval(detectFrame, 2000);
    });

    async function detectFrame() {
      const video = document.getElementById('hidden-video');
      if (!video.videoWidth || !video.videoHeight) return;
      const canvas = document.createElement("canvas");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      const blob = await new Promise(resolve => canvas.toBlob(resolve, "image/jpeg"));
      const formData = new FormData();
      formData.append("email", email);
      formData.append("file", blob, "frame.jpg");
      try {
        const res = await fetch("/interview/detect_frame", { method: "POST", body: formData });
        const data = await res.json();
        document.getElementById('live-warning-message').innerText = data.message;
        const match = data.message.match(/Warning\((\d)\/3\)/);
        if(match) {
          let newWarningCount = parseInt(match[1]);
          if(newWarningCount > warnings) {
            warnings = newWarningCount;
            if(warnings >= maxWarnings) {
              alert("Test terminated due to repeated violations.");
              clearInterval(detectionInterval);
              window.location.href = "/candidate/login";
              return;
            }
            clearInterval(detectionInterval);
            setTimeout(() => {
              detectionInterval = setInterval(detectFrame, 2000);
            }, 5000);
          }
        }
      } catch(err) {
        console.error("Detection error:", err);
      }
    }

    window.onload = function() {
      startPrecheck();
    };
  </script>
</body>
</html>
""",
    "admin_dashboard.html": """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Admin Dashboard</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {
      background: #f4f6f9;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      min-height: 100vh;
      padding: 20px;
    }
    .container {
      max-width: 1200px;
      margin: 0 auto;
    }
    h2 {
      color: #263238;
      text-align: center;
      margin-bottom: 30px;
      font-weight: 600;
    }
    .card {
      border-radius: 15px;
      box-shadow: 0 8px 30px rgba(0, 0, 0, 0.05);
      margin-bottom: 20px;
      animation: fadeIn 0.8s ease-in;
    }
    .form-label {
      color: #455a64;
      font-weight: 500;
    }
    .form-control, .form-select {
      border-radius: 10px;
      padding: 10px;
    }
    .btn-filter {
      background: #0288d1;
      border: none;
      padding: 10px;
      border-radius: 10px;
      transition: background 0.3s, transform 0.3s;
    }
    .btn-filter:hover {
      background: #0277bd;
      transform: translateY(-2px);
    }
    .btn-action {
      padding: 10px 20px;
      border-radius: 10px;
      transition: background 0.3s, transform 0.3s;
    }
    .btn-action:hover {
      transform: translateY(-2px);
    }
    .table {
      border-radius: 10px;
      overflow: hidden;
    }
    th, td {
      vertical-align: middle;
    }
    .visual-icon {
      position: fixed;
      bottom: 20px;
      right: 20px;
      cursor: pointer;
      background: #0288d1;
      border-radius: 50%;
      width: 60px;
      height: 60px;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
      transition: background 0.3s, transform 0.3s;
    }
    .visual-icon:hover {
      background: #0277bd;
      transform: scale(1.1);
    }
    .visual-icon img {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      object-fit: cover;
    }
    .bulk-action-btn {
      margin-right: 10px;
      margin-bottom: 10px;
      padding: 10px 15px;
      font-size: 0.9rem;
    }
    /* Removed .btn-download-selected styling as we use btn-success now */
    .btn-download-reject {
      background: #dc3545;
      border: none;
    }
    .btn-download-reject:hover {
      background: #c82333;
    }
    .btn-send-selected {
      background: #17a2b8;
      border: none;
    }
    .btn-send-selected:hover {
      background: #138496;
    }
    .btn-send-reject {
      background: #6c757d;
      border: none;
    }
    .btn-send-reject:hover {
      background: #5a6268;
    }
    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>Interview Results Dashboard</h2>
    <div class="card">
      <div class="card-body">
        <form method="get" action="/admin/dashboard">
          <div class="row g-3">
            <!-- Interview Level Filter -->
            <div class="col-md-2">
              <label for="level" class="form-label">Interview Level</label>
              <select class="form-select" id="level" name="level">
                <option value="">-- Select Level --</option>
                <option value="1" {% if level == '1' %}selected{% endif %}>Level 1 (Aptitude)</option>
                <option value="2" {% if level == '2' %}selected{% endif %}>Level 2 (Interview)</option>
                <option value="3" {% if level == '3' %}selected{% endif %}>Level 3 (HR Interview)</option>
              </select>
            </div>
            <!-- From Date Filter -->
            <div class="col-md-2">
              <label for="from_date" class="form-label">From Date</label>
              <input type="date" class="form-control" id="from_date" name="from_date" value="{{ from_date }}">
            </div>
            <!-- To Date Filter -->
            <div class="col-md-2">
              <label for="to_date" class="form-label">To Date</label>
              <input type="date" class="form-control" id="to_date" name="to_date" value="{{ to_date }}">
            </div>
            <!-- Min Score Filter -->
            <div class="col-md-2">
              <label for="min_mark" class="form-label">Min Score</label>
              <input type="number" class="form-control" id="min_mark" name="min_mark" step="0.01" value="{{ min_mark }}">
            </div>
            <!-- Max Score Filter -->
            <div class="col-md-2">
              <label for="max_mark" class="form-label">Max Score</label>
              <input type="number" class="form-control" id="max_mark" name="max_mark" step="0.01" value="{{ max_mark }}">
            </div>
            <!-- Top N Filter -->
            <div class="col-md-2">
              <label for="top_number" class="form-label">Top N</label>
              <input type="number" class="form-control" id="top_number" name="top_number" value="{{ top_number }}">
            </div>
            <!-- job title Filter (only for Level 2) -->
            {% if job_roles|length > 0 %}
            <div class="col-md-2">
              <label for="job_role" class="form-label">job title</label>
              <select class="form-select" id="job_role" name="job_role">
                <option value="">-- Select job title --</option>
                {% for role in job_roles %}
                <option value="{{ role }}" {% if job_role == role %}selected{% endif %}>{{ role }}</option>
                {% endfor %}
              </select>
            </div>
            {% endif %}
            <div class="col-md-2 d-flex align-items-end">
              <button type="submit" class="btn btn-filter w-100">Apply Filters</button>
            </div>
          </div>
        </form>
        {% if results %}
        <table class="table table-striped mt-4">
          <thead class="table-dark">
            <tr>
              <th>Select</th>
              <th>Name</th>
              <th>Email</th>
              <th>Date</th>
              <th>Score</th>
              {% if level == '2' %}<th>job title</th>{% endif %}
              <th>Responses</th>
            </tr>
          </thead>
          <tbody>
            {% for result in results %}
            <tr>
              <td><input type="checkbox" name="selected_emails" value="{{ result['candidate email'] }}"></td>
              <td>{{ result['candidate name'] }}</td>
              <td>{{ result['candidate email'] }}</td>
              <td>{{ result['interview date'] }}</td>
              <td>{{ result['total score'] }}</td>
              {% if level == '2' %}<td>{{ result['job title'] }}</td>{% endif %}
              <td>
                {% if level == '1' %}
                  No responses available
                {% else %}
                  <a href="/admin/view_responses?email={{ result['candidate email'] }}&level={{ level }}" class="btn btn-info btn-sm">View</a>
                {% endif %}
              </td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
        <div class="bulk-actions mt-4 text-center">
          <!-- Updated button class to btn-success -->
          <button class="btn btn-success btn-action bulk-action-btn" onclick="bulkAction('download_selected')">Download Selected</button>
          <button class="btn btn-danger btn-action bulk-action-btn btn-download-reject" onclick="bulkAction('download_reject')">Download Reject</button>
          <button class="btn btn-success btn-action bulk-action-btn btn-send-selected" onclick="bulkAction('send_selected_mail')">Send Selected Mail</button>
          <button class="btn btn-warning btn-action bulk-action-btn btn-send-reject" onclick="bulkAction('send_reject_mail')">Send Reject Mail</button>
        </div>
        {% else %}
        <p class="text-center mt-4">No results available.</p>
        {% endif %}
      </div>
    </div>
    <a href="/admin/visual_dashboard" class="visual-icon">
      <img src="/static/images/chart-icon.png" alt="Visual Dashboard">
    </a>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
  <script>
    function bulkAction(action) {
      const selectedEmails = Array.from(document.querySelectorAll('input[name="selected_emails"]:checked')).map(cb => cb.value).join(',');
      if (!selectedEmails) {
        alert('Please select at least one candidate.');
        return;
      }
      const form = document.createElement('form');
      form.method = 'POST';
      form.action = '/admin/bulk_action';
      const actionInput = document.createElement('input');
      actionInput.type = 'hidden';
      actionInput.name = 'action';
      actionInput.value = action;
      form.appendChild(actionInput);
      const emailsInput = document.createElement('input');
      emailsInput.type = 'hidden';
      emailsInput.name = 'selected_emails';
      emailsInput.value = selectedEmails;
      form.appendChild(emailsInput);
      const level = document.getElementById('level').value;
      if (level) {
        const levelInput = document.createElement('input');
        levelInput.type = 'hidden';
        levelInput.name = 'level';
        levelInput.value = level;
        form.appendChild(levelInput);
      }
      const from_date = document.getElementById('from_date').value;
      if (from_date) {
        const fromDateInput = document.createElement('input');
        fromDateInput.type = 'hidden';
        fromDateInput.name = 'from_date';
        fromDateInput.value = from_date;
        form.appendChild(fromDateInput);
      }
      const to_date = document.getElementById('to_date').value;
      if (to_date) {
        const toDateInput = document.createElement('input');
        toDateInput.type = 'hidden';
        toDateInput.name = 'to_date';
        toDateInput.value = to_date;
        form.appendChild(toDateInput);
      }
      const min_mark = document.getElementById('min_mark').value;
      if (min_mark) {
        const minMarkInput = document.createElement('input');
        minMarkInput.type = 'hidden';
        minMarkInput.name = 'min_mark';
        minMarkInput.value = min_mark;
        form.appendChild(minMarkInput);
      }
      const max_mark = document.getElementById('max_mark').value;
      if (max_mark) {
        const maxMarkInput = document.createElement('input');
        maxMarkInput.type = 'hidden';
        maxMarkInput.name = 'max_mark';
        maxMarkInput.value = max_mark;
        form.appendChild(maxMarkInput);
      }
      const top_number = document.getElementById('top_number').value;
      if (top_number) {
        const topNumberInput = document.createElement('input');
        topNumberInput.type = 'hidden';
        topNumberInput.name = 'top_number';
        topNumberInput.value = top_number;
        form.appendChild(topNumberInput);
      }
      document.body.appendChild(form);
      form.submit();
    }
  </script>
</body>
</html>
""",
    "visual_dashboard.html": """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Visual Dashboard</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    body {
      background: #f4f6f9;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      min-height: 100vh;
      padding: 20px;
    }
    .container {
      max-width: 1400px;
      margin: 0 auto;
    }
    h2 {
      color: #263238;
      text-align: center;
      margin-bottom: 30px;
      font-weight: 600;
    }
    .card {
      border-radius: 15px;
      box-shadow: 0 8px 30px rgba(0, 0, 0, 0.05);
      margin-bottom: 20px;
    }
    .form-select, .form-control {
      border-radius: 10px;
      padding: 10px;
    }
    .chart-container {
      margin-bottom: 30px;
    }
    .table-container {
      max-height: 400px;
      overflow-y: auto;
      border-radius: 10px;
    }
    .table {
      margin-bottom: 0;
    }
    .high-score {
      background-color: #d4edda !important;
    }
    .low-score {
      background-color: #f8d7da !important;
    }
    .chart-col {
      min-height: 400px;
    }
    .back-button {
      margin: 20px 0;
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>Interview Visual Dashboard</h2>

    <!-- Filters -->
    <div class="card mb-4">
      <div class="card-body">
        <form method="get" action="/admin/visual_dashboard">
          <div class="row g-3">
            <div class="col-md-3">
              <label for="result_type" class="form-label">Select Results</label>
              <select class="form-select" id="result_type" name="result_type" onchange="this.form.submit()">
                <option value="interview" {% if result_type == "interview" %}selected{% endif %}>Interview Results</option>
                <option value="hr" {% if result_type == "hr" %}selected{% endif %}>HR Results</option>
                <option value="aptitude" {% if result_type == "aptitude" %}selected{% endif %}>Aptitude Results</option>
              </select>
            </div>
            <div class="col-md-3">
              <label for="from_interview_date" class="form-label">From Interview Date</label>
              <input type="date" class="form-control" id="from_interview_date" name="from_interview_date" 
                     value="{{ from_interview_date or '' }}" onchange="this.form.submit()">
            </div>
            <div class="col-md-3">
              <label for="to_interview_date" class="form-label">To Interview Date (Optional)</label>
              <input type="date" class="form-control" id="to_interview_date" name="to_interview_date" 
                     value="{{ to_interview_date or '' }}" onchange="this.form.submit()">
            </div>
            <div class="col-md-3">
              <label for="job_role" class="form-label">job title</label>
              <select class="form-select" id="job_role" name="job_role" onchange="this.form.submit()">
                <option value="">All Roles</option>
                {% for role in job_roles %}
                  <option value="{{ role }}" {% if role == request.query_params.get('job_role') %}selected{% endif %}>{{ role }}</option>
                {% endfor %}
              </select>
            </div>
          </div>
        </form>
      </div>
    </div>

    <!-- Cards for Metrics -->
    <div class="row">
      <div class="col-md-4">
        <div class="card">
          <div class="card-body text-center">
            <h5 class="card-title">Total Candidates</h5>
            <p class="card-text">{{ total_candidates }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card">
          <div class="card-body text-center">
            <h5 class="card-title">Average Score</h5>
            <p class="card-text">{{ average_score }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card">
          <div class="card-body text-center">
            <h5 class="card-title">Answered All 5 Questions</h5>
            <p class="card-text">{{ all_questions_answered }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Visualizations -->
    <div class="row chart-container">
      <div class="col-md-4 chart-col">
        <div id="bar-chart"></div>
      </div>
      <div class="col-md-4 chart-col">
        <div id="top-5-chart"></div>
      </div>
      <div class="col-md-4 chart-col">
        {% if pie_fig and result_type == "interview" %}
          <div id="pie-chart"></div>
        {% else %}
          <div>No job title Data Available</div>
        {% endif %}
      </div>
    </div>
    <div class="row chart-container">
      <div class="col-md-12">
        <div id="line-chart"></div>
      </div>
    </div>

    <!-- Tables -->
    <div class="row">
      <div class="col-md-8">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">Candidate Details</h5>
            <div class="table-container">
              <table class="table table-striped">
                <thead>
                  <tr>
                    <th>Candidate Name</th>
                    <th>Email</th>
                    <th>Interview Date</th>
                    <th>Total Score</th>
                    {% if result_type == "interview" %}
                      <th>job title</th>
                    {% endif %}
                  </tr>
                </thead>
                <tbody>
                  {% for row in table_data %}
                    <tr>
                      <td>{{ row['candidate name'] }}</td>
                      <td>{{ row['candidate email'] }}</td>
                      <td>{{ row['interview date'] }}</td>
                      <td class="{% if row['total score'] >= 80 %}high-score{% elif row['total score'] <= 20 %}low-score{% endif %}">
                        {{ row['total score'] }}
                      </td>
                      {% if result_type == "interview" %}
                        <td>{{ row['job title'] }}</td>
                      {% endif %}
                    </tr>
                  {% endfor %}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        {% if result_type == "interview" and all_questions_candidates %}
          <div class="card">
            <div class="card-body">
              <h5 class="card-title">Candidates Answered All 5 Questions</h5>
              <div class="table-container">
                <table class="table table-striped">
                  <thead>
                    <tr>
                      <th>Candidate Name</th>
                    </tr>
                  </thead>
                  <tbody>
                    {% for row in all_questions_candidates %}
                      <tr>
                        <td>{{ row['candidate name'] }}</td>
                      </tr>
                    {% endfor %}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        {% endif %}
      </div>
    </div>

    <!-- Back Button -->
    <div class="row">
      <div class="col-md-12 text-center">
        <button class="btn btn-primary back-button" onclick="history.back()">Back</button>
      </div>
    </div>
  </div>

  <script>
    // Ensure Plotly renders correctly
    try {
      Plotly.newPlot('bar-chart', JSON.parse('{{ bar_fig | safe }}'));
      Plotly.newPlot('top-5-chart', JSON.parse('{{ top_5_fig | safe }}'));
      Plotly.newPlot('line-chart', JSON.parse('{{ line_fig | safe }}'));
      {% if pie_fig and result_type == "interview" %}
        Plotly.newPlot('pie-chart', JSON.parse('{{ pie_fig | safe }}'));
      {% endif %}
    } catch (e) {
      console.error('Error rendering Plotly charts:', e);
    }
  </script>
</body>
</html>
""",
    "admin_view_responses.html": """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>View Responses</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {
      background: #f4f6f9;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      min-height: 100vh;
      padding: 20px;
    }
    .container {
      max-width: 1000px;
      margin: 0 auto;
    }
    h2 {
      color: #263238;
      margin-bottom: 30px;
      font-weight: 600;
    }
    .card {
      border-radius: 15px;
      box-shadow: 0 8px 30px rgba(0, 0, 0, 0.05);
      animation: fadeIn 0.8s ease-in;
    }
    .table {
      border-radius: 10px;
      overflow: hidden;
    }
    th, td {
      vertical-align: middle;
    }
    .btn-back {
      background: #0288d1;
      border: none;
      padding: 10px 20px;
      border-radius: 10px;
      transition: background 0.3s, transform 0.3s;
    }
    .btn-back:hover {
      background: #0277bd;
      transform: translateY(-2px);
    }
    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }
  </style>
</head>
<body>
  <div class="container">
    <h2 class="text-center">Responses for {{ candidate_email }}</h2>
    <div class="card">
      <div class="card-body">
        <table class="table table-hover">
          <thead class="table-light">
            <tr>
              <th>Question</th>
              <th>Candidate Answer</th>
              {% if level == "2" %}
              <th>Correct Answer</th>
              {% endif %}
              <th>Score</th>
            </tr>
          </thead>
          <tbody>
            {% for qa in qas %}
            <tr>
              <td>{{ qa.question }}</td>
              <td>{{ qa.candidate_answer }}</td>
              {% if level == "2" %}
              <td>{{ qa.correct_answer if qa.correct_answer else "N/A" }}</td>
              {% endif %}
              <td>{{ qa.score }}</td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
    </div>
    <div class="text-center mt-4">
      <a href="/admin/dashboard" class="btn btn-back">Back to Dashboard</a>
    </div>
  </div>
</body>
</html>
""",
    "candidate_submit_name.html": """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Submit Name</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {
      background: linear-gradient(to right, #e1f5fe, #b3e5fc);
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .submit-container {
      background: #fff;
      padding: 40px;
      border-radius: 15px;
      box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
      max-width: 450px;
      width: 100%;
      animation: slideUp 0.8s ease-out;
    }
    h2 {
      color: #0277bd;
      margin-bottom: 30px;
      font-weight: 600;
    }
    .form-label {
      color: #455a64;
      font-weight: 500;
    }
    .form-control {
      border-radius: 10px;
      padding: 12px;
      transition: border-color 0.3s;
    }
    .form-control:focus {
      border-color: #0288d1;
      box-shadow: 0 0 5px rgba(2, 136, 209, 0.5);
    }
    .btn-submit {
      background: #0288d1;
      border: none;
      padding: 12px;
      border-radius: 10px;
      font-size: 1.1rem;
      transition: background 0.3s, transform 0.3s;
    }
    .btn-submit:hover {
      background: #0277bd;
      transform: translateY(-2px);
    }
    @keyframes slideUp {
      from { opacity: 0; transform: translateY(50px); }
      to { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body>
  <div class="submit-container">
    <h2 class="text-center">Submit Your Name</h2>
    <form action="/candidate/submit_name" method="post">
      <div class="mb-4">
        <label for="candidate_name" class="form-label">Your Name</label>
        <input type="text" class="form-control" id="candidate_name" name="candidate_name" placeholder="Enter your name" required>
      </div>
      <input type="hidden" name="email" value="{{ email }}">
      <button type="submit" class="btn btn-submit w-100">Submit</button>
    </form>
  </div>
</body>
</html>
"""
}

for filename, content in templates_data.items():
    filepath = os.path.join(TEMPLATE_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content.strip())

templates = Jinja2Templates(directory=TEMPLATE_DIR)

# Global Variables & Databases
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

candidate_db = {}
candidate_warnings = {}
candidate_status = {}

admin_credentials = {"admin": "admin123"}  # Default admin credentials retained
RESULTS_FILE = "interview_results.xlsx"
APTITUDE_RESULTS_FILE = "aptitude_results.xlsx"
HR_RESULTS_FILE = "hr_result.xlsx"

# Mobile Detection Model Initialization
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
mobile_detection_model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=False)
class DummyDataset:
    classes = ["mobile"]
dataset = DummyDataset()
num_classes = len(dataset.classes) + 1
in_features = mobile_detection_model.roi_heads.box_predictor.cls_score.in_features
mobile_detection_model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
mobile_detection_model.load_state_dict(torch.load("mobile_detection_model.pth", map_location=device))
mobile_detection_model.to(device)
mobile_detection_model.eval()

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# Person Detection Model Initialization
yolo_person_model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
if torch.cuda.is_available():
    yolo_person_model.to(device)
yolo_person_conf_threshold = 0.3

# Detection Helpers
def sync_detect_person(small_frame):
    rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    results_person = yolo_person_model(rgb_frame)
    detections = results_person.xyxy[0].cpu().numpy()
    person_detections = []
    for detection in detections:
        x1, y1, x2, y2, conf, cls = detection
        if conf >= yolo_person_conf_threshold and int(cls) == 0:
            person_detections.append([x1, y1, x2, y2])
    return person_detections

def sync_detect_mobile(small_frame, img_tensor):
    mobile_conf_threshold = 0.3
    with torch.no_grad():
        predictions = mobile_detection_model(img_tensor)
    boxes = predictions[0]['boxes'].cpu().numpy()
    scores = predictions[0]['scores'].cpu().numpy()
    labels = predictions[0]['labels'].cpu().numpy()
    keep = (scores >= mobile_conf_threshold) & (labels > 0)
    boxes = boxes[keep]
    scores = scores[keep]
    labels = labels[keep] - 1
    mobile_detected = False
    mobile_boxes = []
    for box, score, label in zip(boxes, scores, labels):
        if dataset.classes[label] == "mobile":
            mobile_detected = True
            mobile_boxes.append(box)
    return mobile_detected, mobile_boxes

async def detect_person(small_frame):
    return await asyncio.to_thread(sync_detect_person, small_frame)

async def detect_mobile(small_frame, img_tensor):
    return await asyncio.to_thread(sync_detect_mobile, small_frame, img_tensor)

async def combined_detection(small_frame, img_tensor):
    person_future = detect_person(small_frame)
    mobile_future = detect_mobile(small_frame, img_tensor)
    person_detections, mobile_result = await asyncio.gather(person_future, mobile_future)
    mobile_detected, mobile_boxes = mobile_result
    return person_detections, mobile_detected, mobile_boxes

# Q&A Parsing and Generation
def parse_context(context):
    pattern = r"Q\d+:\s*(.*?)\nA\d+:\s*(.*?)(?=\nQ\d+:|$)"
    matches = re.findall(pattern, context, re.DOTALL)
    qa_pairs = []
    for question, answer in matches:
        qa_pairs.append({'question': question.strip(), 'answer': answer.strip()})
    return qa_pairs

def generate_questions(job_description):
    prompt = f"Generate 5 interview questions and answers for the following job description:\n\n{job_description}\n\nFormat the response as:\nQ1: [question]\nA1: [answer]\nQ2: [question]\nA2: [answer]\n...\nQ5: [question]\nA5: [answer]"
    response = ollama.generate(model="llama3.2:1b", prompt=prompt)
    for key in ['text', 'generated_text', 'response', 'completion']:
        if key in response:
            return response[key]
    raise ValueError("Cannot find generated text in response")

GENERATED_QUESTIONS_DIR = "generated_questions"

def generate_qas_using_llama2(job_description):
    hash_object = hashlib.sha256(job_description.encode())
    hash_hex = hash_object.hexdigest()
    filename = os.path.join(GENERATED_QUESTIONS_DIR, f"{hash_hex}.json")
    
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            qa_pairs = json.load(f)
    else:
        generated_text = generate_questions(job_description)
        qa_pairs = parse_context(generated_text)
        os.makedirs(GENERATED_QUESTIONS_DIR, exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(qa_pairs, f, ensure_ascii=False, indent=4)
    
    if len(qa_pairs) < 5:
        raise HTTPException(status_code=500, detail="Not enough questions generated")
    selected_qas = random.sample(qa_pairs, 5)
    return selected_qas

def append_candidate_aptitude_result(candidate_email, candidate_name, interview_datetime, total_score):
    row = {
        "candidate name": candidate_name,
        "candidate email": candidate_email,
        "interview date": interview_datetime if interview_datetime else "",
        "job title": candidate_db[candidate_email]["job_title"],  # Added
        "total score": total_score,
        "Interview Level": "APTITUDE"
    }
    new_row_df = pd.DataFrame([row])
    if os.path.exists(APTITUDE_RESULTS_FILE):
        df = pd.read_excel(APTITUDE_RESULTS_FILE)
        df = pd.concat([df, new_row_df], ignore_index=True)
    else:
        df = new_row_df
    df.to_excel(APTITUDE_RESULTS_FILE, index=False)

def append_candidate_result(candidate_email, candidate_name, total_score, evaluations, interview_datetime=None):
    row = {
        "candidate name": candidate_name,
        "candidate email": candidate_email,
        "interview date": interview_datetime if interview_datetime else "",
        "job title": candidate_db[candidate_email]["job_title"],  # Added
        "total score": total_score,
        "Interview Level": "INTERVIEW",
        "Job Description": candidate_db[candidate_email]["job_description"]
    }
    for i, eval_ in enumerate(evaluations, start=1):
        row[f"question {i}"] = eval_.get("question", "")
        row[f"candidate answer {i}"] = eval_.get("candidate_answer", "")
        row[f"correct answer {i}"] = eval_.get("correct_answer", "")
        row[f"score {i}"] = eval_.get("score", "")
    new_row_df = pd.DataFrame([row])
    if os.path.exists(RESULTS_FILE):
        df = pd.read_excel(RESULTS_FILE)
        df = pd.concat([df, new_row_df], ignore_index=True)
    else:
        df = new_row_df
    df.to_excel(RESULTS_FILE, index=False)

def append_hr_candidate_result(candidate_email, candidate_name, total_score, evaluations, interview_datetime=None):
    row = {
        "candidate name": candidate_name,
        "candidate email": candidate_email,
        "interview date": interview_datetime if interview_datetime else "",
        "job title": candidate_db[candidate_email]["job_title"],  # Added
        "total score": total_score,
        "Interview Level": "HR_INTERVIEW"
    }
    for i, eval_ in enumerate(evaluations, start=1):
        row[f"question {i}"] = eval_.get("question", "")
        row[f"candidate answer {i}"] = eval_.get("candidate_answer", "")
        row[f"score {i}"] = eval_.get("score", "")
    new_row_df = pd.DataFrame([row])
    if os.path.exists(HR_RESULTS_FILE):
        df = pd.read_excel(HR_RESULTS_FILE)
        df = pd.concat([df, new_row_df], ignore_index=True)
    else:
        df = new_row_df
    df.to_excel(HR_RESULTS_FILE, index=False)

# Pydantic Models
class AdminLogin(BaseModel):
    username: str
    password: str

class ScheduleInterview(BaseModel):
    candidate_emails: str
    interview_datetime: str
    job_description: str
    level: str

class CandidateLogin(BaseModel):
    email: str
    password: str

class InterviewSubmission(BaseModel):
    email: str
    responses: list

class AnswerSubmission(BaseModel):
    answers: Dict[int, str]

class AptitudeEvaluation(BaseModel):
    email: str
    answers: Dict[str, str]

# Endpoint: Upload Recording
@app.post("/interview/upload_recording")
async def upload_recording(email: str = Form(...), file: UploadFile = File(...)):
    video_folder = "interview_video"
    os.makedirs(video_folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{email}_{timestamp}.webm"
    filepath = os.path.join(video_folder, filename)
    contents = await file.read()
    with open(filepath, "wb") as f:
        f.write(contents)
    return JSONResponse(content={"message": f"Recording saved as {filename}"})

# Routes: UI Endpoints
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/admin/login", response_class=HTMLResponse)
def admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request, "email": ""})

@app.post("/admin/login", response_class=HTMLResponse)
def admin_login(request: Request, email: str = Form(...), password: str = Form(...)):
    message = ""
    message_type = ""
    if email == "admin" and password == admin_credentials["admin"]:
        return RedirectResponse(url="/admin/panel", status_code=302)
    else:
        admins = load_registered_admins()
        for admin in admins:
            if admin["email"] == email and admin["password"] == password:
                return RedirectResponse(url="/admin/panel", status_code=302)
        message = "Invalid admin credentials"
        message_type = "error"
    return templates.TemplateResponse(
        "admin_login.html",
        {"request": request, "message": message, "message_type": message_type, "email": email}
    )

@app.get("/admin/register", response_class=HTMLResponse)
def admin_register_page(request: Request):
    return templates.TemplateResponse("admin_register.html", {"request": request, "name": "", "email": ""})

@app.post("/admin/register", response_class=HTMLResponse)
def admin_register(request: Request, name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    message = ""
    message_type = ""
    if not email.endswith("@vdartinc.com"):
        message = "Email must end with @vdartinc.com"
        message_type = "error"
    else:
        admins = load_registered_admins()
        for admin in admins:
            if admin["email"] == email:
                message = "Email already registered"
                message_type = "error"
                break
        else:
            new_admin = {"name": name, "email": email, "password": password}
            admins.append(new_admin)
            save_registered_admins(admins)
            message = "Registration successful. You can now log in."
            message_type = "success"
    return templates.TemplateResponse(
        "admin_register.html",
        {"request": request, "message": message, "message_type": message_type, "name": name, "email": email}
    )

@app.get("/admin/forgot_password", response_class=HTMLResponse)
def forgot_password_page(request: Request):
    return templates.TemplateResponse("admin_forgot_password.html", {"request": request, "email": ""})

@app.post("/admin/forgot_password", response_class=HTMLResponse)
def forgot_password(request: Request, email: str = Form(...)):
    message = ""
    message_type = ""
    if email == "admin":
        message = "Default admin cannot use forgot password"
        message_type = "error"
    else:
        admins = load_registered_admins()
        for admin in admins:
            if admin["email"] == email:
                password_message = f"Your password for the admin account registered with email {email} is: {admin['password']}"
                send_email(email, "Your Password", password_message)
                message = "Password sent successfully to your email."
                message_type = "success"
                break
        else:
            message = "Email not found"
            message_type = "error"
    return templates.TemplateResponse(
        "admin_forgot_password.html",
        {"request": request, "message": message, "message_type": message_type, "email": email}
    )

@app.get("/admin/panel", response_class=HTMLResponse)
def admin_panel(request: Request):
    return templates.TemplateResponse("admin_panel.html", {"request": request})

@app.get("/candidate/login", response_class=HTMLResponse)
def candidate_login_page(request: Request):
    return templates.TemplateResponse("candidate_login.html", {"request": request})

@app.post("/candidate/login")
async def candidate_login(email: str = Form(...), password: str = Form(...)):
    # Validate email and password
    if email not in candidate_db or candidate_db[email]["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Get the scheduled interview time string
    interview_datetime_str = candidate_db[email]["interview_datetime"]
    
    # Parse the datetime string based on its format
    try:
        if 'T' in interview_datetime_str:
            # Format from datetime-local input (e.g., "2023-10-10T10:00")
            scheduled_time = datetime.strptime(interview_datetime_str, "%Y-%m-%dT%H:%M")
        else:
            # Format for level 3 with HR (e.g., "2023-10-10 10:00")
            scheduled_time = datetime.strptime(interview_datetime_str, "%Y-%m-%d %H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid interview datetime format")
    
    # Get current time
    current_time = datetime.now()
    
    # Define the login window
    start_window = scheduled_time - timedelta(minutes=5)
    end_window = scheduled_time + timedelta(minutes=15)
    
    # Check if current time is within the login window
    if not (start_window <= current_time <= end_window):
        raise HTTPException(
            status_code=403,
            detail="Login is only allowed from 5 minutes before to 15 minutes after the scheduled interview time."
        )
    
    # Redirect to the interview UI with email as a query parameter
    return RedirectResponse(url=f"/interview/ui?email={email}", status_code=302)
@app.get("/interview/ui", response_class=HTMLResponse)
def interview_ui(request: Request, email: str):
    if email not in candidate_db:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if candidate_status.get(email) == "terminated":
        return HTMLResponse(content="<h3>Interview terminated due to repeated warnings.</h3>")
    candidate = candidate_db[email]
    if "qas" in candidate:
        return templates.TemplateResponse("interview.html", {"request": request, "qas": candidate["qas"], "email": email})
    elif candidate.get("level") == "1":
        def load_dataset(filepath="Quantitative_Aptitude_Questions.json") -> List[dict]:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)

        def reformat_questions(questions: List[dict]) -> List[dict]:
            reformatted = []
            for q in questions:
                new_q = {}
                new_q["id"] = str(q.get("question_number", q.get("id")))
                new_q["question"] = q.get("question", "")
                options = q.get("options", {})
                if isinstance(options, dict):
                    opt_keys = sorted(options.keys())
                    new_q["options"] = [options[key] for key in opt_keys]
                elif isinstance(options, list):
                    new_q["options"] = options
                else:
                    new_q["options"] = []
                answer = q.get("answer", "")
                if isinstance(answer, dict):
                    new_q["answer"] = answer.get("text", "")
                elif isinstance(answer, str):
                    new_q["answer"] = answer
                else:
                    new_q["answer"] = ""
                reformatted.append(new_q)
            return reformatted

        raw_dataset = load_dataset("Quantitative_Aptitude_Questions.json")
        QUESTION_BANK = reformat_questions(raw_dataset)

        def get_random_questions(n: int = 50) -> List[dict]:
            total = len(QUESTION_BANK)
            selected = random.sample(QUESTION_BANK, min(n, total))
            return selected
        selected_questions = get_random_questions(n=50)
        candidate_db[email]["aptitude_questions"] = selected_questions
        ui_questions = [{"id": q["id"], "question": q["question"], "options": q["options"]} for q in selected_questions]
        return templates.TemplateResponse("aptitude.html", {"request": request, "questions": ui_questions, "email": email})
    elif candidate.get("level") == "3":
        meet_link = "https://meet.google.com/zke-dxnk-miz"
        html_content = f"""
        <html>
          <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Google Meet Interview</title>
            <style>
              body {{ 
                background: linear-gradient(135deg, #e3f2fd, #bbdefb); 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                min-height: 100vh; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
              }}
              .box {{
                background: #fff;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
                text-align: center;
                animation: fadeIn 0.8s ease-in;
              }}
              h2 {{ color: #263238; font-weight: 600; }}
              a {{ color: #1976d2; text-decoration: none; }}
              a:hover {{ text-decoration: underline; }}
              @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
            </style>
          </head>
          <body>
            <div class="box">
              <h2>Please join the interview via Google Meet</h2>
              <p><a href="{meet_link}" target="_blank">{meet_link}</a></p>
            </div>
          </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    else:
        raise HTTPException(status_code=400, detail="Invalid candidate data")

@app.get("/ap1_detect", response_class=HTMLResponse)
def aptitude_ui(request: Request, email: str):
    if email not in candidate_db:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return RedirectResponse(url=f"/interview/ui?email={email}", status_code=302)

# Routes: Admin Endpoints
@app.post("/admin/schedule")
def schedule_interview(
    candidate_emails: str = Form(...),
    interview_datetime: str = Form(None),
    job_description: str = Form(None),
    level: str = Form(...),
    hr_available: str = Form(None),
    hr_emails: str = Form(None),
    viewer_emails: str = Form(None),
    from_time: str = Form(None),
    to_time: str = Form(None),
    hr_date: str = Form(None),
    job_title: str = Form(...)  # Added
):
    def generate_password():
        letters = random.choices(string.ascii_letters, k=4)
        symbol = random.choice("!@#$%^&*")
        numbers = random.choices(string.digits, k=2)
        password_list = letters + [symbol] + numbers
        random.shuffle(password_list)
        print("".join(password_list))
        return "".join(password_list)
    
    emails = [email.strip() for email in candidate_emails.split(",") if email.strip()]
    if not emails:
        raise HTTPException(status_code=400, detail="At least one candidate email is required")
    
    meet_link = "https://meet.google.com/zke-dxnk-miz"
    
    if level in ["1", "2"]:
        if not interview_datetime:
            raise HTTPException(status_code=400, detail="Interview date and time are required")
        if level == "2" and not job_description:
            raise HTTPException(status_code=400, detail="Job description is required for Level 2")
        
        for email in emails:
            random_password = generate_password()
            candidate_db[email] = {
                "password": random_password,
                "interview_datetime": interview_datetime,
                "job_description": job_description if level == "2" else "Not specified",
                "level": level,
                "job_title": job_title  # Added
            }
            if level == "2":
                qas = generate_qas_using_llama2(job_description)
                candidate_db[email]["qas"] = qas
            candidate_status[email] = "active"
            candidate_warnings[email] = 0
            
            subject = "Your Interview Details & Login Link"
            message = (
                f"Dear Candidate,\n\n"
                f"You have been scheduled for an interview.\n"
                f"Interview Date and Time: {interview_datetime}\n"
                f"Job Title: {job_title}\n"  # Added
                f"Job Description: {job_description if level == '2' else 'Not specified'}\n"
                f"Interview Level: {level}\n\n"
                f"Please login at /candidate/login with your email and password: {random_password}\n\n"
                f"Best Regards,\nInterview Team"
            )
            send_email(email, subject, message)
    
    elif level == "3":
        if hr_available == "yes":
            if not all([hr_emails, from_time, to_time, hr_date]):
                raise HTTPException(
                    status_code=400,
                    detail="HR emails, from time, to time, and interview date are required when HR is available"
                )
            
            hr_email_list = [email.strip() for email in hr_emails.split(",") if email.strip()]
            viewer_email_list = (
                [email.strip() for email in viewer_emails.split(",") if email.strip()]
                if viewer_emails else []
            )
            if not hr_email_list:
                raise HTTPException(status_code=400, detail="At least one HR email is required")
            
            timetable_text, timetable = generate_timetable(emails, from_time, to_time, hr_date)
            
            for slot in timetable:
                candidate_email = slot["candidate_email"]
                random_password = generate_password()
                candidate_db[candidate_email] = {
                    "password": random_password,
                    "interview_datetime": f"{slot['date']} {slot['start_time']}",
                    "job_description": job_description or "Google Meet Interview",
                    "level": level,
                    "job_title": job_title  # Added
                }
                candidate_status[candidate_email] = "active"
                candidate_warnings[candidate_email] = 0
                
                subject = "Your Interview Details & Login Link"
                message = (
                    f"Dear Candidate,\n\n"
                    f"You have been scheduled for an interview.\n"
                    f"Interview Date: {slot['date']}\n"
                    f"Time: {slot['start_time']} to {slot['end_time']}\n"
                    f"Job Title: {job_title}\n"  # Added
                    f"Join the Google Meet: {meet_link}\n"
                    f"Please login at /candidate/login with your email and password: {random_password}\n\n"
                    f"Best Regards,\nInterview Team"
                )
                send_email(candidate_email, subject, message)
            
            timetable_subject = "Interview Schedule Timetable"
            timetable_message = (
                f"Dear Team,\n\n"
                f"Please find the interview schedule below:\n\n"
                f"{timetable_text}\n\n"
                f"Job Title: {job_title}\n"  # Added
                f"Join the Google Meet: {meet_link}\n\n"
                f"Best Regards,\nInterview Team"
            )
            for hr_email in hr_email_list:
                send_email(hr_email, timetable_subject, timetable_message)
            for viewer_email in viewer_email_list:
                send_email(viewer_email, timetable_subject, timetable_message)
        
        elif hr_available == "no":
            if not interview_datetime:
                raise HTTPException(status_code=400, detail="Interview date and time are required")
            hr_questions = load_hr_questions()
            if len(hr_questions) < 5:
                raise HTTPException(status_code=500, detail="Not enough HR questions available")
            selected_questions = random.sample(hr_questions, 5)
            
            for email in emails:
                random_password = generate_password()
                candidate_db[email] = {
                    "password": random_password,
                    "interview_datetime": interview_datetime,
                    "level": level,
                    "qas": [{"question": q} for q in selected_questions],
                    "job_title": job_title  # Added
                }
                candidate_status[email] = "active"
                candidate_warnings[email] = 0
                
                subject = "Your Interview Details & Login Link"
                message = (
                    f"Dear Candidate,\n\n"
                    f"You have been scheduled for an automated interview.\n"
                    f"Interview Date and Time: {interview_datetime}\n"
                    f"Job Title: {job_title}\n"  # Added
                    f"Please login at /candidate/login with your email and password: {random_password}\n\n"
                    f"Best Regards,\nInterview Team"
                )
                send_email(email, subject, message)
        
        else:
            raise HTTPException(status_code=400, detail="Invalid hr_available value")
    
    else:
        raise HTTPException(status_code=400, detail="Invalid level")
    
    html_content = f"""
    <html>
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Interview Scheduled</title>
        <style>
          body {{ 
            background: linear-gradient(135deg, #e3f2fd, #bbdefb); 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            min-height: 100vh; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
          }}
          .box {{
            background: #fff;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
            text-align: center;
            animation: fadeIn 0.8s ease-in;
          }}
          h2 {{ color: #263238; font-weight: 600; }}
          @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
        </style>
      </head>
      <body>
        <div class="box">
          <h2>Interview scheduled for: {', '.join(emails)}</h2>
        </div>
      </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/admin/dashboard", response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    level: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    min_mark: Optional[float] = None,
    max_mark: Optional[float] = None,
    top_number: Optional[int] = None,
    job_role: Optional[str] = None
):
    # Determine the appropriate results file based on level
    file_to_use = APTITUDE_RESULTS_FILE if level == "1" else HR_RESULTS_FILE if level == "3" else RESULTS_FILE
    
    # Load the results file
    if os.path.exists(file_to_use):
        df = pd.read_excel(file_to_use)
        if level == "1":
            df = df.rename(columns={
                "Name": "candidate name",
                "Mail": "candidate email",
                "Interview Date": "interview date",
                "Score": "total score"
            })
    else:
        df = pd.DataFrame()
    
    # Convert 'job title' column to string to handle mixed types
    if not df.empty and "job title" in df.columns:
        df["job title"] = df["job title"].astype(str)
    
    # Extract unique job titles for the dropdown (only for interview_results.xlsx)
    job_roles = []
    if file_to_use == RESULTS_FILE and not df.empty and "job title" in df.columns:
        job_roles = sorted(df["job title"].dropna().unique().tolist())
    
    # Apply filters
    filtered_df = df.copy()
    if not filtered_df.empty:
        # Filter by from_date
        if from_date:
            filtered_df = filtered_df[
                filtered_df["interview date"].apply(
                    lambda d: pd.to_datetime(d, errors="coerce") >= pd.to_datetime(from_date)
                )
            ]
        # Filter by to_date
        if to_date:
            filtered_df = filtered_df[
                filtered_df["interview date"].apply(
                    lambda d: pd.to_datetime(d, errors="coerce") <= pd.to_datetime(to_date)
                )
            ]
        # Filter by min_mark
        if min_mark is not None:
            filtered_df = filtered_df[filtered_df["total score"] >= min_mark]
        # Filter by max_mark
        if max_mark is not None:
            filtered_df = filtered_df[filtered_df["total score"] <= max_mark]
        # Filter by job_role
        if job_role and "job title" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["job title"] == job_role]
        # Apply top_number (sort by total score and take top N)
        if top_number is not None:
            filtered_df = filtered_df.sort_values(by="total score", ascending=False).head(top_number)
        # Format interview date for display
        filtered_df['interview date'] = pd.to_datetime(
            filtered_df['interview date'], errors='coerce'
        ).dt.date
    
    # Convert filtered dataframe to list of records for template
    results = filtered_df.to_dict(orient="records")
    
    # Pass all parameters to the template for form persistence
    return templates.TemplateResponse(
        "admin_dashboard.html",
        {
            "request": request,
            "results": results,
            "level": level if level else "",
            "job_roles": job_roles,
            "from_date": from_date or "",
            "to_date": to_date or "",
            "min_mark": min_mark if min_mark is not None else "",
            "max_mark": max_mark if max_mark is not None else "",
            "top_number": top_number if top_number is not None else "",
            "job_role": job_role or ""
        }
    )

@app.get("/admin/visual_dashboard", response_class=HTMLResponse)
def visual_dashboard(
    request: Request,
    from_interview_date: Optional[str] = Query(None),
    to_interview_date: Optional[str] = Query(None),
    job_role: Optional[str] = Query(None),
    result_type: Optional[str] = Query(None)
):
    # Determine which Excel file to load based on result_type
    if result_type == "aptitude":
        df = pd.read_excel(APTITUDE_RESULTS_FILE) if os.path.exists(APTITUDE_RESULTS_FILE) else pd.DataFrame()
        if not df.empty:
            df = df.rename(columns={
                "Name": "candidate name",
                "Mail": "candidate email",
                "Interview Date": "interview date",
                "Score": "total score"
            })
    elif result_type == "hr":
        df = pd.read_excel(HR_RESULTS_FILE) if os.path.exists(HR_RESULTS_FILE) else pd.DataFrame()
    else:  # Default to "interview"
        df = pd.read_excel(RESULTS_FILE) if os.path.exists(RESULTS_FILE) else pd.DataFrame()
        result_type = "interview"  # Set default

    # Convert "interview date" to date objects (without time)
    if not df.empty and "interview date" in df.columns:
        df["interview date"] = pd.to_datetime(df["interview date"], errors="coerce").dt.date

    # Get unique job titles for dropdown
    job_roles = df["job title"].unique().tolist() if not df.empty and "job title" in df.columns else []

    # Apply filters
    filtered_df = df.copy()
    if from_interview_date and "interview date" in filtered_df.columns:
        try:
            from_date = dt.strptime(from_interview_date, "%Y-%m-%d").date()
            to_date = dt.strptime(to_interview_date, "%Y-%m-%d").date() if to_interview_date else from_date
            if to_date < from_date:
                to_date = from_date  # Ensure to_date is not before from_date
            filtered_df = filtered_df[
                (filtered_df["interview date"] >= from_date) & 
                (filtered_df["interview date"] <= to_date)
            ]
        except ValueError:
            pass  # Ignore invalid date formats
    if job_role and "job title" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["job title"] == job_role]

    # Compute card visual metrics
    total_candidates = filtered_df["candidate email"].nunique() if not filtered_df.empty else 0
    average_score = round(filtered_df["total score"].mean(), 2) if not filtered_df.empty else 0

    # Compute candidates who answered all 5 questions (for interview_results)
    all_questions_answered = 0
    all_questions_candidates = []
    if result_type == "interview" and not filtered_df.empty:
        answer_columns = [f"candidate answer {i}" for i in range(1, 6)]
        if all(col in filtered_df.columns for col in answer_columns):
            all_questions_mask = filtered_df[answer_columns].notnull().all(axis=1)
            all_questions_answered = all_questions_mask.sum()
            all_questions_candidates = filtered_df[all_questions_mask][["candidate name"]].to_dict(orient="records")

    # Prepare visualizations
    if not filtered_df.empty:
        # Bar Chart: Number of candidates by interview date
        if "interview date" in filtered_df.columns:
            candidate_count_by_date = filtered_df.groupby("interview date")["candidate email"].nunique().reset_index()
            candidate_count_by_date.columns = ["interview date", "candidate count"]
            bar_fig = px.bar(
                candidate_count_by_date,
                x="interview date",
                y="candidate count",
                title="Number of Candidates by Interview Date",
                labels={"interview date": "Interview Date", "candidate count": "Number of Candidates"}
            )
            bar_fig.update_xaxes(tickformat="%Y-%m-%d")
        else:
            bar_fig = px.bar(title="No Date Data Available")

        # Bar Chart: Top 5 candidates by total score
        if "candidate name" in filtered_df.columns and "total score" in filtered_df.columns:
            top_5_df = filtered_df.sort_values("total score", ascending=False).head(5)
            top_5_fig = px.bar(
                top_5_df,
                x="candidate name",
                y="total score",
                title="Top 5 Candidates by Total Score",
                labels={"candidate name": "Candidate Name", "total score": "Total Score"}
            )
        else:
            top_5_fig = px.bar(title="No Candidate Data Available")

        # Line Chart: Average scores over time
        if "interview date" in filtered_df.columns and "total score" in filtered_df.columns:
            scores_over_time = filtered_df.groupby("interview date")["total score"].mean().reset_index()
            line_fig = px.line(
                scores_over_time,
                x="interview date",
                y="total score",
                title="Average Total Score Over Time",
                labels={"interview date": "Interview Date", "total score": "Average Total Score"}
            )
            line_fig.update_xaxes(tickformat="%Y-%m-%d")
        else:
            line_fig = px.line(title="No Date Data Available")

        # Pie Chart: Distribution of job titles (only for interview_results)
        if result_type == "interview" and "job title" in filtered_df.columns:
            job_role_dist = filtered_df["job title"].value_counts().reset_index()
            job_role_dist.columns = ["job title", "count"]
            pie_fig = px.pie(
                job_role_dist,
                values="count",
                names="job title",
                title="Distribution of job titles"
            )
        else:
            pie_fig = None

        # Table data for candidate details, sorted by total score descending
        table_columns = ["candidate name", "candidate email", "interview date", "total score"]
        if result_type == "interview":
            table_columns.append("job title")
        if all(col in filtered_df.columns for col in table_columns):
            table_data = filtered_df.sort_values("total score", ascending=False)[table_columns].to_dict(orient="records")
        else:
            table_data = []
    else:
        # Placeholder figures
        bar_fig = px.bar(title="No Data Available")
        top_5_fig = px.bar(title="No Candidate Data Available")
        line_fig = px.line(title="No Date Data Available")
        pie_fig = None
        table_data = []

    # Convert Plotly figures to JSON
    bar_fig_json = json.dumps(bar_fig, cls=plotly.utils.PlotlyJSONEncoder)
    top_5_fig_json = json.dumps(top_5_fig, cls=plotly.utils.PlotlyJSONEncoder)
    line_fig_json = json.dumps(line_fig, cls=plotly.utils.PlotlyJSONEncoder)
    pie_fig_json = json.dumps(pie_fig, cls=plotly.utils.PlotlyJSONEncoder) if pie_fig else None

    # Render the template
    return templates.TemplateResponse("visual_dashboard.html", {
        "request": request,
        "total_candidates": total_candidates,
        "average_score": average_score,
        "all_questions_answered": all_questions_answered,
        "all_questions_candidates": all_questions_candidates,
        "bar_fig": bar_fig_json,
        "top_5_fig": top_5_fig_json,
        "line_fig": line_fig_json,
        "pie_fig": pie_fig_json,
        "table_data": table_data,
        "job_roles": job_roles,
        "result_type": result_type,
        "from_interview_date": from_interview_date,
        "to_interview_date": to_interview_date
    })
@app.get("/admin/view_responses", response_class=HTMLResponse)
def view_responses(request: Request, email: str, level: str):
    print(f"Email: {email}, Level: {level}")
    if level == "2":
        file_to_use = RESULTS_FILE
    elif level == "3":
        file_to_use = HR_RESULTS_FILE
    else:
        print("Invalid level")
        raise HTTPException(status_code=400, detail="Invalid level")
    print(f"Checking file: {file_to_use}")
    if not os.path.exists(file_to_use):
        print("Results file not found")
        raise HTTPException(status_code=404, detail="No results found")
    df = pd.read_excel(file_to_use)
    print("DataFrame columns:", df.columns.tolist())
    candidate_row = df[df["candidate email"] == email]
    print("Candidate row:", candidate_row)
    if candidate_row.empty:
        print("Candidate not found")
        raise HTTPException(status_code=404, detail="Candidate not found")
    response_dict = candidate_row.iloc[0].to_dict()
    print("Response dict:", response_dict)
    qas = []
    question_columns = [col for col in response_dict if col.lower().startswith("question")]
    print("Question columns:", question_columns)
    for i, q_col in enumerate(question_columns, start=1):
        ca_col = f"candidate answer {i}"
        score_col = f"score {i}"
        correct_col = f"correct answer {i}" if level == "2" else ""
        qa = {
            "question": response_dict.get(q_col, ""),
            "candidate_answer": response_dict.get(ca_col, ""),
            "score": response_dict.get(score_col, "")
        }
        if level == "2":
            qa["correct_answer"] = response_dict.get(correct_col, "")
        qas.append(qa)
        print(f"QA {i}:", qa)
    print("Rendering template with qas:", qas)
    return templates.TemplateResponse(
        "admin_view_responses.html", 
        {"request": request, "candidate_email": email, "qas": qas, "level": level}
    )
@app.post("/admin/bulk_action")
async def bulk_action(
    request: Request,
    action: str = Form(...),
    selected_emails: str = Form(...),
    level: Optional[str] = Form(None),
    from_date: Optional[str] = Form(None),
    to_date: Optional[str] = Form(None),
    min_mark: Optional[float] = Form(None),
    max_mark: Optional[float] = Form(None),
    top_number: Optional[int] = Form(None)
):
    file_to_use = APTITUDE_RESULTS_FILE if level == "1" else HR_RESULTS_FILE if level == "3" else RESULTS_FILE
    if os.path.exists(file_to_use):
        df = pd.read_excel(file_to_use)
        if level == "1":
            df = df.rename(columns={
                "Name": "candidate name",
                "Mail": "candidate email",
                "Interview Date": "interview date",
                "Score": "total score"
            })
    else:
        df = pd.DataFrame()
    
    if from_date:
        df = df[df["interview date"].apply(lambda d: pd.to_datetime(d, errors="coerce") >= pd.to_datetime(from_date))]
    if to_date:
        df = df[df["interview date"].apply(lambda d: pd.to_datetime(d, errors="coerce") <= pd.to_datetime(to_date))]
    if min_mark is not None:
        df = df[df["total score"] >= min_mark]
    if max_mark is not None:
        df = df[df["total score"] <= max_mark]
    if top_number is not None:
        df = df.sort_values(by="total score", ascending=False).head(top_number)
    
    emails = [e.strip() for e in selected_emails.split(",") if e.strip()]
    
    if action in ["download_selected", "download_reject"]:
        os.makedirs("results", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if action == "download_selected":
            selected_df = df[df["candidate email"].isin(emails)]
            filename = f"results/selected_candidates_{timestamp}.xlsx"
        elif action == "download_reject":
            selected_df = df[~df["candidate email"].isin(emails)]
            filename = f"results/reject_candidates_{timestamp}.xlsx"
        selected_df.to_excel(filename, index=False)
        return FileResponse(filename, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=os.path.basename(filename))
    elif action in ["send_selected_mail", "send_reject_mail"]:
        if action == "send_selected_mail":
            target_emails = emails
        elif action == "send_reject_mail":
            all_emails = df["candidate email"].tolist()
            target_emails = [e for e in all_emails if e not in emails]
        default_subject = "Interview Update"
        default_message = "This is an automated notification regarding your interview status."
        for email in target_emails:
            send_email(email, default_subject, default_message)
        return RedirectResponse(url="/admin/dashboard", status_code=302)
    else:
        raise HTTPException(status_code=400, detail="Invalid bulk action")
    
@app.post("/interview/detect_frame")
async def detect_frame(email: str = Form(...), file: UploadFile = File(...)):
    contents = await file.read()
    np_arr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(status_code=400, detail="Invalid image file")
    scale_factor = 0.25
    small_frame = cv2.resize(frame, (0, 0), fx=scale_factor, fy=scale_factor)
    pil_img = Image.fromarray(cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB))
    img_tensor = transform(pil_img).unsqueeze(0).to(device)
    person_detections, mobile_detected, mobile_boxes = await combined_detection(small_frame, img_tensor)
    person_count = len(person_detections)
    annotated_frame = frame.copy()
    for (x1, y1, x2, y2) in person_detections:
        x1_orig = int(x1 / scale_factor)
        y1_orig = int(y1 / scale_factor)
        x2_orig = int(x2 / scale_factor)
        y2_orig = int(y2 / scale_factor)
        cv2.rectangle(annotated_frame, (x1_orig, y1_orig), (x2_orig, y2_orig), (0, 255, 0), 2)
        cv2.putText(annotated_frame, "Person", (x1_orig, max(y1_orig - 10, 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    for box in mobile_boxes:
        x1, y1, x2, y2 = box.astype(int)
        x1 = int(x1 / scale_factor)
        y1 = int(y1 / scale_factor)
        x2 = int(x2 / scale_factor)
        y2 = int(y2 / scale_factor)
        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(annotated_frame, "Mobile", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
    retval, buffer = cv2.imencode('.jpg', annotated_frame)
    jpg_as_text = base64.b64encode(buffer).decode("utf-8")
    if email == "precheck":
        if person_count != 1:
            return {"message": "Person detection failed. Exactly one person must be detected during precheck.",
                    "annotated_image": jpg_as_text}
        if mobile_detected:
            return {"message": "Mobile phone detected during precheck.",
                    "annotated_image": jpg_as_text}
        return {"message": "No prohibited items detected.",
                "annotated_image": jpg_as_text}
    if email not in candidate_db:
        raise HTTPException(status_code=404, detail="Candidate not found")
    warnings = candidate_warnings.get(email, 0)
    if candidate_status.get(email) == "terminated":
        return {"message": f"Interview terminated. Warning({warnings}/3)",
                "annotated_image": jpg_as_text}
    message_parts = []
    if person_count > 1:
        message_parts.append("Multiple persons detected.")
    if mobile_detected:
        message_parts.append("Mobile phone detected.")
    if message_parts:
        candidate_warnings[email] = warnings + 1
        warnings = candidate_warnings[email]
        violation_message = " ".join(message_parts)
        if warnings >= 3:
            candidate_status[email] = "terminated"
            return {"message": f"{violation_message} Warning({warnings}/3). Interview terminated.",
                    "annotated_image": jpg_as_text}
        else:
            return {"message": f"{violation_message} Warning({warnings}/3).",
                    "annotated_image": jpg_as_text}
    else:
        return {"message": f"No prohibited items detected. Warning({warnings}/3).",
                "annotated_image": jpg_as_text}

@app.post("/candidate/login")
def candidate_login(email: str = Form(...), password: str = Form(...)):
    if email in candidate_db and candidate_db[email].get("password") == password:
        return RedirectResponse(url=f"/interview/ui?email={email}", status_code=302)
    raise HTTPException(status_code=401, detail="Invalid candidate credentials")

@app.post("/interview/submit")
def submit_interview(submission: InterviewSubmission):
    email = submission.email
    if email not in candidate_db:
        raise HTTPException(status_code=404, detail="Candidate not found")
    candidate = candidate_db[email]
    if "qas" not in candidate:
        raise HTTPException(status_code=400, detail="No interview questions loaded for candidate")
    qas = candidate["qas"]
    if len(qas) != len(submission.responses):
        raise HTTPException(status_code=400, detail="Responses count does not match questions count")
    total_score = 0
    evaluations = []
    for qa, resp in zip(qas, submission.responses):
        question_text = qa["question"]
        candidate_answer = resp.get("candidate_answer", "")
        if "answer" in qa:
            correct_answer = qa["answer"]
            question_tokens = set(question_text.lower().split())
            candidate_tokens = candidate_answer.lower().split()
            filtered_tokens = [t for t in candidate_tokens if t not in question_tokens]
            filtered_answer = " ".join(filtered_tokens).strip()
            if not filtered_answer:
                score = 0.0
            else:
                vectorizer = TfidfVectorizer().fit([filtered_answer, correct_answer])
                vecs = vectorizer.transform([filtered_answer, correct_answer])
                similarity = cosine_similarity(vecs[0], vecs[1])[0][0]
                score = round(similarity * 5, 2)
        else:
            score = evaluate_answer_with_llama(question_text, candidate_answer)
        total_score += score
        evaluations.append({
            "question": question_text,
            "candidate_answer": candidate_answer,
            "score": score,
            "feedback": f"Your score: {score} out of 5."
        })
    candidate["total_score"] = total_score
    candidate["evaluations"] = evaluations
    return JSONResponse(content={"redirect": f"/candidate/submit_name?email={email}"})

@app.post("/ap1/evaluate")
def evaluate_aptitude(evaluation: AptitudeEvaluation):
    email = evaluation.email
    if email not in candidate_db:
        raise HTTPException(status_code=404, detail="Candidate not found")
    candidate = candidate_db[email]
    if "aptitude_questions" not in candidate:
        raise HTTPException(status_code=400, detail="Aptitude questions not loaded for candidate")
    questions = candidate["aptitude_questions"]
    submitted_answers = evaluation.answers
    total_score = 0
    evaluations = []
    for q in questions:
        qid = q["id"]
        correct_answer = q.get("answer", "").strip().lower()
        candidate_answer = submitted_answers.get(qid, "").strip().lower()
        score = 1 if candidate_answer == correct_answer and candidate_answer != "" else 0
        total_score += score
        evaluations.append({
            "question": q["question"],
            "correct_answer": q.get("answer", ""),
            "candidate_answer": submitted_answers.get(qid, ""),
            "score": score,
            "feedback": f"{score} mark awarded." if score == 1 else "No mark awarded."
        })
    candidate["total_score"] = total_score
    candidate["evaluations"] = evaluations
    return JSONResponse(content={"score": total_score, "total": len(questions)})

@app.get("/candidate/submit_name", response_class=HTMLResponse)
def candidate_submit_name_page(request: Request, email: str):
    return templates.TemplateResponse("candidate_submit_name.html", {"request": request, "email": email})

@app.post("/candidate/submit_name")
def candidate_submit_name(email: str = Form(...), candidate_name: str = Form(...)):
    if email not in candidate_db:
        raise HTTPException(status_code=404, detail="Candidate not found")
    candidate = candidate_db[email]
    total_score = candidate.get("total_score", 0)
    evaluations = candidate.get("evaluations", [])
    if candidate.get("level") == "1":
        append_candidate_aptitude_result(email, candidate_name, candidate.get("interview_datetime"), total_score)
    elif candidate.get("level") == "2":
        append_candidate_result(email, candidate_name, total_score, evaluations, candidate.get("interview_datetime"))
    elif candidate.get("level") == "3":
        append_hr_candidate_result(email, candidate_name, total_score, evaluations, candidate.get("interview_datetime"))
    html_content = f"""
    <html>
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Submission Successful</title>
        <style>
          body {{ 
            background: linear-gradient(135deg, #e3f2fd, #bbdefb); 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            min-height: 100vh; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
          }}
          .box {{
            background: #fff;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
            text-align: center;
            animation: fadeIn 0.8s ease-in;
          }}
          h2 {{ color: #263238; font-weight: 600; }}
          @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
        </style>
      </head>
      <body>
        <div class="box">
          <h2>Thank you, {candidate_name}. Your result has been submitted.</h2>
        </div>
      </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# AP1 Endpoints
ap1_router = APIRouter(prefix="/ap1")

@ap1_router.get("/", response_class=HTMLResponse)
def ap1_index(email: str = ""):
    return RedirectResponse(url=f"/ap1_detect?email={email}", status_code=302)

app.include_router(ap1_router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8004)