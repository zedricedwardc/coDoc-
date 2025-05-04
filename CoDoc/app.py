from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
import os
import logging
import traceback
from dotenv import load_dotenv
import google.generativeai as genai
import re

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

@app.route('/challenge')
def challenge():
    return render_template('challenge.html')

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

@app.route('/api/challenge/submit', methods=['POST'])
def submit_challenge():
    data = request.json
    code = data.get('code', '')
    challenge_id = data.get('challenge_id', '')
    language = data.get('language', 'python')
    
    if not code or not challenge_id:
        return jsonify({'error': 'Missing code or challenge ID'}), 400
    
    try:
        # Check if the code is empty or just contains the template
        if is_template_code(code, language):
            return jsonify({'error': 'Please implement your solution before submitting.'}), 400
            
        # Check if the code contains the required function for the challenge
        if not has_required_function(code, challenge_id, language):
            return jsonify({'error': 'Your solution must implement the required function.'}), 400
        
        # Run the analysis to get complexity
        result = run_analysis(code)
        
        # Calculate score based on time and space complexity
        time_complexity = result['native_analysis']['time_complexity']
        space_complexity = result['native_analysis']['space_complexity']
        
        # Simple scoring formula: lower complexity = higher score
        # Base score of 100, subtract complexity values
        score = max(0, 100 - (time_complexity * 5) - (space_complexity * 2))
        
        # Add feedback based on complexity
        feedback = []
        if time_complexity < 10:
            feedback.append("Great job! Your time complexity is excellent.")
        elif time_complexity < 20:
            feedback.append("Your time complexity is good, but could be improved.")
        else:
            feedback.append("Your time complexity needs improvement. Try to optimize your algorithm.")
            
        if space_complexity < 10:
            feedback.append("Your space complexity is excellent.")
        elif space_complexity < 20:
            feedback.append("Your space complexity is good, but could be improved.")
        else:
            feedback.append("Your space complexity needs improvement. Try to reduce memory usage.")
        
        return jsonify({
            'score': score,
            'time_complexity': time_complexity,
            'space_complexity': space_complexity,
            'feedback': feedback
        })
    except Exception as e:
        logging.error(f"Challenge submission error: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': f"An error occurred while evaluating your solution: {str(e)}"}), 500

def is_template_code(code, language):
    """Check if the code is just the template."""
    if language == 'python':
        # Check if code only contains comments and pass statements
        if '# Your code here' in code and 'pass' in code and not re.search(r'return\s+\w+', code):
            # Check if there's any substantial code beyond the template
            lines = [line.strip() for line in code.split('\n') if line.strip() and not line.strip().startswith('#')]
            meaningful_lines = [line for line in lines if line != 'pass' and 'def ' not in line]
            return len(meaningful_lines) == 0
    elif language == 'javascript':
        # Check if code only contains comments
        if '// Your code here' in code and not re.search(r'return\s+\w+', code):
            # Check if there's any substantial code beyond the template
            lines = [line.strip() for line in code.split('\n') if line.strip() and not line.strip().startswith('//')]
            meaningful_lines = [line for line in lines if 'function ' not in line and '{' not in line and '}' not in line]
            return len(meaningful_lines) == 0
    
    # If we can't determine, assume it's not just a template
    return False

def has_required_function(code, challenge_id, language):
    """Check if the code contains the required function for the challenge."""
    required_functions = {
        '1': {'python': 'def two_sum', 'javascript': 'function twoSum'},
        '2': {'python': 'def longest_palindrome', 'javascript': 'function longestPalindrome'},
        '3': {'python': 'def max_path_sum', 'javascript': 'function maxPathSum'},
    }
    
    if challenge_id in required_functions and language in required_functions[challenge_id]:
        return required_functions[challenge_id][language] in code
    
    return True  # If we don't have a specific check, assume it's valid

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
