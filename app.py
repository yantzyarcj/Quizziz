import sqlite3, random
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.config["SECRET_KEY"]="quiz"
DB = "final_quiz.db"

def get_quizzes():
    conn = sqlite3.connect(DB)
    rows = conn.execute("SELECT id, name, description FROM quizzes").fetchall()
    conn.close()
    return rows

def get_questions(quiz_id):
    conn = sqlite3.connect(DB)
    rows = conn.execute("SELECT question, correct, wrong1, wrong2, wrong3 FROM questions WHERE quiz_id=?", (quiz_id,)).fetchall()
    conn.close()
    return rows

@app.route("/")
def index():
    quizzes = get_quizzes()
    return render_template("index.html", quizzes=quizzes)

@app.route("/start", methods=["POST"])
def start():
    quiz_id = int(request.form.get("quiz_id"))
    rows = get_questions(quiz_id)
    questions = [{"q": r[0], "a": r[1], "w": [r[2], r[3], r[4]]} for r in rows]
    session["questions"] = questions
    session["current"] = 0
    session["score"] = 0
    return redirect(url_for("test"))

@app.route("/test", methods=["GET", "POST"])
def test():
    questions = session.get("questions", [])
    idx = session.get("current", 0)

    if request.method == "POST" and idx > 0:
        jawaban = request.form.get("answer", "")
        if jawaban == questions[idx-1]["a"]:
            session["score"] += 1
    
    if idx >= len(questions):
        return redirect(url_for("result"))
    
    q = questions[idx]
    session["current"] = idx + 1

    pilihan = [q["a"]] + q["w"]
    random.shuffle(pilihan)

    return render_template("test.html", q=q, idx=idx, pilihan=pilihan, score=session["score"], total=len(questions))

@app.route("/result")
def result():
    score = session.get("score", 0)
    total = len(session.get("questions", []))
    return render_template("result.html", score=score, total=total)
app.run(debug=True)

