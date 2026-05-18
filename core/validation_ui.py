import os
import sys
from datetime import datetime, timezone, timedelta
from flask import Flask, render_template, request, redirect, url_for, jsonify

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.recipe_validation_agent import build_validation_graph, RecipeValidationState

JST = timezone(timedelta(hours=9))

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates"),
)

validation_graph = build_validation_graph()
current_state = {}


@app.route("/")
def index():
    return render_template("validation.html", state=current_state)


@app.route("/start", methods=["POST"])
def start_validation():
    global current_state
    recipe_name = request.form.get("recipe_name", "クレソンサラダ")
    initial_state = {
        "recipe_name": recipe_name,
        "recipe_id": "",
        "ai_suggestion": "",
        "taste_score": 0.0,
        "appearance_score": 0.0,
        "difficulty_score": 0.0,
        "feedback_text": "",
        "overall_score": 0.0,
        "neo4j_updated": False,
        "validated_at": "",
    }
    result = validation_graph.invoke(initial_state, {"interrupt_before": ["await_evaluation"]})
    current_state = result
    return redirect(url_for("index"))


@app.route("/submit", methods=["POST"])
def submit_evaluation():
    global current_state
    current_state["taste_score"] = float(request.form.get("taste_score", 0))
    current_state["appearance_score"] = float(request.form.get("appearance_score", 0))
    current_state["difficulty_score"] = float(request.form.get("difficulty_score", 0))
    current_state["feedback_text"] = request.form.get("feedback_text", "")
    current_state["validated_at"] = datetime.now(JST).isoformat()

    result = validation_graph.invoke(current_state)
    current_state = result
    print(f"[submit_evaluation] 完了: overall={result['overall_score']} neo4j={result['neo4j_updated']}")
    return redirect(url_for("index"))


@app.route("/reset")
def reset():
    global current_state
    current_state = {}
    return redirect(url_for("index"))


if __name__ == "__main__":
    print("=" * 50)
    print("実食検証システム起動")
    print("http://localhost:5001")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5001, debug=False)
