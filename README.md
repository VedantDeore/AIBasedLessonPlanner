# AI-Based Lesson Planner

The AI-Based Lesson Planner is a tool designed to automate the creation of structured lesson plans using OCR (Optical Character Recognition) and NLP (Natural Language Processing). It extracts data from academic calendars and syllabi, processes it, and generates customizable lesson plans in multiple formats (JSON, PDF, Excel, Word, Image).

## Table of Contents
- [Features](#features)
- [Project Setup Steps](#project-setup-steps)
- [Usage Instructions](#usage-instructions)
- [Folder Structure](#folder-structure)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features
- Extracts text from uploaded images of academic calendars and syllabi using OCR.
- Parses extracted data to identify key dates, holidays, events, topics, and subtopics.
- Generates structured lesson plans with customizable fields (e.g., Method, Student Activity, Assessment Tool).
- Supports dynamic editing of generated lesson plans.
- Exports lesson plans in multiple formats: JSON, PDF, Excel, Word, and Image.

## Project Setup Steps

### 1. Prerequisites
Before setting up the project, ensure you have the following installed:
- Python 3.8 or higher
- Tesseract OCR (for text extraction from images)
- A modern web browser

### Install Tesseract OCR
#### Windows:
Download and install Tesseract from [here](https://github.com/tesseract-ocr/tesseract).

#### macOS:
```bash
brew install tesseract
```

#### Linux:
```bash
sudo apt-get install tesseract-ocr
```

### 2. Clone the Repository
```bash
git clone https://github.com/your-repo-url/AIBasedLessonPlanner.git
cd AIBasedLessonPlanner
```

### 3. Set Up a Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Tesseract Path (For Windows Users)
If you're on Windows, update the Tesseract path in the code. Open the `app.py` file and modify the following line:
```python
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
```
Replace the path with the actual installation path of Tesseract on your system.

### 6. Run the Application
```bash
python app.py
```
By default, the application will run on `http://127.0.0.1:8000`. Open this URL in your web browser to access the application.

## Usage Instructions
### Upload Academic Calendar
- Navigate to the `/upload_calendar` route.
- Upload an image or text file containing the academic calendar.
- The system will extract key dates, holidays, and events.

### Upload Syllabus
- Navigate to the `/upload_syllabus` route.
- Upload an image or text file containing the syllabus.
- The system will parse topics and subtopics.

### Edit Extracted Data
- Use the `/edit_calendar` route to review and edit the extracted data.

### Generate Lesson Plan
- Navigate to the `/final_plan` route to view and edit the generated lesson plan.

### Download Lesson Plan
- Use the `/download_lesson_plan` route to download the lesson plan in your preferred format (JSON, PDF, Excel, Word, Image).

## Folder Structure
```
AIBasedLessonPlanner/
├── app.py                  # Main Flask application file
├── requirements.txt        # List of Python dependencies
├── uploads/                # Directory for uploaded files
├── data/                   # Directory for storing intermediate JSON files
├── templates/              # HTML templates for rendering pages
│   ├── index.html          # Homepage
│   ├── upload_calendar.html
│   ├── upload_syllabus.html
│   ├── edit_calendar.html
│   ├── final.html
│   └── download.html
└── README.md               # This file
```

## Dependencies
All required Python packages are listed in the `requirements.txt` file:

```
Flask==2.3.2
pytesseract==0.3.10
Pillow==9.5.0
pandas==1.5.3
numpy==1.23.5
openpyxl==3.1.2
reportlab==4.0.4
docx==0.2.4
requests==2.31.0
spacy==3.5.0
regex==2023.10.3
```
To install these dependencies, run:
```bash
pip install -r requirements.txt
```

## Contributing
We welcome contributions from the community! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add your commit message here"
   ```
4. Push your changes to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Submit a pull request to the main repository.
