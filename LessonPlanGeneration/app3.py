from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
import json
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from flask import Flask, render_template, request, redirect, url_for, send_file, flash

from PIL import Image
import pytesseract
import json
import os
import re
import pandas as pd
import datetime as dt


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For session management



UPLOAD_FOLDER = 'text_files'
ALLOWED_EXTENSIONS = {'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Function to read text files
def read_text_files(directory):
    documents = []
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
                documents.append(file.read())
    return documents

# ///////////////////////////////////////////////////////////

# Configure Tesseract (adjust path as needed)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Ensure directories exist
os.makedirs('uploads', exist_ok=True)
os.makedirs('data', exist_ok=True)

# OCR and Text Processing Functions
def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)
        return pytesseract.image_to_string(image)
    except Exception as e:
        return f"Error during OCR: {str(e)}"

def clean_text(raw_text):
    # Remove headers, footers, unnecessary lines
    filtered_text = re.sub(r"\[.*?\]|\bPage\s+\d+.*?\b|Vishwakarma.*?Pune.*?|Issue\s+\d+:.*?\d{2}/\d{2}/\d{2}", "", raw_text)
    filtered_text = re.sub(r"\n\s*\n", "\n\n", filtered_text).strip()
    return filtered_text

def extract_topics_and_subtopics(cleaned_text):
    topics = []
    lines = cleaned_text.split("\n")

    current_topic = None
    for line in lines:
        if line.strip():
            if re.match(r"^[A-Za-z\s]+[\d\s]*[:\-]", line):
                if current_topic:
                    topics.append(current_topic)
                current_topic = {"topic": line.strip(), "subtopics": []}
            elif current_topic:
                current_topic["subtopics"].append(line.strip())
    if current_topic:
        topics.append(current_topic)
    return topics

def generate_lesson_plan(start_date, end_date, lecture_days, public_holidays, flat_lecture_topics):
    current_date = start_date
    lecture_no = 1
    schedule = []

    for lecture_topic in flat_lecture_topics:
        while current_date <= end_date:
            if current_date.weekday() in lecture_days and current_date not in public_holidays:
                schedule.append({
                    "Date": current_date.strftime("%Y-%m-%d"),
                    "Day": current_date.strftime("%A"),
                    "Lecture No": lecture_no,
                    "Topic": lecture_topic
                })
                lecture_no += 1
                current_date += dt.timedelta(days=1)
                break
            current_date += dt.timedelta(days=1)

    return pd.DataFrame(schedule)


import re
import json
import datetime as dt

@app.route('/upload_calendar', methods=['GET', 'POST'])
def upload_calendar():
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'calendar_image' not in request.files:
            return "No file uploaded", 400
        
        calendar_image = request.files['calendar_image']
        
        if calendar_image.filename == '':
            return "No selected file", 400
        
        # Save the uploaded image
        image_path = os.path.join('uploads', 'calendar_image.jpg')
        calendar_image.save(image_path)
        
        # Extract text from image
        calendar_text = extract_text_from_image(image_path)
        
        # Clean the extracted text
        cleaned_calendar_text = clean_text(calendar_text)
        
        # Extract start and end semester dates
        start_of_semester = re.search(r"Start of Semester.*?(\d{1,2}/\d{1,2}/\d{2,4})", cleaned_calendar_text)
        end_of_semester = re.search(r"End Semester Examination.*?(\d{1,2}/\d{1,2}/\d{2,4})", cleaned_calendar_text)
        
        # Extract class test and event dates
        class_test_1 = re.search(r"Class Test 1.*?(\d{1,2}/\d{1,2}/\d{2,4})\s*to\s*(\d{1,2}/\d{1,2}/\d{2,4})", cleaned_calendar_text)
        mid_semester_reviews = re.search(r"Mid Semester Reviews.*?(\d{1,2}/\d{1,2}/\d{2,4})\s*to\s*(\d{1,2}/\d{1,2}/\d{2,4})", cleaned_calendar_text)
        class_test_2 = re.search(r"Class Test 2.*?(\d{1,2}/\d{1,2}/\d{2,4})\s*to\s*(\d{1,2}/\d{1,2}/\d{2,4})", cleaned_calendar_text)
        remedial_teaching = re.search(r"End Semester Remedial Teaching.*?(\d{1,2}/\d{1,2}/\d{2,4})\s*to\s*(\d{1,2}/\d{1,2}/\d{2,4})", cleaned_calendar_text)
        
        # Extract holidays
        holidays = re.findall(r"([A-Za-z\s]+[-/A-Za-z\s]*\d{1,2}/\d{1,2}/\d{2,4})", cleaned_calendar_text)
        
        # Extract event dates (if any)
        event_dates = {
            'start_of_semester': start_of_semester.group(1) if start_of_semester else None,
            'end_of_semester': end_of_semester.group(1) if end_of_semester else None,
            'class_test_1': {'start': class_test_1.group(1), 'end': class_test_1.group(2)} if class_test_1 else None,
            'mid_semester_reviews': {'start': mid_semester_reviews.group(1), 'end': mid_semester_reviews.group(2)} if mid_semester_reviews else None,
            'class_test_2': {'start': class_test_2.group(1), 'end': class_test_2.group(2)} if class_test_2 else None,
            'remedial_teaching': {'start': remedial_teaching.group(1), 'end': remedial_teaching.group(2)} if remedial_teaching else None
        }
        
        # Extract holiday dates
        holiday_dates = []
        for holiday in holidays:
            date_match = re.search(r"(\d{1,2}/\d{1,2}/\d{2,4})", holiday)
            if date_match:
                holiday_dates.append(date_match.group(1))
        
        # Save extracted data to JSON
        with open('data/calendar_data.json', 'w') as f:
            json.dump({
                'calendar_text': cleaned_calendar_text,  # Save the cleaned text
                'raw_text': calendar_text,  # Save the raw OCR text
                'events': event_dates,  # Save the extracted event dates
                'holidays': holiday_dates  # Save the holidays
            }, f, indent=4)
        
        return redirect(url_for('upload_syllabus'))
    
    return render_template('upload_calendar.html')

# Helper function to clean extracted text
def clean_text(raw_text):
    # Remove unwanted characters or fix OCR issues (e.g., incorrect spaces, misinterpreted characters)
    cleaned_text = raw_text.replace("\n", " ").replace("\u00a5", "Y").replace("\u2014", "-")
    
    # Fix spaces, punctuation, and formatting
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Replace multiple spaces with single space
    cleaned_text = re.sub(r'(\d{1,2}/\d{1,2}/\d{2,4})', r'\1', cleaned_text)  # Ensure date format is consistent
    
    return cleaned_text


# @app.route('/upload_calendar', methods=['GET', 'POST'])
# def upload_calendar():
#     if request.method == 'POST':
#         # Check if a file was uploaded
#         if 'calendar_image' not in request.files:
#             return "No file uploaded", 400
        
#         calendar_image = request.files['calendar_image']
        
#         if calendar_image.filename == '':
#             return "No selected file", 400
        
#         # Save the uploaded image
#         image_path = os.path.join('uploads', 'calendar_image.jpg')
#         calendar_image.save(image_path)
        
#         # Extract text from image
#         calendar_text = extract_text_from_image(image_path)
        
#         # Clean the extracted text
#         cleaned_calendar_text = clean_text(calendar_text)
        
#         # Extract public holidays (if needed)
#         public_holidays = re.findall(r"\b\d{2}/\d{2}/\d{4}\b", cleaned_calendar_text)
#         public_holidays = [dt.datetime.strptime(date, "%d/%m/%Y").date() for date in public_holidays]
        
#         # Save extracted data to JSON
#         with open('data/calendar_data.json', 'w') as f:
#             json.dump({
#                 'calendar_text': cleaned_calendar_text,  # Save the cleaned text
#                 'raw_text': calendar_text,  # Save the raw OCR text
#                 'public_holidays': [str(holiday) for holiday in public_holidays]
#             }, f, indent=4)
        
#         return redirect(url_for('upload_syllabus'))
    
#     return render_template('upload_calendar.html')

@app.route('/upload_syllabus', methods=['GET', 'POST'])
def upload_syllabus():
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'syllabus_image' not in request.files:
            return "No file uploaded", 400
        
        syllabus_image = request.files['syllabus_image']
        
        if syllabus_image.filename == '':
            return "No selected file", 400
        
        # Save the uploaded image
        image_path = os.path.join('uploads', 'syllabus_image.jpg')
        syllabus_image.save(image_path)
        
        # Extract text from image
        syllabus_text = extract_text_from_image(image_path)
        cleaned_syllabus_text = clean_text(syllabus_text)
        
        # Extract topics
        topics = extract_topics_and_subtopics(cleaned_syllabus_text)
        
        # Save extracted data to JSON
        with open('data/syllabus_data.json', 'w') as f:
            json.dump({
                'syllabus_text': cleaned_syllabus_text,
                'topics': topics
            }, f, indent=4)
        
        return redirect(url_for('edit_calendar'))
    
    return render_template('upload_syllabus.html')


@app.route('/edit_calendar', methods=['GET', 'POST'])
def edit_calendar():
    calendar_file = 'data/calendar_data.json'
    
    # Load existing data from JSON
    with open(calendar_file, 'r') as f:
        calendar_data = json.load(f)

    if request.method == 'POST':
        # Update events
        events = {
            "start_of_semester": request.form.get("start_of_semester"),
            "end_of_semester": request.form.get("end_of_semester"),
            "class_test_1": request.form.get("class_test_1"),
            "mid_semester_reviews": request.form.get("mid_semester_reviews"),
            "class_test_2": request.form.get("class_test_2"),
            "remedial_teaching": request.form.get("remedial_teaching"),
        }

        # Update holidays
        holidays = request.form.getlist("holidays[]")
        
        # Update lecture days and times
        lecture_days = request.form.getlist("days[]")
        lecture_times = request.form.getlist("times[]")

        # Save updated data back to JSON
        calendar_data['events'] = events
        calendar_data['holidays'] = holidays
        calendar_data['lecture_days'] = lecture_days
        calendar_data['lecture_times'] = lecture_times

        with open(calendar_file, 'w') as f:
            json.dump(calendar_data, f, indent=4)

        return redirect(url_for('edit_calendar'))

    # Pre-fill form with existing data
    return render_template('edit_calendar.html', calendar_data=calendar_data, zip=zip)






@app.route('/final_plan')
def final_plan():
    # Load lesson plan
    lesson_plan = pd.read_json('data/lesson_plan.json', orient='records')
    
    return render_template('final.html', lesson_plan=lesson_plan.to_dict('records'))

@app.route('/download_lesson_plan')
def download_lesson_plan():
    return send_file('data/lesson_plan.json', 
                     mimetype='application/json', 
                     as_attachment=True, 
                     download_name='lesson_plan.json')


# ///////////////////////////////////////////////////////////


# Helper functions
def load_json(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return {}

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
def load_user_credentials():
    if os.path.exists('user_credentials.json'):
        try:
            with open('user_credentials.json', 'r') as f:
                data = f.read()
                if not data.strip():  # If file is empty or only contains whitespace
                    return {}  # Return an empty dictionary
                return json.loads(data)  # Load the JSON content
        except json.JSONDecodeError:
            # Handle the case where the file contains invalid JSON
            print("Error: The user_credentials.json file is invalid.")
            return {}
    return {}  # If file doesn't exist, return an empty dictionary

# Save user credentials
def save_user_credentials(data):
    with open('user_credentials.json', 'w') as f:
        json.dump(data, f, indent=4)



@app.route('/')
def home():
    username = None
    
    if 'user_email' in session:
        username = session['user_email']
        return render_template('index.html', username=username)

    return render_template('index.html')



@app.route('/lessonplanner')
def lessonplanner():
    username = None
    
    if 'user_email' in session:
        username = session['user_email']
        

        return render_template('lessonplanner.html', username=username)

    return render_template('index.html')

@app.route('/profile')
def profile():
    if 'user_email' in session:
        user_email = session['user_email']
        user_credentials = load_user_credentials()

        if user_email in user_credentials:
            user_data = user_credentials[user_email]  # Fetch user data
            user_email = user_email
            return render_template('profile.html', user=user_data, user_email = user_email)

    return redirect(url_for('login'))  # Redirect to login if not logged in

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user_credentials = load_user_credentials()
        if email not in user_credentials or user_credentials[email]['password'] != password:
            return render_template('login.html', error='Invalid email or password!')

        session['user_email'] = email
        session['user_type'] = 'teacher'  # Assuming all registered users are teachers
        return redirect(url_for('home'))

    return render_template('login.html')


# Registration route for teachers
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return 'Passwords do not match!'

        user_credentials = load_user_credentials()

        if email in user_credentials:
            return 'Email already registered!'

        # Add teacher data
        user_credentials[email] = {
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'password': password
        }

        save_user_credentials(user_credentials)
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True, port=8000)
