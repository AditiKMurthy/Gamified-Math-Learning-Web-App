import base64
import io
import os
import random
import json
import sys
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, render_template
import pandas as pd


import bcrypt
import gspread
from dotenv import load_dotenv

# Ensure secrets and sensitive files are not pushed to Git
# Add .env and service_account.json to .gitignore if not already present
# Example .gitignore entries:
# .env
# service_account.json

# Load environment variables from .env file
load_dotenv()
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Add the logic/python directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'logic', 'python'))

# Import the Python modules
try:
    from logic.python import algebra
    from logic.python import real_numbers
    from logic.python import stats
    from logic.python import surface_areas_volumes
    from logic.python import triangles
    PYTHON_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import Python modules: {e}")
    PYTHON_MODULES_AVAILABLE = False

app = Flask(__name__)

# Google Sheets setup
SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE', 'service_account.json')
SCOPES = os.getenv('SCOPES', 'https://www.googleapis.com/auth/spreadsheets,https://www.googleapis.com/auth/drive').split(',')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID', '1FFLrl7f24QKM3xpQSYwib-NmlSE5s4Mb7iXFeVQVYIg')
SHEET_NAME = os.getenv('SHEET_NAME', 'login')
try:
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )
    gspread_client = gspread.authorize(credentials)
    sheet_service = build('sheets', 'v4', credentials=credentials)
    spreadsheet = gspread_client.open_by_key(SPREADSHEET_ID)
    login_sheet = spreadsheet.worksheet(SHEET_NAME)
    GOOGLE_SHEETS_AVAILABLE = True
    print("Google Sheets integration enabled")
except Exception as e:
    print(f"Warning: Google Sheets not available: {e}")
    GOOGLE_SHEETS_AVAILABLE = False

# Fallback: Simple in-memory user storage (for development/testing)
FALLBACK_USERS = {}

# Fetch users from login sheet
def get_users():
    if not GOOGLE_SHEETS_AVAILABLE:
        # Return fallback users
        return [[username, user_data['password_hash'], user_data['name']] 
                for username, user_data in FALLBACK_USERS.items()]
    try:
        result = sheet_service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f'{SHEET_NAME}!A2:C'
        ).execute()
        return result.get('values', [])
    except Exception as e:
        print(f"Error fetching users from Google Sheets: {e}")
        return []

# Append new user
def append_user(username, password_hash, name):
    if not GOOGLE_SHEETS_AVAILABLE:
        # Store in fallback storage
        FALLBACK_USERS[username] = {
            'password_hash': password_hash.decode(),
            'name': name
        }
        print(f"DEBUG: User '{username}' stored in fallback storage")
        return True
    try:
        body = {'values': [[username, password_hash.decode(), name]]}
        sheet_service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=f'{SHEET_NAME}!A:C',
            valueInputOption='RAW',
            body=body
        ).execute()
        return True
    except Exception as e:
        print(f"Error appending user to Google Sheets: {e}")
        return False

# Create a worksheet if not already exists
def get_or_create_user_worksheet(username):
    """Get existing worksheet or create new one for the user with quiz headers"""
    if not GOOGLE_SHEETS_AVAILABLE:
        print("Google Sheets not available, using fallback mode")
        return f"fallback://{username}_worksheet"
        
    try:
        # Clean username for worksheet name (remove special characters)
        worksheet_name = username.replace(' ', '_').replace('-', '_').replace('.', '_')
        worksheet_name = ''.join(c for c in worksheet_name if c.isalnum() or c == '_')
        print(f"DEBUG: Looking for worksheet: {worksheet_name}")
        
        # Get all existing worksheets to check if it already exists
        all_worksheets = [ws.title for ws in spreadsheet.worksheets()]
        print(f"DEBUG: All existing worksheets: {all_worksheets}")
        
        # Check if worksheet already exists using improved logic
        # Try exact match first
        if worksheet_name in all_worksheets:
            print(f"DEBUG: Worksheet '{worksheet_name}' exists in list, trying to access it...")
            try:
                existing_worksheet = spreadsheet.worksheet(worksheet_name)
                print(f"DEBUG: Successfully accessed existing worksheet: {existing_worksheet.title}")
                return f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit#gid={existing_worksheet.id}"
            except Exception as access_error:
                print(f"DEBUG: Could not access existing worksheet '{worksheet_name}': {str(access_error)}")
        
        # Try case-insensitive match
        for ws_name in all_worksheets:
            if ws_name.lower() == worksheet_name.lower():
                print(f"DEBUG: Found case-insensitive match: {ws_name}, trying to access it...")
                try:
                    existing_worksheet = spreadsheet.worksheet(ws_name)
                    print(f"DEBUG: Successfully accessed existing worksheet: {existing_worksheet.title}")
                    return f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit#gid={existing_worksheet.id}"
                except Exception as access_error:
                    print(f"DEBUG: Could not access existing worksheet '{ws_name}': {str(access_error)}")
        
        # Try partial match
        for ws_name in all_worksheets:
            if worksheet_name.lower() in ws_name.lower() or ws_name.lower() in worksheet_name.lower():
                print(f"DEBUG: Found partial match: {ws_name}, trying to access it...")
                try:
                    existing_worksheet = spreadsheet.worksheet(ws_name)
                    print(f"DEBUG: Successfully accessed existing worksheet: {existing_worksheet.title}")
                    return f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit#gid={existing_worksheet.id}"
                except Exception as access_error:
                    print(f"DEBUG: Could not access existing worksheet '{ws_name}': {str(access_error)}")
        
        print(f"DEBUG: No existing worksheet found for '{worksheet_name}', will create new one")
        
        # Create new worksheet (handle potential conflicts)
        print(f"DEBUG: Creating new worksheet: {worksheet_name}")
        try:
            worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=1000, cols=8)
            print(f"DEBUG: Created new worksheet: {worksheet.title}")
        except Exception as create_error:
            print(f"DEBUG: Error creating worksheet '{worksheet_name}': {str(create_error)}")
            # Try with a suffix if there's a conflict
            for i in range(1, 10):
                try:
                    new_name = f"{worksheet_name}_{i}"
                    print(f"DEBUG: Trying alternative name: {new_name}")
                    worksheet = spreadsheet.add_worksheet(title=new_name, rows=1000, cols=8)
                    print(f"DEBUG: Created worksheet with alternative name: {worksheet.title}")
                    break
                except Exception as alt_error:
                    print(f"DEBUG: Failed to create worksheet '{new_name}': {str(alt_error)}")
                    continue
            else:
                print(f"DEBUG: Could not create worksheet with any name")
                return None
        
        # Add headers to the first row
        headers = [
            'Topic',
            'Level', 
            'Question',
            'Correct Answer',
            "User's Answer",
            'Status (Correct/Wrong)',
            'Time Used (seconds)',
            'Timestamp'
        ]
        
        worksheet.append_row(headers)
        print(f"DEBUG: Added headers to new worksheet")
        
        # Return worksheet URL
        return f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit#gid={worksheet.id}"
        
    except Exception as e:
        print(f"Error creating worksheet for {username}: {str(e)}")
        print(f"DEBUG: Full error details: {type(e).__name__}: {str(e)}")
        return None

def get_user_worksheet(username):
    """Get user's worksheet without creating a new one"""
    if not GOOGLE_SHEETS_AVAILABLE:
        print("Google Sheets not available, using fallback mode")
        return f"fallback://{username}_worksheet"
        
    try:
        # Clean username for worksheet name
        worksheet_name = username.replace(' ', '_').replace('-', '_').replace('.', '_')
        worksheet_name = ''.join(c for c in worksheet_name if c.isalnum() or c == '_')
        print(f"DEBUG: Getting worksheet: {worksheet_name}")
        
        # Get all worksheets to find the correct one
        all_worksheets = [ws.title for ws in spreadsheet.worksheets()]
        print(f"DEBUG: All available worksheets: {all_worksheets}")
        
        # Try exact match first
        if worksheet_name in all_worksheets:
            print(f"DEBUG: Found exact match: {worksheet_name}")
            worksheet = spreadsheet.worksheet(worksheet_name)
            print(f"DEBUG: Retrieved worksheet: {worksheet.title}")
            return worksheet
        
        # Try case-insensitive match
        for ws_name in all_worksheets:
            if ws_name.lower() == worksheet_name.lower():
                print(f"DEBUG: Found case-insensitive match: {ws_name}")
                worksheet = spreadsheet.worksheet(ws_name)
                print(f"DEBUG: Retrieved worksheet: {worksheet.title}")
                return worksheet
        
        # Try partial match (in case there are special characters or variations)
        for ws_name in all_worksheets:
            if worksheet_name.lower() in ws_name.lower() or ws_name.lower() in worksheet_name.lower():
                print(f"DEBUG: Found partial match: {ws_name}")
                worksheet = spreadsheet.worksheet(ws_name)
                print(f"DEBUG: Retrieved worksheet: {worksheet.title}")
                return worksheet
        
        print(f"DEBUG: No worksheet found for {username} (cleaned: {worksheet_name})")
        return None
        
    except Exception as e:
        print(f"DEBUG: Could not get worksheet for {username}: {str(e)}")
        return None

# Log quiz attempt to Google Sheets
def log_quiz_attempt(username, topic, level, question, correct_answer, user_answer, status, time_used):
    """Log a single quiz attempt to the user's worksheet"""
    print(f"DEBUG: Attempting to log quiz attempt for {username}")
    
    if not GOOGLE_SHEETS_AVAILABLE:
        print("Google Sheets not available, using fallback mode - quiz data logged to console")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"FALLBACK QUIZ LOG: {username} | {topic} | {level} | {question[:50]}... | Correct: {correct_answer} | User: {user_answer} | Status: {status} | Time: {time_used}s | {timestamp}")
        return True
        
    try:
        # Get user's worksheet (don't create new one, just get existing)
        worksheet = get_user_worksheet(username)
        
        if worksheet is None:
            print(f"DEBUG: Could not get worksheet for {username}, attempting to create one...")
            # Try to create worksheet if it doesn't exist
            sheet_url = get_or_create_user_worksheet(username)
            if sheet_url:
                worksheet = get_user_worksheet(username)
                if worksheet is None:
                    print(f"DEBUG: Still could not get worksheet after creation attempt")
                    return False
            else:
                print(f"DEBUG: Failed to create worksheet for {username}")
                return False
        
        print(f"DEBUG: Using worksheet: {worksheet.title}")
        
        # Prepare row data
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row_data = [
            topic,
            level,
            question,
            str(correct_answer),
            str(user_answer),
            status,
            str(time_used),
            timestamp
        ]
        print(f"DEBUG: Row data: {row_data}")
        
        # Append the row
        worksheet.append_row(row_data)
        print(f"DEBUG: Successfully appended row to worksheet")
        
        return True
        
    except Exception as e:
        print(f"Error logging quiz attempt for {username}: {str(e)}")
        print(f"DEBUG: Full error details: {type(e).__name__}: {str(e)}")
        return False

@app.route('/api/quiz/log-attempt', methods=['POST'])
def log_quiz_attempt_api():
    """API endpoint to log quiz attempts to Google Sheets"""
    print(f"DEBUG: Received quiz log attempt request")
    try:
        data = request.get_json()
        print(f"DEBUG: Request data: {data}")
        
        username = data.get('username')
        topic = data.get('topic')
        level = data.get('level')
        question = data.get('question')
        correct_answer = data.get('correct_answer')
        user_answer = data.get('user_answer')
        status = data.get('status')  # 'Correct' or 'Wrong'
        time_used = data.get('time_used')  # seconds
        
        print(f"DEBUG: Extracted data - username: {username}, topic: {topic}, level: {level}")
        print(f"DEBUG: question: {question[:50]}..., correct: {correct_answer}, user: {user_answer}, status: {status}, time: {time_used}")
        
        if not all([username, topic, level, question, correct_answer, user_answer, status, time_used is not None]):
            print(f"DEBUG: Missing required fields")
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        # Log the attempt
        success = log_quiz_attempt(username, topic, level, question, correct_answer, user_answer, status, time_used)
        
        if success:
            print(f"DEBUG: Quiz attempt logged successfully")
            return jsonify({'success': True, 'message': 'Quiz attempt logged successfully'})
        else:
            print(f"DEBUG: Failed to log quiz attempt")
            return jsonify({'success': False, 'message': 'Failed to log quiz attempt'}), 500
            
    except Exception as e:
        print(f"DEBUG: Exception in log_quiz_attempt_api: {str(e)}")
        return jsonify({'success': False, 'message': f'Error logging quiz attempt: {str(e)}'}), 500

@app.route('/api/test-sheets', methods=['GET'])
def test_sheets():
    """Test endpoint to verify Google Sheets is working"""
    try:
        if not GOOGLE_SHEETS_AVAILABLE:
            return jsonify({'success': False, 'message': 'Google Sheets not available'})
        
        # Try to access the spreadsheet
        spreadsheet_info = spreadsheet.title
        worksheets = [ws.title for ws in spreadsheet.worksheets()]
        
        # Get all users from the login sheet
        users = get_users()
        
        return jsonify({
            'success': True,
            'message': 'Google Sheets is working',
            'spreadsheet_title': spreadsheet_info,
            'worksheets': worksheets,
            'users_in_login_sheet': users,
            'user_count': len(users)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Google Sheets error: {str(e)}'})

@app.route('/api/test-quiz-log', methods=['POST'])
def test_quiz_log():
    """Test endpoint to manually test quiz logging"""
    try:
        if not GOOGLE_SHEETS_AVAILABLE:
            return jsonify({'success': False, 'message': 'Google Sheets not available'})
        
        data = request.get_json()
        username = data.get('username', 'testuser')
        
        # Test data
        test_data = {
            'username': username,
            'topic': 'algebra',
            'level': 'easy',
            'question': 'Test question for debugging',
            'correct_answer': 'A',
            'user_answer': 'B',
            'status': 'Wrong',
            'time_used': 45
        }
        
        print(f"DEBUG: Testing quiz log with data: {test_data}")
        
        # Try to log the test attempt
        success = log_quiz_attempt(
            test_data['username'],
            test_data['topic'],
            test_data['level'],
            test_data['question'],
            test_data['correct_answer'],
            test_data['user_answer'],
            test_data['status'],
            test_data['time_used']
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Test quiz log successful',
                'test_data': test_data
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Test quiz log failed',
                'test_data': test_data
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Test quiz log error: {str(e)}'
        })

@app.route('/api/test-worksheet/<username>', methods=['GET'])
def test_worksheet(username):
    """Test endpoint to check user's worksheet status"""
    try:
        if not GOOGLE_SHEETS_AVAILABLE:
            return jsonify({'success': False, 'message': 'Google Sheets not available'})
        
        # Clean username
        clean_username = username.replace(' ', '_').replace('-', '_').replace('.', '_')
        clean_username = ''.join(c for c in clean_username if c.isalnum() or c == '_')
        
        # Get all worksheets to see what exists
        all_worksheets = [ws.title for ws in spreadsheet.worksheets()]
        
        print(f"DEBUG: All worksheets: {all_worksheets}")
        print(f"DEBUG: Looking for worksheet: '{clean_username}'")
        print(f"DEBUG: Original username: '{username}'")
        
        # Check if worksheet exists in the list
        worksheet_exists = clean_username in all_worksheets
        
        # Try to get existing worksheet
        worksheet = get_user_worksheet(username)
        
        if worksheet:
            # Get some data from the worksheet
            try:
                all_values = worksheet.get_all_values()
                row_count = len(all_values)
                header_row = all_values[0] if all_values else []
                
                return jsonify({
                    'success': True,
                    'message': f'Worksheet found for {username}',
                    'worksheet_name': worksheet.title,
                    'row_count': row_count,
                    'header_row': header_row,
                    'clean_username': clean_username,
                    'worksheet_exists_in_list': worksheet_exists,
                    'all_worksheets': all_worksheets
                })
            except Exception as e:
                return jsonify({
                    'success': True,
                    'message': f'Worksheet found but error reading data: {str(e)}',
                    'worksheet_name': worksheet.title,
                    'clean_username': clean_username,
                    'worksheet_exists_in_list': worksheet_exists,
                    'all_worksheets': all_worksheets
                })
        else:
            # Try to create worksheet
            print(f"DEBUG: Attempting to create worksheet for {username}")
            sheet_url = get_or_create_user_worksheet(username)
            if sheet_url:
                return jsonify({
                    'success': True,
                    'message': f'Created new worksheet for {username}',
                    'sheet_url': sheet_url,
                    'clean_username': clean_username,
                    'worksheet_exists_in_list': worksheet_exists,
                    'all_worksheets': all_worksheets
                })
            else:
                return jsonify({
                    'success': False,
                    'message': f'Could not create worksheet for {username}',
                    'clean_username': clean_username,
                    'worksheet_exists_in_list': worksheet_exists,
                    'all_worksheets': all_worksheets
                })
                
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Test worksheet error: {str(e)}'
        })

@app.route('/api/find-worksheet/<username>', methods=['GET'])
def find_worksheet(username):
    """Find the exact worksheet name for a user"""
    try:
        if not GOOGLE_SHEETS_AVAILABLE:
            return jsonify({'success': False, 'message': 'Google Sheets not available'})
        
        # Clean username
        clean_username = username.replace(' ', '_').replace('-', '_').replace('.', '_')
        clean_username = ''.join(c for c in clean_username if c.isalnum() or c == '_')
        
        # Get all worksheets
        all_worksheets = [ws.title for ws in spreadsheet.worksheets()]
        
        # Find potential matches
        exact_matches = [ws for ws in all_worksheets if ws == clean_username]
        case_insensitive_matches = [ws for ws in all_worksheets if ws.lower() == clean_username.lower()]
        partial_matches = [ws for ws in all_worksheets if clean_username.lower() in ws.lower() or ws.lower() in clean_username.lower()]
        
        return jsonify({
            'success': True,
            'username': username,
            'clean_username': clean_username,
            'all_worksheets': all_worksheets,
            'exact_matches': exact_matches,
            'case_insensitive_matches': case_insensitive_matches,
            'partial_matches': partial_matches
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Find worksheet error: {str(e)}'
        })

# ---------------- QUESTION LOADER ---------------- #
LOGIC_FOLDER = os.path.join(os.path.dirname(__file__), 'logic')

# Load all questions into memory    
def load_questions():
    questions_by_topic = {}
    for filename in os.listdir(LOGIC_FOLDER):
        if filename.endswith(".json"):
            topic_name = filename.replace("_mcqs_by_level.json", "").replace(".json", "")
            try:
                with open(os.path.join(LOGIC_FOLDER, filename), "r", encoding='utf-8') as f:
                    data = json.load(f)
                    questions_by_topic[topic_name.lower()] = data
            except Exception as e:
                print(f"Failed to load {filename}: {e}")
    return questions_by_topic

QUESTIONS_DB = load_questions()

# ---------------- STATIC FILES ---------------- #
@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory('assets', filename)

@app.route('/styles.css')
def serve_styles():
    return send_from_directory('templates', 'styles.css')

@app.route('/script.js')
def serve_script():
    return send_from_directory('templates', 'script.js')

# ---------------- ROUTES ---------------- #
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

@app.route('/result')
def result():
    return render_template('result.html')

# ---------------- PYTHON MODULE APIs ---------------- #
@app.route('/api/python/algebra/<level>', methods=['GET'])
def get_algebra_question(level):
    """Get algebra question from Python module"""
    if not PYTHON_MODULES_AVAILABLE:
        return jsonify({"error": "Python modules not available"}), 500
    
    try:
        question = algebra.get_question(level)
        return jsonify({
            "topic": "algebra",
            "level": level,
            "question": question
        })
    except Exception as e:
        return jsonify({"error": f"Error getting algebra question: {str(e)}"}), 500

@app.route('/api/python/algebra/quiz/<level>', methods=['GET'])
def get_algebra_quiz_questions(level):
    """Get 5 algebra questions for quiz from JSON file"""
    try:
        # Load algebra questions from JSON file
        json_file_path = os.path.join(LOGIC_FOLDER, 'pyqs', 'Algebra_CBSE_MCQ_by_Difficulty_FULL.json')
        
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Get questions for the specified level
        if level.lower() in data and data[level.lower()]:
            # Select 5 random questions from the available questions
            available_questions = data[level.lower()]
            if len(available_questions) >= 5:
                selected_questions = random.sample(available_questions, 5)
            else:
                # If less than 5 questions available, use all available
                selected_questions = available_questions
            
            return jsonify({
                "topic": "algebra",
                "level": level,
                "total_questions": len(selected_questions),
                "questions": selected_questions
            })
        else:
            return jsonify({"error": f"No questions available for level '{level}'"}), 404
            
    except FileNotFoundError:
        return jsonify({"error": "Algebra questions JSON file not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Error loading algebra questions: {str(e)}"}), 500

@app.route('/api/python/real_numbers/<level>', methods=['GET'])
def get_real_numbers_question(level):
    """Get real numbers question from Python module"""
    if not PYTHON_MODULES_AVAILABLE:
        return jsonify({"error": "Python modules not available"}), 500
    
    try:
        question = real_numbers.get_question(level)
        return jsonify({
            "topic": "real_numbers",
            "level": level,
            "question": question
        })
    except Exception as e:
        return jsonify({"error": f"Error getting real numbers question: {str(e)}"}), 500

@app.route('/api/python/stats/<level>', methods=['GET'])
def get_stats_question(level):
    """Get statistics question from Python module"""
    if not PYTHON_MODULES_AVAILABLE:
        return jsonify({"error": "Python modules not available"}), 500
    
    try:
        # Get mode from query parameter, default to 'static'
        mode = request.args.get('mode', 'static')
        question = stats.get_question(level=level, mode=mode)
        return jsonify({
            "topic": "statistics",
            "level": level,
            "mode": mode,
            "question": question
        })
    except Exception as e:
        return jsonify({"error": f"Error getting statistics question: {str(e)}"}), 500

@app.route('/api/python/surface_areas_volumes/<level>', methods=['GET'])
def get_surface_areas_volumes_question(level):
    """Get surface areas and volumes question from Python module"""
    if not PYTHON_MODULES_AVAILABLE:
        return jsonify({"error": "Python modules not available"}), 500
    
    try:
        question = surface_areas_volumes.get_question(level)
        return jsonify({
            "topic": "surface_areas_volumes",
            "level": level,
            "question": question
        })
    except Exception as e:
        return jsonify({"error": f"Error getting surface areas and volumes question: {str(e)}"}), 500

@app.route('/api/python/triangles/<level>', methods=['GET'])
def get_triangles_question(level):
    """Get triangles question from Python module"""
    if not PYTHON_MODULES_AVAILABLE:
        return jsonify({"error": "Python modules not available"}), 500
    
    try:
        question = triangles.get_question(level)
        return jsonify({
            "topic": "triangles",
            "level": level,
            "question": question
        })
    except Exception as e:
        return jsonify({"error": f"Error getting triangles question: {str(e)}"}), 500

# ---------------- UNIFIED PYTHON API ---------------- #
@app.route('/api/python/question/<topic>/<level>', methods=['GET'])
def get_python_question(topic, level):
    """Unified API to get questions from any Python module"""
    if not PYTHON_MODULES_AVAILABLE:
        return jsonify({"error": "Python modules not available"}), 500
    
    topic_mapping = {
        'algebra': algebra,
        'real_numbers': real_numbers,
        'statistics': stats,
        'surface_areas_volumes': surface_areas_volumes,
        'triangles': triangles
    }
    
    if topic not in topic_mapping:
        return jsonify({"error": f"Topic '{topic}' not found"}), 404
    
    try:
        module = topic_mapping[topic]
        
        # Handle special case for stats module which has mode parameter
        if topic == 'statistics':
            mode = request.args.get('mode', 'static')
            question = module.get_question(level=level, mode=mode)
        else:
            question = module.get_question(level)
        
        return jsonify({
            "topic": topic,
            "level": level,
            "question": question
        })
    except Exception as e:
        return jsonify({"error": f"Error getting {topic} question: {str(e)}"}), 500

@app.route('/api/python/quiz/<topic>/<level>', methods=['GET'])
def get_quiz_questions(topic, level):
    """Get 5 quiz questions for any topic from JSON files"""
    try:
        # Map topic names to JSON file names
        topic_to_json = {
            'algebra': 'Algebra_CBSE_MCQ_by_Difficulty_FULL.json',
            'real_numbers': 'Real_Numbers_CBSE_MCQ_by_Difficulty_FULL.json',
            'statistics': 'Statistics_CBSE_MCQ_by_Difficulty_FULL.json',
            'surface_areas_volumes': 'Surface_Areas_Volumes_CBSE_MCQ_by_Difficulty_FULL.json',
            'triangles': 'Triangles_CBSE_MCQ_by_Difficulty_FULL.json'
        }
        
        if topic not in topic_to_json:
            return jsonify({"error": f"Topic '{topic}' not supported for quiz generation"}), 404
        
        json_filename = topic_to_json[topic]
        json_file_path = os.path.join(LOGIC_FOLDER, 'pyqs', json_filename)
        
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Get questions for the specified level
        if level.lower() in data and data[level.lower()]:
            # Select 5 random questions from the available questions
            available_questions = data[level.lower()]
            if len(available_questions) >= 5:
                selected_questions = random.sample(available_questions, 5)
            else:
                # If less than 5 questions available, use all available
                selected_questions = available_questions
            
            return jsonify({
                "topic": topic,
                "level": level,
                "total_questions": len(selected_questions),
                "questions": selected_questions
            })
        else:
            return jsonify({"error": f"No questions available for {topic} level '{level}'"}), 404
            
    except FileNotFoundError:
        return jsonify({"error": f"Questions JSON file for topic '{topic}' not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Error loading {topic} questions: {str(e)}"}), 500

# ---------------- AVAILABLE TOPICS API ---------------- #
@app.route('/api/python/topics', methods=['GET'])
def get_available_python_topics():
    """Get list of available topics from Python modules"""
    if not PYTHON_MODULES_AVAILABLE:
        return jsonify({"error": "Python modules not available"}), 500
    
    topics = {
        'algebra': 'Algebra questions',
        'real_numbers': 'Real Numbers questions',
        'statistics': 'Statistics questions (supports static and dynamic modes)',
        'surface_areas_volumes': 'Surface Areas and Volumes questions',
        'triangles': 'Triangles questions'
    }
    
    return jsonify({
        "available_topics": topics,
        "python_modules_available": True
    })

# ---------------- EXISTING APIs ---------------- #
@app.route('/api/topics', methods=['GET'])
def list_topics():
    return jsonify({"available_topics": list(QUESTIONS_DB.keys())})

@app.route('/api/questions/<topic>', methods=['GET'])
def get_questions(topic):
    topic_key = topic.lower().replace(" ", "_")
    topic_data = None

    for key in QUESTIONS_DB:
        if topic_key in key:
            topic_data = QUESTIONS_DB[key]
            break

    if not topic_data:
        return jsonify({"error": "Topic not found"}), 404

    levels = ["easy", "medium", "hard"]
    output = {}

    for level in levels:
        if level in topic_data and isinstance(topic_data[level], list):
            output[level] = random.sample(topic_data[level], min(2, len(topic_data[level])))
        else:
            output[level] = []

    return jsonify({
        "topic": topic,
        "questions": output
    })

@app.route('/api/quiz/submit', methods=['POST'])
def submit_quiz():
    try:
        data = request.get_json()
        answers = data.get('answers', {})
        topic = data.get('topic', '')
        
        # Calculate score (simple implementation)
        correct_answers = 0
        total_questions = len(answers)
        
        # For now, just return a basic result
        # You can implement more sophisticated scoring logic here
        score_percentage = random.randint(60, 95)  # Placeholder
        
        return jsonify({
            "success": True,
            "score": score_percentage,
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "topic": topic
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- GOOGLE SHEETS AUTHENTICATION APIs ---------------- #
@app.route('/api/register', methods=['POST'])
def register():
    """Register new user with Google Sheets exclusively"""
    try:
        data = request.get_json()
        username = data.get('username', '').lower().strip()
        password = data.get('password', '').strip()
        name = data.get('name', username)

        print(f"DEBUG: Registration attempt - Username: '{username}', Name: '{name}'")

        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password required'}), 400

        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters long'}), 400

        # Check if user already exists in Google Sheets
        users = get_users()
        print(f"DEBUG: Existing users in sheet: {users}")
        if any(user[0].lower() == username for user in users):
            return jsonify({'success': False, 'message': 'Username already registered'}), 400

        # Hash password with bcrypt and add user to Google Sheets
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        print(f"DEBUG: Password hash created: {password_hash.decode()[:20]}...")
        
        if append_user(username, password_hash, name):
            print(f"DEBUG: User '{username}' successfully added to Google Sheets")
            # Create user worksheet upon registration with headers
            sheet_url = get_or_create_user_worksheet(username)
            return jsonify({
                'success': True, 
                'message': 'Registration successful',
                'sheet_url': sheet_url
            })
        else:
            print(f"DEBUG: Failed to add user '{username}' to Google Sheets")
            return jsonify({'success': False, 'message': 'Failed to register user'}), 500

    except Exception as e:
        print(f"DEBUG: Registration exception: {str(e)}")
        return jsonify({'success': False, 'message': f'Registration error: {str(e)}'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Login user with Google Sheets authentication"""
    try:
        data = request.get_json()
        username = data.get('username', '').lower().strip()
        password = data.get('password', '').strip()

        print(f"DEBUG: Login attempt - Username: '{username}'")

        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password required'}), 400

        # Check user credentials in Google Sheets
        users = get_users()
        print(f"DEBUG: Users from sheet: {users}")
        
        for user in users:
            if len(user) < 2:
                print(f"DEBUG: Skipping incomplete row: {user}")
                continue  # Skip incomplete rows

            stored_username = user[0].strip()
            stored_hash = user[1].strip()
            
            print(f"DEBUG: Comparing '{username}' with stored '{stored_username}'")

            if stored_username == username:
                print(f"DEBUG: Username match found! Checking password...")
                if bcrypt.checkpw(password.encode(), stored_hash.encode()):
                    print(f"DEBUG: Password match! Login successful for '{username}'")
                    # Get or create user worksheet (with headers)
                    sheet_url = get_or_create_user_worksheet(username)
                    return jsonify({
                        'success': True,
                        'message': 'Login successful',
                        'sheet_url': sheet_url
                    })
                else:
                    print(f"DEBUG: Password mismatch for user '{username}'")
                    return jsonify({'success': False, 'message': 'Invalid password'}), 400

        print(f"DEBUG: No username match found for '{username}'")
        return jsonify({'success': False, 'message': 'User not found'}), 400

    except Exception as e:
        print(f"DEBUG: Login exception: {str(e)}")
        return jsonify({'success': False, 'message': f'Login error: {str(e)}'}), 500

# ---------------- RUN APP ---------------- #
if __name__ == '__main__':
    print("Starting iSpace Math Flask App...")
    print(f"Python modules available: {PYTHON_MODULES_AVAILABLE}")
    if PYTHON_MODULES_AVAILABLE:
        print("Available Python modules: algebra, real_numbers, stats, surface_areas_volumes, triangles")
    app.run(debug=True, port=8001, host='0.0.0.0')
