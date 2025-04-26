# CoDoc - Code Analysis Tool

CoDoc is a web-based code analysis tool that helps developers understand and improve their code by providing metrics, complexity analysis, and AI-powered insights.

## Features

- Analyze code in multiple languages (Python, JavaScript, Java, C)
- Auto-detect language or manually select
- View code metrics (LOC, functions, complexity)
- Get function-level complexity analysis
- Receive AI-powered insights and refactoring suggestions

## Installation

1. Clone this repository
2. Install the required dependencies:

\`\`\`bash
pip install flask flask-cors python-dotenv radon prettytable google-generativeai javalang esprima pycparser
\`\`\`

3. Make sure you have a valid Google API key in the `api_key.env` file

## Running the Application

1. Start the Flask server:

\`\`\`bash
python app.py
\`\`\`

2. Open your web browser and navigate to `http://localhost:5000`

## Usage

1. Enter or paste your code in the editor
2. Select the language or use auto-detect
3. Click "Analyze Code"
4. View the results in the analysis panel

## Sample Code

The application includes sample code for each supported language to help you get started.

## Requirements

- Python 3.7+
- Flask
- Google Gemini API key
