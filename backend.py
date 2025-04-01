from flask import Flask, request, jsonify
import os
import json
import uuid
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*")

QUIZ_FOLDER = "quizzes"
LEADERBOARD_FILE = "leaderboard.json"
os.makedirs(QUIZ_FOLDER, exist_ok=True)

# Load leaderboard
if not os.path.exists(LEADERBOARD_FILE):
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump({}, f)

@app.route("/create-quiz", methods=["POST"])
def create_quiz():
    data = request.json
    quiz_id = str(uuid.uuid4())[:8]
    quiz_path = os.path.join(QUIZ_FOLDER, f"{quiz_id}.json")
    
    with open(quiz_path, "w") as f:
        json.dump(data, f)
    
    return jsonify({"quiz_id": quiz_id, "redirect": "/"}), 201

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
    correct_answers = quiz_data.get("questions", [])
    
    score = 0
    total = len(correct_answers)
    
    for i, question in enumerate(correct_answers):
        correct_answer = question["answer"]
        user_answer = user_answers.get(str(i))
        
        if question["type"] == "multiple":
            if sorted(map(int, user_answer)) == sorted(map(int, correct_answer.split(","))):
                score += 1
        elif question["type"] == "text":
            if user_answer.strip().lower() == correct_answer.strip().lower():
                score += 1
        else:
            if str(user_answer) == str(correct_answer):
                score += 1
    
    username = request.json.get("username", "Anonymous")
    
    # Update leaderboard
    with open(LEADERBOARD_FILE, "r") as f:
        leaderboard = json.load(f)
    
    if quiz_id not in leaderboard:
        leaderboard[quiz_id] = []
    
    leaderboard[quiz_id].append({"username": username, "score": score})
    
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(leaderboard, f)
    
    return jsonify({"score": score, "total": total})

@app.route("/leaderboard/<quiz_id>", methods=["GET"])
def get_leaderboard(quiz_id):
    with open(LEADERBOARD_FILE, "r") as f:
        leaderboard = json.load(f)
    
    if quiz_id not in leaderboard:
        return jsonify({"error": "No leaderboard data available"}), 404
    
    sorted_leaderboard = sorted(leaderboard[quiz_id], key=lambda x: x["score"], reverse=True)
    return jsonify(sorted_leaderboard)

if __name__ == "__main__":
    app.run(debug=True)
