import json
import random
import os

# ---------- Load Questions from File ----------
def load_mcqs_by_level():
    file_path = os.path.join(os.path.dirname(__file__), '..', 'pyqs', 'statistics_mcqs_by_level.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading Statistics MCQ: {e}")
        return {"easy": [], "medium": [], "hard": []}

# ---------- Get Static MCQs ----------
def get_static_question(level="easy"):
    mcqs = load_mcqs_by_level().get(level.lower(), [])
    return random.choice(mcqs) if mcqs else {"error": f"No {level} questions found."}

# ---------- Generate Dynamic Question ----------
def generate_dynamic_question(level="easy"):
    level = level.lower()
    
    if level == "easy":
        nums = random.sample(range(10, 50), 3)
        mean_val = sum(nums) // 3
        options = {
            "A": str(mean_val),
            "B": str(mean_val + 5),
            "C": str(mean_val - 5),
            "D": str(mean_val + 10)
        }
        return {
            "question": f"What is the mean of {nums[0]}, {nums[1]}, {nums[2]}?",
            "options": options,
            "answer": "A"
        }
    
    elif level == "medium":
        # Median of 5 values
        values = sorted(random.sample(range(10, 100), 5))
        median = values[2]
        options = {
            "A": str(median),
            "B": str(values[1]),
            "C": str(values[3]),
            "D": str(median + 5)
        }
        return {
            "question": f"What is the median of these values: {', '.join(map(str, values))}?",
            "options": options,
            "answer": "A"
        }

    elif level == "hard":
        # Mode from repeated values
        base = random.randint(10, 20)
        values = [base] * 3 + [base + 1] * 2 + [base + 2]  # base is mode
        random.shuffle(values)
        mode = base
        options = {
            "A": str(mode),
            "B": str(mode + 1),
            "C": str(mode - 1),
            "D": str(mode + 2)
        }
        return {
            "question": f"Find the mode of the dataset: {', '.join(map(str, values))}",
            "options": options,
            "answer": "A"
        }

    else:
        return {"error": "Invalid difficulty level."}

# ---------- Main Unified Interface ----------
def get_question(level="easy", mode="static"):
    """
    mode: 'static' => pick from JSON
          'dynamic' => generate a fresh new question
    """
    if mode == "static":
        return get_static_question(level)
    elif mode == "dynamic":
        return generate_dynamic_question(level)
    else:
        return {"error": "Invalid mode. Use 'static' or 'dynamic'."}

# ---------- CLI Testing ----------
if __name__ == "__main__":
    for level in ["easy", "medium", "hard"]:
        for mode in ["static", "dynamic"]:
            print(f"\n📘 Statistics | Level: {level.upper()} | Mode: {mode.upper()}")
            q = get_question(level=level, mode=mode)
            if "error" in q:
                print(q["error"])
            else:
                print("Q:", q["question"])
                for opt, val in q["options"].items():
                    print(f"  {opt}: {val}")
                print("✅ Answer:", q["answer"])
