from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
import os
import logging
import traceback
from dotenv import load_dotenv
import google.generativeai as genai

# Import the analysis function from the provided file
from updated_app import run_analysis, detect_language

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv('api_key.env')
API_KEY = os.getenv('GOOGLE_API_KEY')

if API_KEY:
    genai.configure(api_key=API_KEY)
    logging.info("AI API key loaded successfully.")
else:
    logging.warning("No API key found. AI analysis will be limited.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyzer')
def analyzer():
    return render_template('analyzer.html')

@app.route('/modules')
def modules():
    return render_template('modules.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    code = data.get('code', '')
    
    if not code:
        return jsonify({'error': 'No code provided'}), 400
    
    try:
        # Get the selected language
        selected_language = data.get('language', 'auto')
        
        # Auto-detect language if not specified
        detected_language = detect_language(code)
        
        # If a specific language was selected (not auto), validate it matches the detected language
        if selected_language != 'auto' and detected_language != 'unknown' and selected_language != detected_language:
            return jsonify({'error': f'The code appears to be written in {detected_language}, but you selected {selected_language}. Please select the correct language or use auto-detect.'}), 400
            
        # Use the detected language if auto was selected
        language = detected_language if selected_language == 'auto' else selected_language
        
        # Run the analysis
        result = run_analysis(code)
        return jsonify(result)
    except ValueError as e:
        # Handle validation errors
        logging.error(f"Validation error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        # Handle unexpected errors
        logging.error(f"Unexpected error: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/api/refactor', methods=['POST'])
def refactor():
    data = request.json
    code = data.get('code', '')
    language = data.get('language', 'auto')
    
    if not code:
        return jsonify({'error': 'No code provided'}), 400
    
    try:
        # Auto-detect language if not specified
        if language == 'auto':
            language = detect_language(code)
        
        # Generate refactored code using AI
        refactored_code, improvements = generate_refactored_code(code, language)
        
        return jsonify({
            'refactored_code': refactored_code,
            'improvements': improvements
        })
    except Exception as e:
        logging.error(f"Refactoring error: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': f"An error occurred during refactoring: {str(e)}"}), 500

def generate_refactored_code(code, language):
    """Generate refactored code using AI."""
    if not API_KEY:
        return code, ["AI refactoring not available without API key"]
    
    try:
        prompt = f"""
        You are an expert code refactorer. Refactor the following {language} code to make it more efficient, 
        readable, and following best practices. Return ONLY the refactored code without any explanations, comments or markdown.
        
        {code}
        """
        
        improvements_prompt = f"""
        Analyze the following {language} code and list 3-5 specific improvements that could be made to make it more efficient, 
        readable, and following best practices. Return ONLY a list of improvements, one per line.
        
        {code}
        """
        
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Get refactored code
        refactored_response = model.generate_content(prompt)
        refactored_code = refactored_response.text.strip()
        
        # Get improvements
        improvements_response = model.generate_content(improvements_prompt)
        improvements_text = improvements_response.text.strip()
        improvements = [line.strip() for line in improvements_text.split('\n') if line.strip()]
        
        return refactored_code, improvements
    except Exception as e:
        logging.error(f"AI refactoring error: {str(e)}")
        return code, [f"Error during refactoring: {str(e)}"]

if __name__ == '__main__':
    app.run(debug=True, port=5000)
