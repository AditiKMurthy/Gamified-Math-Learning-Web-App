import json
import random
import os
import math

# ---------- Load Questions from File ----------
def load_mcqs_by_level():
    file_path = os.path.join(os.path.dirname(__file__), '..', 'pyqs', 'real_numbers_mcqs_by_level.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading Real Numbers MCQ: {e}")
        return {"easy": [], "medium": [], "hard": []}

# ---------- Generate Dynamic Questions ----------
def generate_easy_question():
    """Generate easy real numbers questions"""
    question_types = [
        "square_root",
        "cube_root", 
        "power"
    ]
    
    q_type = random.choice(question_types)
    
    if q_type == "square_root":
        num = random.choice([4, 9, 16, 25, 36, 49, 64, 81, 100])
        answer = int(math.sqrt(num))
        question = f"What is the square root of {num}?"
        options = {
            "A": str(answer),
            "B": str(answer + 1),
            "C": str(answer - 1),
            "D": str(answer + 2)
        }
        return {
            "question": question,
            "options": options,
            "answer": "A"
        }
    
    elif q_type == "cube_root":
        num = random.choice([8, 27, 64, 125, 216, 343, 512, 729])
        answer = int(round(num ** (1/3)))
        question = f"Find the cube root of {num}"
        options = {
            "A": str(answer),
            "B": str(answer + 1),
            "C": str(answer - 1),
            "D": str(answer + 2)
        }
        return {
            "question": question,
            "options": options,
            "answer": "A"
        }
    
    else:  # power
        base = random.randint(2, 5)
        exponent = random.randint(2, 6)
        answer = base ** exponent
        question = f"What is {base} to the power of {exponent}?"
        options = {
            "A": str(answer),
            "B": str(answer + 1),
            "C": str(answer - 1),
            "D": str(answer + 2)
        }
        return {
            "question": question,
            "options": options,
            "answer": "A"
        }

def generate_medium_question():
    """Generate medium real numbers questions"""
    question_types = [
        "irrational_approximation",
        "decimal_to_fraction",
        "scientific_notation"
    ]
    
    q_type = random.choice(question_types)
    
    if q_type == "irrational_approximation":
        num = random.choice([2, 3, 5, 7, 11])
        answer = round(math.sqrt(num), 2)
        question = f"Approximate √{num} to 2 decimal places"
        options = {
            "A": str(answer),
            "B": str(answer + 0.01),
            "C": str(answer - 0.01),
            "D": str(answer + 0.02)
        }
        return {
            "question": question,
            "options": options,
            "answer": "A"
        }
    
    elif q_type == "decimal_to_fraction":
        # Simple fractions like 0.5 = 1/2
        fractions = [(0.5, "1/2"), (0.25, "1/4"), (0.75, "3/4"), (0.2, "1/5"), (0.4, "2/5")]
        decimal, fraction = random.choice(fractions)
        question = f"Convert {decimal} to a fraction"
        options = {
            "A": fraction,
            "B": "1/3",
            "C": "2/3",
            "D": "1/6"
        }
        return {
            "question": question,
            "options": options,
            "answer": "A"
        }
    
    else:  # scientific_notation
        num = random.randint(100, 999)
        power = random.randint(2, 5)
        answer = num * (10 ** power)
        question = f"Write {answer} in scientific notation"
        options = {
            "A": f"{num} × 10^{power}",
            "B": f"{num} × 10^{power + 1}",
            "C": f"{num} × 10^{power - 1}",
            "D": f"{num + 1} × 10^{power}"
        }
        return {
            "question": question,
            "options": options,
            "answer": "A"
        }

def generate_hard_question():
    """Generate hard real numbers questions"""
    question_types = [
        "complex_irrational",
        "logarithm",
        "exponential"
    ]
    
    q_type = random.choice(question_types)
    
    if q_type == "complex_irrational":
        # Questions about π, e, etc.
        constants = [("π", 3.14159), ("e", 2.71828)]
        constant, value = random.choice(constants)
        question = f"What is the approximate value of {constant}?"
        options = {
            "A": str(value),
            "B": str(value + 0.1),
            "C": str(value - 0.1),
            "D": str(value + 0.2)
        }
        return {
            "question": question,
            "options": options,
            "answer": "A"
        }
    
    elif q_type == "logarithm":
        base = random.randint(2, 5)
        num = base ** random.randint(2, 4)
        answer = int(math.log(num, base))
        question = f"Find log_{base}({num})"
        options = {
            "A": str(answer),
            "B": str(answer + 1),
            "C": str(answer - 1),
            "D": str(answer + 2)
        }
        return {
            "question": question,
            "options": options,
            "answer": "A"
        }
    
    else:  # exponential
        base = random.randint(2, 4)
        exponent = random.randint(3, 6)
        answer = base ** exponent
        question = f"Calculate {base}^{exponent}"
        options = {
            "A": str(answer),
            "B": str(answer + 1),
            "C": str(answer - 1),
            "D": str(answer + 2)
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
        print(f"\n📘 Real Numbers | Level: {level.upper()}")
        q = get_question(level)
        if "error" in q:
            print(q["error"])
        else:
            print("Q:", q["question"])
            for opt, val in q["options"].items():
                print(f"  {opt}: {val}")
            print("✅ Answer:", q["answer"])
