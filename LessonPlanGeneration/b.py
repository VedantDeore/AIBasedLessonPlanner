from PyPDF2 import PdfReader
import spacy
import re

# Load spaCy model
nlp = spacy.load("en_core_web_sm")
nlp.max_length = 3000000  # Increase this limit to handle larger text

# Function to extract text from a specific page range in the PDF
def extract_text_from_pdf(pdf_path, start_page=None, end_page=None):
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        text = ""
        if start_page is None and end_page is None:
            # Extract text from the entire PDF if no range is provided
            for page in reader.pages:
                text += page.extract_text() or ''
        else:
            # Extract text from the specified page range
            for i in range(start_page, end_page + 1):
                text += reader.pages[i].extract_text() or ''
    return text

# Function to extract topics and subtopics from the index page (Table of Contents)
def extract_topics_from_index(text):
    topics = []
    for line in text.split("\n"):
        # Clean line to remove trailing page numbers and non-relevant characters
        line_cleaned = re.sub(r'\s*\*\s*$', '', line.strip())  # Remove trailing asterisks
        line_cleaned = re.sub(r'\s+\d+$', '', line_cleaned)  # Remove trailing page numbers
        line_cleaned = re.sub(r'\s+', ' ', line_cleaned)  # Normalize spaces

        # Match patterns for topics and subtopics (e.g., 1.4, 1.4.1)
        if re.match(r'^\d+(\.\d+)*\s+', line_cleaned):
            topics.append(line_cleaned.strip())
    return topics

# Function to calculate weightage by checking the length of content for each topic/subtopic
def calculate_weightage(topics, full_text):
    weightage_dict = {}
    for topic in topics:
        topic_title = ' '.join(topic.split(' ')[1:])  # Remove the numbering part of the topic

        # Find the index of the topic in the text to extract the corresponding content
        pattern = re.escape(topic_title) + r'.*?(?=\d+\.\d+|\Z)'  # Look for the topic until the next subtopic
        content = re.search(pattern, full_text, re.DOTALL)

        if content:
            content_length = len(content.group(0))  # Get the length of the content
            weightage = 1 if content_length < 300 else 2  # Set weightage based on content length
        else:
            weightage = 0  # No content found for the topic

        weightage_dict[topic] = weightage
    return weightage_dict

# Function to format the output into a structured form
def format_output(topics, weightage_dict):
    formatted_output = []
    for topic in topics:
        if re.match(r'^\d+$', topic):  # Main topic (e.g., 1, 2, 3)
            formatted_output.append(f'{topic}')
        elif re.match(r'^\d+\.\d+$', topic):  # Subtopic (e.g., 2.1, 3.1)
            formatted_output.append(f'{topic} (CO: {weightage_dict.get(topic, 1)})')
        elif re.match(r'^\d+\.\d+\.\d+$', topic):  # Deeper subtopic (e.g., 5.4.1)
            formatted_output.append(f'{topic} (CO: {weightage_dict.get(topic, 1)})')
        else:
            formatted_output.append(f'{topic}')  # For unrecognized formats
    return '\n'.join(formatted_output)

# Main function to generate the topic outline
def generate_topic_outline(pdf_path, index_start_page, index_end_page):
    # Step 1: Extract text from the index (Table of Contents) pages
    index_text = extract_text_from_pdf(pdf_path, index_start_page, index_end_page)

    # Step 2: Extract topics and subtopics from the index
    topics = extract_topics_from_index(index_text)

    # Step 3: Extract text from the entire book
    full_text = extract_text_from_pdf(pdf_path)

    # Step 4: Calculate weightage by checking the length of content for each topic/subtopic in the book
    weightage_dict = calculate_weightage(topics, full_text)

    # Step 5: Format the output
    structured_output = format_output(topics, weightage_dict)

    # Save the output to a .txt file
    # Save the output to a .txt file using UTF-8 encoding
    with open('output_outline.txt', 'w', encoding='utf-8') as f:
        f.write(structured_output)


    print('Generated outline saved to output_outline.txt')

# Usage
pdf_path = 'books/Andrew S. Tanenbaum - Computer Networks.pdf'  # Specify your PDF file here
index_start_page = 9  # Example: Starting page of the index in the PDF
index_end_page = 19    # Example: Ending page of the index in the PDF
generate_topic_outline(pdf_path, index_start_page, index_end_page)
