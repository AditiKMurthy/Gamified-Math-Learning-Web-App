import json
import random
import os
import math

# ---------- Load MCQs from JSON ----------
def load_mcqs_by_level():
    file_path = os.path.join(os.path.dirname(__file__), '..', 'pyqs', 'surface_areas_volumes_mcqs_by_level.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading MCQs: {e}")
        return {"easy": [], "medium": [], "hard": []}

# ---------- Generate Dynamic Questions ----------
def generate_easy_question():
    """Generate easy surface area and volume questions"""
    question_types = [
        "cube_surface_area",
        "cube_volume", 
        "sphere_surface_area"
    ]
    
    q_type = random.choice(question_types)
    
    if q_type == "cube_surface_area":
        side = random.randint(3, 8)
        surface_area = 6 * side * side
        question = f"What is the surface area of a cube with side {side}?"
        options = {
            "A": str(surface_area),
            "B": str(surface_area + 1),
            "C": str(surface_area - 1),
            "D": str(surface_area + 2)
        }
        return {
            "question": question,
            "options": options,
            "answer": "A"
        }
    
    elif q_type == "cube_volume":
        side = random.randint(3, 8)
        volume = side ** 3
        question = f"Find the volume of a cube with side {side}"
        options = {
            "A": str(volume),
            "B": str(volume + 1),
            "C": str(volume - 1),
            "D": str(volume + 2)
        }
        return {
            "question": question,
            "options": options,
            "answer": "A"
        }
    
    else:  # sphere_surface_area
        radius = random.randint(2, 6)
        surface_area = 4 * math.pi * radius * radius
        question = f"What is the surface area of a sphere with radius {radius}?"
        options = {
            "A": str(round(surface_area, 1)),
            "B": str(round(surface_area + 1, 1)),
            "C": str(round(surface_area - 1, 1)),
            "D": str(round(surface_area + 2, 1))
        }
        return {
            "question": question,
            "options": options,
            "answer": "A"
        }

def generate_medium_question():
    """Generate medium surface area and volume questions"""
    question_types = [
        "cylinder_volume",
        "cone_surface_area",
        "pyramid_volume"
    ]
    
    q_type = random.choice(question_types)
    
    if q_type == "cylinder_volume":
        radius = random.randint(2, 5)
        height = random.randint(4, 8)
        volume = math.pi * radius * radius * height
        question = f"Find the volume of a cylinder with radius {radius} and height {height}"
        options = {
            "A": str(round(volume, 2)),
            "B": str(round(volume + 1, 2)),
            "C": str(round(volume - 1, 2)),
            "D": str(round(volume + 2, 2))
        }
        return {
            "question": question,
            "options": options,
            "answer": "A"
        }
    
    elif q_type == "cone_surface_area":
        radius = random.randint(2, 5)
        height = random.randint(3, 7)
        slant_height = math.sqrt(radius**2 + height**2)
        surface_area = math.pi * radius * (radius + slant_height)
        question = f"What is the surface area of a cone with radius {radius} and height {height}?"
        options = {
            "A": str(round(surface_area, 1)),
            "B": str(round(surface_area + 1, 1)),
            "C": str(round(surface_area - 1, 1)),
            "D": str(round(surface_area + 2, 1))
        }
        return {
            "question": question,
            "options": options,
            "answer": "A"
        }
    
    else:  # pyramid_volume
        base = random.randint(3, 6)
        height = random.randint(4, 8)
        volume = (1/3) * base * base * height
        question = f"Find the volume of a pyramid with base {base} and height {height}"
        options = {
            "A": str(round(volume, 2)),
            "B": str(round(volume + 1, 2)),
            "C": str(round(volume - 1, 2)),
            "D": str(round(volume + 2, 2))
        }
        return {
            "question": question,
            "options": options,
            "answer": "A"
        }

def generate_hard_question():
    """Generate hard surface area and volume questions"""
    question_types = [
        "torus_volume",
        "ellipsoid_volume",
        "truncated_cone"
    ]
    
    q_type = random.choice(question_types)
    
    if q_type == "torus_volume":
        major_radius = random.randint(4, 8)
        minor_radius = random.randint(1, 3)
        volume = 2 * math.pi * math.pi * major_radius * minor_radius * minor_radius
        question = f"Find the volume of a torus with major radius {major_radius} and minor radius {minor_radius}"
        options = {
            "A": str(round(volume, 2)),
            "B": str(round(volume + 1, 2)),
            "C": str(round(volume - 1, 2)),
            "D": str(round(volume + 2, 2))
        }
        return {
            "question": question,
            "options": options,
            "answer": "A"
        }
    
    elif q_type == "ellipsoid_volume":
        a, b, c = random.randint(2, 4), random.randint(3, 5), random.randint(4, 6)
        volume = (4/3) * math.pi * a * b * c
        question = f"Find the volume of an ellipsoid with axes {a}, {b}, {c}"
        options = {
            "A": str(round(volume, 2)),
            "B": str(round(volume + 1, 2)),
            "C": str(round(volume - 1, 2)),
            "D": str(round(volume + 2, 2))
        }
        return {
            "question": question,
            "options": options,
            "answer": "A"
        }
    
    else:  # truncated_cone
        r1, r2, h = random.randint(2, 4), random.randint(1, 2), random.randint(3, 6)
        volume = (1/3) * math.pi * h * (r1**2 + r1*r2 + r2**2)
        question = f"Find the volume of a truncated cone with radii {r1}, {r2} and height {h}"
        options = {
            "A": str(round(volume, 2)),
            "B": str(round(volume + 1, 2)),
            "C": str(round(volume - 1, 2)),
            "D": str(round(volume + 2, 2))
        }
        return {
            "question": question,
            "options": options,
            "answer": "A"
        }

# ---------- Pick Random MCQ ----------
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

# ---------- CLI Test (optional) ----------
if __name__ == "__main__":
    for level in ["easy", "medium", "hard"]:
        print(f"\n📘 Surface Areas & Volumes | Level: {level.upper()}")
        q = get_question(level)
        if "error" in q:
            print(q["error"])
        else:
            print("Q:", q["question"])
            for opt, val in q["options"].items():
                print(f"  {opt}: {val}")
            print("✅ Answer:", q["answer"])
