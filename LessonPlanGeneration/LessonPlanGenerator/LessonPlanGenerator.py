import PyPDF2
import spacy
import re
from collections import Counter

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    pdf_text = ''
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfFileReader(pdf_file)
        num_pages = pdf_reader.numPages
        for page_num in range(num_pages):
            page = pdf_reader.getPage(page_num)
            pdf_text += page.extract_text()
    return pdf_text

# Function to identify topics and subtopics
def extract_topics_and_subtopics(text):
    doc = nlp(text)
    topics = []
    
    for sent in doc.sents:
        # Simple heading detection based on sentence structure and keywords
        if re.match(r'^\d+(\.\d+)*', sent.text.strip()):
            topics.append(sent.text.strip())
    
    return topics

# Function to assign weightage to topics and subtopics based on frequency
def assign_weightage(topics):
    weightage_dict = {}
    
    for topic in topics:
        weightage = 1  # Default weightage
        # Higher weightage for topics/subtopics that appear frequently
        if len(re.findall(r'\b(' + re.escape(topic.split(' ')[0]) + r')\b', ' '.join(topics))) > 2:
            weightage = 2
        weightage_dict[topic] = weightage
    
    return weightage_dict

# Function to format the output into the required structure
def format_output(topics, weightage_dict):
    formatted_output = []
    for topic in topics:
        if re.match(r'^\d+$', topic):  # Main topic (e.g., 1, 2, 3)
            formatted_output.append(f'{topic}')
        elif re.match(r'^\d+\.\d+$', topic):  # Subtopic (e.g., 2.1, 3.1)
            formatted_output.append(f'{topic} (Weightage: {weightage_dict.get(topic, 1)})')
        else:
            formatted_output.append(f'{topic}')  # Deeper subtopics
    
    return '\n'.join(formatted_output)

# Main Function
def generate_topic_outline(pdf_path):
    # Step 1: Extract text from PDF
    text = extract_text_from_pdf(pdf_path)
    
    # Step 2: Extract topics and subtopics
    topics = extract_topics_and_subtopics(text)
    
    # Step 3: Assign weightage
    weightage_dict = assign_weightage(topics)
    
    # Step 4: Format the output
    structured_output = format_output(topics, weightage_dict)
    
    # Save to a .txt file
    with open('output_outline.txt', 'w') as f:
        f.write(structured_output)
    
    print('Generated outline saved to output_outline.txt')

# Usage
pdf_path = 'path_to_your_pdf_file.pdf'  # Specify your PDF file here
generate_topic_outline(pdf_path)
