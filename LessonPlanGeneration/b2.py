import pytesseract
from PIL import Image
import streamlit as st
import pandas as pd
import datetime as dt
import re

# Configure Tesseract (adjust the path for your system if necessary)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Function to extract text from an image using Tesseract OCR
def extract_text_from_image(image):
    try:
        return pytesseract.image_to_string(image)
    except Exception as e:
        return f"Error during OCR: {str(e)}"

# Function to clean and normalize text
def clean_text(raw_text):
    # Remove headers, footers, or unnecessary lines
    filtered_text = re.sub(r"\[.*?\]|\bPage\s+\d+.*?\b|Vishwakarma.*?Pune.*?|Issue\s+\d+:.*?\d{2}/\d{2}/\d{2}", "", raw_text)
    # Remove excessive whitespace or newlines
    filtered_text = re.sub(r"\n\s*\n", "\n\n", filtered_text).strip()
    return filtered_text

# Function to extract topics and subtopics
def extract_topics_and_subtopics(cleaned_text):
    topics = []
    lines = cleaned_text.split("\n")

    current_topic = None
    for line in lines:
        if line.strip():
            # Check for new topic based on typical syllabus formatting
            if re.match(r"^[A-Za-z\s]+[\d\s]*[:\-]", line):
                if current_topic:
                    topics.append(current_topic)
                current_topic = {"topic": line.strip(), "subtopics": []}
            elif current_topic:
                current_topic["subtopics"].append(line.strip())
    if current_topic:
        topics.append(current_topic)
    return topics

# Function to flatten topics into a list of lecture topics
def flatten_topics(topics):
    flat_lecture_topics = []
    for topic in topics:
        flat_lecture_topics.append(topic["topic"])
        flat_lecture_topics.extend(topic["subtopics"])
    return flat_lecture_topics

# Function to generate a lesson plan with flat lecture topics
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

# Streamlit App
def main():
    st.title("Lesson Plan Generator")

    # File uploads
    syllabus_image = st.file_uploader("Upload Syllabus Image", type=["jpg", "png"])
    calendar_image = st.file_uploader("Upload Academic Calendar Image", type=["jpg", "png"])
    subject_name = st.text_input("Enter the Subject Name")

    if syllabus_image and calendar_image and subject_name:
        syllabus_image = Image.open(syllabus_image)
        calendar_image = Image.open(calendar_image)

        # Extract text from images
        syllabus_text = extract_text_from_image(syllabus_image)
        calendar_text = extract_text_from_image(calendar_image)

        if "Error" in syllabus_text or "Error" in calendar_text:
            st.error("Failed to extract text from image(s).")
            return

        # Clean and process text
        syllabus_text = clean_text(syllabus_text)
        calendar_text = clean_text(calendar_text)

        # Extract topics and subtopics
        topics = extract_topics_and_subtopics(syllabus_text)

        # Flatten topics for lectures
        flat_lecture_topics = flatten_topics(topics)

        # Extract public holidays
        public_holidays = re.findall(r"\b\d{2}/\d{2}/\d{4}\b", calendar_text)
        public_holidays = [dt.datetime.strptime(date, "%d/%m/%Y").date() for date in public_holidays]

        # Display extracted topics
        st.write(f"**Extracted Lecture Topics for {subject_name}:**")
        for lecture_topic in flat_lecture_topics:
            st.write(f"- {lecture_topic}")

        # Lesson plan inputs
        start_date = st.date_input("Semester Start Date", dt.date.today())
        end_date = st.date_input("Semester End Date", start_date + dt.timedelta(days=120))
        lecture_days_input = st.text_input("Lecture Days (e.g., 0 for Monday, 2 for Wednesday)", "0,2,4")
        lecture_days = [int(day.strip()) for day in lecture_days_input.split(",")]

        # Generate lesson plan
        if st.button("Generate Lesson Plan") and flat_lecture_topics:
            lesson_plan = generate_lesson_plan(
                start_date=start_date,
                end_date=end_date,
                lecture_days=lecture_days,
                public_holidays=public_holidays,
                flat_lecture_topics=flat_lecture_topics
            )

            st.write("**Generated Lesson Plan:**")
            st.dataframe(lesson_plan)

            # Download as CSV
            csv = lesson_plan.to_csv(index=False)
            st.download_button("Download Lesson Plan as CSV", data=csv, file_name=f"{subject_name}_lesson_plan.csv", mime="text/csv")

if __name__ == "__main__":
    main()
