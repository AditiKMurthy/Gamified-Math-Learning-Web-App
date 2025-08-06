import random
import json
import os

# ---------- Load Questions from JSON ----------
def load_algebra_questions():
    """Load algebra questions from JSON file"""
    json_file_path = os.path.join(os.path.dirname(__file__), '..', 'pyqs', 'Algebra_CBSE_MCQ_by_Difficulty_FULL.json')
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except Exception as e:
        print(f"Error loading algebra questions from JSON: {e}")
        return None

# ---------- Get Questions by Level ----------
def get_easy_question():
    """Get a random easy algebra question from JSON"""
    questions_data = load_algebra_questions()
    if questions_data and 'easy' in questions_data and questions_data['easy']:
        return random.choice(questions_data['easy'])
    else:
        return {"error": "No easy questions available"}

def get_medium_question():
    """Get a random medium algebra question from JSON"""
    questions_data = load_algebra_questions()
    if questions_data and 'medium' in questions_data and questions_data['medium']:
        return random.choice(questions_data['medium'])
    else:
        return {"error": "No medium questions available"}

def get_hard_question():
    """Get a random hard algebra question from JSON"""
    questions_data = load_algebra_questions()
    if questions_data and 'hard' in questions_data and questions_data['hard']:
        return random.choice(questions_data['hard'])
    else:
        return {"error": "No hard questions available"}

# ---------- Unified Interface ----------
def get_question(level="easy"):
    level = level.lower()
    if level == "easy":
        return get_easy_question()
    elif level == "medium":
        return get_medium_question()
    elif level == "hard":
        return get_hard_question()
    else:
        return {"error": "Invalid level. Use 'easy', 'medium', or 'hard'."}

# ---------- CLI Testing ----------
if __name__ == "__main__":
    for level in ["easy", "medium", "hard"]:
        print(f"\n📘 Algebra | Level: {level.upper()}")
        q = get_question(level)
        if "error" in q:
            print(q["error"])
        else:
            print("Q:", q["question"])
            for opt, val in q["options"].items():
                print(f"  {opt}: {val}")
            print("✅ Answer:", q["answer"])
