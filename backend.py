from flask import Flask, request, jsonify
import os
import json
import uuid
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

QUIZ_FOLDER = "quizzes"
os.makedirs(QUIZ_FOLDER, exist_ok=True)

@app.route("/create-quiz", methods=["POST"])
def create_quiz():
    data = request.json
    quiz_id = str(uuid.uuid4())[:8]
    quiz_path = os.path.join(QUIZ_FOLDER, f"{quiz_id}.json")
    with open(quiz_path, "w") as f:
        json.dump(data, f)
    return jsonify({"quiz_id": quiz_id}), 201

@app.route("/get-quiz/<quiz_id>", methods=["GET"])
def get_quiz(quiz_id):
    quiz_path = os.path.join(QUIZ_FOLDER, f"{quiz_id}.json")
    if not os.path.exists(quiz_path):
        return jsonify({"error": "Quiz not found"}), 404
    with open(quiz_path, "r") as f:
        quiz_data = json.load(f)
    return jsonify(quiz_data)

@app.route("/submit-quiz/<quiz_id>", methods=["POST"])
def submit_quiz(quiz_id):
    quiz_path = os.path.join(QUIZ_FOLDER, f"{quiz_id}.json")
    if not os.path.exists(quiz_path):
        return jsonify({"error": "Quiz not found"}), 404

    with open(quiz_path, "r") as f:
        quiz_data = json.load(f)

    user_answers = request.json.get("answers", {})
    questions = quiz_data.get("questions", [])
    score = 0
    results = []

    for i, question in enumerate(questions):
        correct_answer = question["answer"]
        user_answer = user_answers.get(str(i), None)

        if question["type"] == "oneword":
            # Compare one-word answers (case insensitive, trimmed)
            if user_answer and user_answer.strip().lower() == correct_answer.strip().lower():
                score += 1
                results.append({"question": question["question"], "is_correct": True})
            else:
                results.append({"question": question["question"], "is_correct": False})
        elif question["type"] == "multi":
            # Compare multiple-choice answers (as sets)
            correct_answers = set(correct_answer.split(","))
            user_answers_set = set(user_answer or [])
            if correct_answers == user_answers_set:
                score += 1
                results.append({"question": question["question"], "is_correct": True})
            else:
                results.append({"question": question["question"], "is_correct": False})
        elif question["type"] == "single":
            # Compare single-choice answers
            if user_answer and user_answer[0] == correct_answer:
                score += 1
                results.append({"question": question["question"], "is_correct": True})
            else:
                results.append({"question": question["question"], "is_correct": False})

    return jsonify({"score": score, "total": len(questions), "results": results})

if __name__ == "__main__":
    app.run(debug=True)
