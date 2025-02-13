from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
import json
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import pickle
import re
from flask import Flask, render_template, request, redirect, url_for, send_file, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For session management


UPLOAD_FOLDER = 'text_files'
ALLOWED_EXTENSIONS = {'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to read text files
def read_text_files(directory):
    documents = []
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
                documents.append(file.read())
    return documents

# Function to extract topics from documents
def extract_topics(documents):
    topics = []
    for doc in documents:
        # Adjust regex based on how topics are formatted in your text
        lecture_topics = re.findall(r'\d+\.\s(.+)', doc)
        for topic in lecture_topics:
            topics.append(topic.strip())
    return topics

from datetime import timedelta
import calendar

def distribute_topics(topics, semester_weeks, lectures_per_week, start_date, days, times):
    schedule = []
    topic_index = 0

    # Create a list of lecture days based on selected days
    lecture_days = []
    for week in range(semester_weeks):
        for day, time in zip(days, times):
            # Calculate the actual date for the day of the week
            current_date = start_date + timedelta(weeks=week)
            # Find the first occurrence of the selected day in the current week
            day_offset = (list(calendar.day_name).index(day) - current_date.weekday()) % 7
            lecture_day_date = current_date + timedelta(days=day_offset)
            lecture_days.append((lecture_day_date, day, time))  # Include the day here

    for week in range(semester_weeks):
        for lecture in range(lectures_per_week):
            if topic_index < len(topics):
                if week * lectures_per_week + lecture < len(lecture_days):
                    date, day, time = lecture_days[week * lectures_per_week + lecture]  # Unpack the new day
                    lecture_number = week * lectures_per_week + lecture + 1  # Adjust lecture numbering
                    weightage = 3  # Replace with your actual weightage logic if needed
                    schedule.append({
                        'Date': date.strftime("%Y-%m-%d"),
                        'Day': day,  # Add the day to the schedule
                        'Lecture Number': lecture_number,
                        'Time Slot': time,
                        'Topic': topics[topic_index]
                    })
                    topic_index += 1
                else:
                    break
            else:
                break

    return schedule

@app.route('/upload', methods=['POST'])
def upload_file():
    # Existing upload logic remains unchanged...

    # Process files and generate schedule
    documents = read_text_files(app.config['UPLOAD_FOLDER'])
    topics = extract_topics(documents)

    # Get user input for semester dates and lectures
    semester_start = request.form['semester_start']
    semester_end = request.form['semester_end']
    lectures_per_week = int(request.form['lectures_per_week'])
    days = request.form.getlist('days[]')
    times = request.form.getlist('times[]')

    # Convert string dates to datetime objects
    start_date = datetime.strptime(semester_start, '%Y-%m-%d')
    end_date = datetime.strptime(semester_end, '%Y-%m-%d')

    # Calculate the number of weeks
    delta = end_date - start_date
    semester_weeks = delta.days // 7 + 1  # +1 to include the start week

    # Generate the schedule
    schedule = distribute_topics(topics, semester_weeks, lectures_per_week, start_date, days, times)

    # Save schedule as Excel file
    df_schedule = pd.DataFrame(schedule)  # Create DataFrame directly from the schedule list
    excel_filename = 'lesson_schedule.xlsx'
    df_schedule.to_excel(excel_filename, index=False, engine='openpyxl')  # Set index=False to not include index in the Excel file

    # Provide download link to user
    return send_file(excel_filename, as_attachment=True, download_name=excel_filename)


# Function to calculate the number of weeks and generate the schedule
def calculate_weeks_and_generate_schedule(start_date, end_date, lectures_per_week, days, times, topics):
    # Calculate the number of weeks
    delta = end_date - start_date
    semester_weeks = delta.days // 7 + 1  # +1 to include the start week

    # Generate the schedule
    schedule = distribute_topics(topics, semester_weeks, lectures_per_week)

    # Combine days and times into a dictionary for scheduling
    timed_schedule = {}
    for i, (week, topic) in enumerate(schedule.items()):
        week_number = (i // lectures_per_week) + 1
        lecture_number = (i % lectures_per_week) + 1
        if i < len(days) and i < len(times):
            timed_schedule[f'Week {week_number} Lecture {lecture_number} ({days[i]} {times[i]})'] = topic
        else:
            timed_schedule[f'Week {week_number} Lecture {lecture_number}'] = topic

    return timed_schedule



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
