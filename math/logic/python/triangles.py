import json
import random
import os
import math

# ---------- Load Questions from File ----------
def load_mcqs_by_level():
    file_path = os.path.join(os.path.dirname(__file__), '..', 'pyqs','triangle_mcqs_by_level.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading MCQs: {e}")
        return {"easy": [], "medium": [], "hard": []}

# ---------- Generate Dynamic Questions ----------
def generate_easy_question():
    """Generate easy triangle questions"""
    question_types = [
        "area_basic",
        "perimeter", 
        "angles"
    ]
    
    q_type = random.choice(question_types)
    
    if q_type == "area_basic":
        base = random.randint(3, 10)
        height = random.randint(4, 12)
        area = 0.5 * base * height
        question = f"What is the area of a triangle with base {base} and height {height}?"
        options = {
            "A": str(area),
            "B": str(area + 1),
            "C": str(area - 1),
            "D": str(area + 2)
        }
        return {
            "question": question,
            "options": options,
            "answer": "A"
        }
    
    elif q_type == "perimeter":
        a = random.randint(3, 8)
        b = random.randint(4, 9)
        c = random.randint(5, 10)
        perimeter = a + b + c
        question = f"Find the perimeter of a triangle with sides {a}, {b}, {c}"
        options = {
            "A": str(perimeter),
            "B": str(perimeter + 1),
            "C": str(perimeter - 1),
            "D": str(perimeter + 2)
        }
        return {
            "question": question,
            "options": options,
            "answer": "A"
        }
    
    else:  # angles
        angle1 = random.randint(30, 60)
        angle2 = random.randint(30, 60)
        angle3 = 180 - angle1 - angle2
        question = f"What is the third angle if two angles are {angle1}° and {angle2}°?"
        options = {
            "A": str(angle3),
            "B": str(angle3 + 1),
            "C": str(angle3 - 1),
            "D": str(angle3 + 2)
        }
        return {
            "question": question,
            "options": options,
            "answer": "A"
        }

def generate_medium_question():
    """Generate medium triangle questions"""
    question_types = [
        "heron_formula",
        "trigonometry_basic",
        "pythagorean"
    ]
    
    q_type = random.choice(question_types)
    
    if q_type == "heron_formula":
        # Use sides that form a valid triangle
        a, b, c = 5, 6, 7
        s = (a + b + c) / 2
        area = math.sqrt(s * (s - a) * (s - b) * (s - c))
        question = f"Find the area using Heron's formula: sides {a}, {b}, {c}"
        options = {
            "A": str(round(area, 1)),
            "B": str(round(area + 1, 1)),
            "C": str(round(area - 1, 1)),
            "D": str(round(area + 2, 1))
        }
        return {
            "question": question,
            "options": options,
            "answer": "A"
        }
    
    elif q_type == "trigonometry_basic":
        angles = [30, 45, 60]
        angle = random.choice(angles)
        if angle == 30:
            sin_val = 0.5
        elif angle == 45:
            sin_val = 0.707
        else:  # 60
            sin_val = 0.866
        question = f"What is the sine of {angle}°?"
        options = {
            "A": str(sin_val),
            "B": str(sin_val + 0.1),
            "C": str(sin_val - 0.1),
            "D": str(sin_val + 0.2)
        }
        return {
            "question": question,
            "options": options,
            "answer": "A"
        }
    
    else:  # pythagorean
        # Use Pythagorean triple
        triples = [(3, 4, 5), (5, 12, 13), (6, 8, 10)]
        a, b, c = random.choice(triples)
        question = f"Find the hypotenuse of a right triangle with legs {a} and {b}"
        options = {
            "A": str(c),
            "B": str(c + 1),
            "C": str(c - 1),
            "D": str(c + 2)
        }
        return {
            "question": question,
            "options": options,
            "answer": "A"
        }

def generate_hard_question():
    """Generate hard triangle questions"""
    question_types = [
        "law_of_cosines",
        "trigonometry_advanced",
        "area_coordinates"
    ]
    
    q_type = random.choice(question_types)
    
    if q_type == "law_of_cosines":
        a, b, c = 5, 7, 8
        # Calculate angle C using law of cosines
        cos_C = (a**2 + b**2 - c**2) / (2 * a * b)
        angle_C = math.degrees(math.acos(cos_C))
        question = f"Find the angle using law of cosines: a={a}, b={b}, c={c}"
        options = {
            "A": str(round(angle_C)),
            "B": str(round(angle_C + 1)),
            "C": str(round(angle_C - 1)),
            "D": str(round(angle_C + 2))
        }
        return {
            "question": question,
            "options": options,
            "answer": "A"
        }
    
    elif q_type == "trigonometry_advanced":
        # Special angles
        angle = random.choice([120, 135, 150])
        if angle == 120:
            sin_val = 0.866
        elif angle == 135:
            sin_val = 0.707
        else:  # 150
            sin_val = 0.5
        question = f"What is the sine of {angle}°?"
        options = {
            "A": str(sin_val),
            "B": str(sin_val + 0.1),
            "C": str(sin_val - 0.1),
            "D": str(sin_val + 0.2)
        }
        return {
            "question": question,
            "options": options,
            "answer": "A"
        }
    
    else:  # area_coordinates
        # Triangle with vertices (0,0), (3,0), (0,4)
        area = 0.5 * 3 * 4
        question = f"Find the area of a triangle with vertices (0,0), (3,0), (0,4)"
        options = {
            "A": str(area),
            "B": str(area + 1),
            "C": str(area - 1),
            "D": str(area + 2)
        }
        return {
            "question": question,
            "options": options,
            "answer": "A"
        }

# ---------- Fetch Random Question from Specific Level ----------
def get_easy_question():
    mcqs = load_mcqs_by_level().get("easy", [])
    if mcqs:
        return random.choice(mcqs)
    else:
        return generate_easy_question()

def get_medium_question():
    mcqs = load_mcqs_by_level().get("medium", [])
    if mcqs:
        return random.choice(mcqs)
    else:
        return generate_medium_question()

def get_hard_question():
    mcqs = load_mcqs_by_level().get("hard", [])
    if mcqs:
        return random.choice(mcqs)
    else:
        return generate_hard_question()

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
        print(f"\n📘 Triangles | Level: {level.upper()}")
        q = get_question(level)
        if "error" in q:
            print(q["error"])
        else:
            print("Q:", q["question"])
            for opt, val in q["options"].items():
                print(f"  {opt}: {val}")
            print("✅ Answer:", q["answer"])
