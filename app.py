from flask import Flask, render_template, request, redirect, url_for, session, send_file
import csv
import os
import json
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = 'quiz_secret_key'

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

print("SUPABASE_URL FOUND =", bool(SUPABASE_URL))
print("SUPABASE_KEY FOUND =", bool(SUPABASE_KEY))

supabase = None

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Supabase connected successfully")
else:
    print("Supabase credentials missing")



# -------------------------------
# Quiz Database Functions
# -------------------------------

def get_active_quiz():
    response = (
        supabase.table("quizzes")
        .select("*")
        .eq("is_active", True)
        .limit(1)
        .execute()
    )

    if response.data:
        return response.data[0]
    return None


def get_quiz_questions(quiz_id):

    response = (
        supabase.table("quiz_questions")
        .select("*")
        .eq("quiz_id", quiz_id)
        .order("display_order")
        .execute()
    )

    return response.data


quiz = get_active_quiz()

print("--ACTIVE QUIZ:")
print(quiz)



CSV_FILE = 'results.csv'

#QUIZ_OPEN = True
QUIZ_OPEN = False

admin_db = {
    "admin": "123"
}

quiz_data = [
{
"id": 1,
"text": "Which statement best describes the relationship between air temperature and air density?",
"options": [
"Density increases when temperature increases",
"Density decreases when temperature increases",
"Density remains constant with temperature changes",
"Density only depends on humidity"
],
"correct": "Density decreases when temperature increases"
},


{
    "id": 2,
    "text": "If atmospheric pressure increases while temperature remains constant, the air density will:",
    "options": [
        "Decrease",
        "Remain unchanged",
        "Increase",
        "Become zero"
    ],
    "correct": "Increase"
},

{
    "id": 3,
    "text": "Which atmospheric condition produces the LOWEST air density?",
    "options": [
        "Cold and dry air",
        "Cold and moist air",
        "Warm and dry air",
        "Warm and humid air"
    ],
    "correct": "Warm and humid air"
},

{
    "id": 4,
    "text": "According to the Ideal Gas Law, air density is proportional to pressure and inversely proportional to temperature.  p = P/(RT) If pressure remains constant and temperature increases, density will:",
    "options": [
        "Increase",
        "Decrease",
        "Stay constant",
        "Double automatically"
    ],
    "correct": "Decrease"
},

{
    "id": 5,
    "text": "An aerodrome reports Pressure = 1000 hPa and Temperature = 20°C. Later, temperature rises to 35°C while pressure remains unchanged. What happens to density altitude?",
    "options": [
        "Decreases",
        "Remains unchanged",
        "Increases",
        "Becomes negative"
    ],
    "correct": "Increases"
},

{
    "id": 6,
    "text": "Which statement about humidity and air density is CORRECT?",
    "options": [
        "Humid air is heavier than dry air",
        "Dry air is less dense than humid air",
        "Humid air is less dense than dry air",
        "Humidity has no effect on density"
    ],
    "correct": "Humid air is less dense than dry air"
},

{
    "id": 7,
    "text": "Calculate the approximate air density using p = P/(RT), where P = 100000 Pa, R = 287 J kg⁻¹ K⁻¹ and T = 300 K.",
    "options": [
        "0.86 kg/m³",
        "1.16 kg/m³",
        "2.50 kg/m³",
        "3.48 kg/m³"
    ],
    "correct": "1.16 kg/m³"
},

{
    "id": 8,
    "text": "At a high-elevation airport, aircraft performance is poor mainly because:",
    "options": [
        "Air density is higher",
        "Air density is lower",
        "Humidity is always zero",
        "Pressure increases rapidly"
    ],
    "correct": "Air density is lower"
},

{
    "id": 9,
    "text": "Standard atmospheric pressure at mean sea level used in aviation meteorology is:",
    "options": [
        "950 hPa",
        "1000 hPa",
        "1013.25 hPa",
        "1030 hPa"
    ],
    "correct": "1013.25 hPa"
},

{
    "id": 10,
    "text": "A parcel of air has high temperature, low pressure and high humidity. These conditions together will produce:",
    "options": [
        "Very high density",
        "Moderate density",
        "Low density",
        "No effect on aircraft operations"
    ],
    "correct": "Low density"
},

{
    "id": 11,
    "text": "The temperature at an airport increases from 15°C to 30°C while pressure stays constant. What is the approximate effect on aircraft take-off performance?",
    "options": [
        "Take-off distance decreases",
        "Aircraft lift increases significantly",
        "Take-off distance increases due to lower density",
        "No change in performance"
    ],
    "correct": "Take-off distance increases due to lower density"
},

{
    "id": 12,
    "text": "An aircraft flying from South America to Southern Africa encounters strong easterly Trade Winds. What effect are these winds most likely to have on an aircraft flying westward?",
    "options": [
        "Increase ground speed",
        "Cause a tailwind",
        "Decrease ground speed due to a headwind",
        "Have no effect on flight time"
    ],
    "correct": "Decrease ground speed due to a headwind"
}

]


if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            'Name',
            'Email',
            'Score',
            'Total',
            'Percentage',
            'Answers',
            'Date'
        ])


@app.route('/')
def landing():
    return redirect(url_for('student_login'))

@app.route('/student', methods=['GET', 'POST'])
def student_login():

    active_quiz = get_active_quiz()

    if not active_quiz:
        return "No active quiz has been configured."

    if not active_quiz["quiz_open"]:
        return render_template("quiz_closed.html")


    if request.method == 'POST':

        name = request.form.get('name')
        email = request.form.get('email')

        # Prevent multiple attempts using same email
        # Prevent multiple attempts using same email
        if os.path.exists(CSV_FILE):

            with open(CSV_FILE, 'r') as file:

                reader = csv.reader(file)

                for row in reader:

                    if len(row) > 1:

                        existing_email = row[1]

                        if existing_email.lower() == email.lower():

                            return """
                            <h2 style='color:red; text-align:center; margin-top:50px;'>
                                You have already attempted this quiz.
                            </h2>
                            """

        session['student_name'] = name
        session['student_email'] = email
        session['role'] = 'student'

        return redirect(url_for('quiz'))

    return render_template('student_login.html')

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        if username in admin_db and admin_db[username] == password:
            session['role'] = 'admin'
            return redirect(url_for('admin'))

        return 'Invalid Admin Credentials'

    return render_template('admin_login.html')


@app.route('/quiz')
def quiz():

    if session.get('role') != 'student':
        return redirect(url_for('landing'))

    active_quiz = get_active_quiz()

    questions = get_quiz_questions(active_quiz["id"])

    print("QUESTIONS FROM DATABASE:")
    print(questions)

    formatted_questions = []

    for q in questions:
        formatted_questions.append({
            "id": q["id"],
            "text": q["question"],
            "options": [
                q["option1"],
                q["option2"],
                q["option3"],
                q["option4"]
            ],
            "image": q.get("image_url")
        })

    return render_template(
        'index.html',
        questions=formatted_questions,
        user=session['student_name'],
        quiz=active_quiz
    )

@app.route('/submit', methods=['POST'])
def submit():

    if session.get('role') != 'student':
        return redirect(url_for('landing'))

    active_quiz = get_active_quiz()
    questions = get_quiz_questions(active_quiz["id"])

    score = 0
    total = len(questions)

    review_data = []
    answers_data = {}

    for q in questions:

        answer = request.form.get(f"question_{q['id']}")

        correct = answer == q['correct']

        if correct:
            score += 1

        review_data.append({
            'question': q['question'],
            'user_answer': answer,
            'correct_answer': q['correct'],
            'is_correct': correct
        })

        answers_data[f"Q{q['id']}"] = {
            'answer': answer,
            'correct': q['correct'],
            'status': 'Correct' if correct else 'Wrong'
        }

    percentage = round((score / total) * 100, 2) if total else 0


    # SAVE RESULT TO SUPABASE
    # Save to Supabase
    if supabase:
        try:
            supabase.table("quiz_results2").insert({
                "name": session['student_name'],
                "email": session['student_email'],
                "score": score,
                "total": total,
                "percentage": percentage,
                "answers": json.dumps(answers_data),
                "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }).execute()

            print("Saved to Supabase")

        except Exception as e:
            print("SUPABASE ERROR:", e)

    # SAVE RESULT TO CSV
    with open(CSV_FILE, 'a', newline='') as file:
        writer = csv.writer(file)

        writer.writerow([
            session['student_name'],
            session['student_email'],
            score,
            total,
            percentage,
            json.dumps(answers_data),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ])

    return render_template(
        'results.html',
        score=score,
        total=total,
        percentage=percentage,
        review_data=review_data
    )


@app.route('/admin')
def admin():

    if session.get('role') != 'admin':
        return redirect(url_for('landing'))

    results = []
    active_quiz = get_active_quiz()
    quiz_open = active_quiz["quiz_open"] if active_quiz else False
    total_participants = 0
    average_score = 0
    highest_score = 0
    latest_submission = "N/A"

    try:

        # Read quiz results
        response = supabase.table("quiz_results2") \
            .select("*") \
            .order("id", desc=True) \
            .execute()

        results = response.data

        # Dashboard statistics
        total_participants = len(results)

        if total_participants > 0:

            average_score = round(
                sum(r["percentage"] for r in results) / total_participants,
                2
            )

            highest_score = max(r["percentage"] for r in results)

            latest_submission = results[0]["date"]

    except Exception as e:
        print("ADMIN ERROR:", e)

    return render_template(
    'admin.html',
    results=results,
    quiz_open=quiz_open,
    active_quiz=active_quiz,
    total_participants=total_participants,
    average_score=average_score,
    highest_score=highest_score,
    latest_submission=latest_submission
)



@app.route('/manage-quiz')
def manage_quiz():

    if session.get('role') != 'admin':
        return redirect(url_for('landing'))

    response = (
        supabase.table("quizzes")
        .select("*")
        .order("id")
        .execute()
    )

    quizzes = response.data

    return render_template(
        "manage_quiz.html",
        quizzes=quizzes
    )


@app.route('/activate-quiz/<int:quiz_id>', methods=['POST'])
def activate_quiz(quiz_id):

    if session.get("role") != "admin":
        return redirect(url_for("landing"))

    # Deactivate every quiz
    supabase.table("quizzes").update({
        "is_active": False,
        "quiz_open": False
    }).neq("id", 0).execute()

    # Activate selected quiz
    supabase.table("quizzes").update({
        "is_active": True,
        "quiz_open": True
    }).eq("id", quiz_id).execute()

    return redirect(url_for("manage_quiz"))


@app.route('/deactivate-quiz/<int:quiz_id>', methods=['POST'])
def deactivate_quiz(quiz_id):

    if session.get("role") != "admin":
        return redirect(url_for("landing"))

    supabase.table("quizzes").update({
        "is_active": False,
        "quiz_open": False
    }).eq("id", quiz_id).execute()

    return redirect(url_for("manage_quiz"))


@app.route('/manage-questions/<int:quiz_id>')
def manage_questions(quiz_id):

    if session.get("role") != "admin":
        return redirect(url_for("landing"))

    quiz = (
        supabase.table("quizzes")
        .select("*")
        .eq("id", quiz_id)
        .single()
        .execute()
    ).data

    questions = (
        supabase.table("quiz_questions")
        .select("*")
        .eq("quiz_id", quiz_id)
        .order("display_order")
        .execute()
    ).data

    return render_template(
        "manage_questions.html",
        quiz=quiz,
        questions=questions
    )





@app.route('/delete-question/<int:question_id>')
def delete_question(question_id):

    if session.get("role") != "admin":
        return redirect(url_for("landing"))

    # Find which quiz this question belongs to
    question = supabase.table("quiz_questions") \
        .select("quiz_id") \
        .eq("id", question_id) \
        .single() \
        .execute()

    quiz_id = question.data["quiz_id"]

    # Delete the question
    supabase.table("quiz_questions") \
        .delete() \
        .eq("id", question_id) \
        .execute()

    return redirect(url_for("manage_questions", quiz_id=quiz_id))







@app.route('/create-quiz', methods=['GET', 'POST'])
def create_quiz():

    if session.get("role") != "admin":
        return redirect(url_for("landing"))

    if request.method == "POST":

        supabase.table("quizzes").insert({

            "title": request.form["title"],

            "description": request.form["description"],

            "rules": request.form["rules"],

            "pass_mark": int(request.form["pass_mark"]),

            "time_limit": int(request.form["time_limit"])
            if request.form["time_limit"] else None,

            "quiz_open": False,

            "is_active": False

        }).execute()

        return redirect(url_for("manage_quiz"))

    return render_template("create_quiz.html")









@app.route('/edit-question/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):

    if session.get("role") != "admin":
        return redirect(url_for("landing"))

    response = supabase.table("quiz_questions") \
        .select("*") \
        .eq("id", question_id) \
        .single() \
        .execute()

    question = response.data

    if request.method == "POST":

        correct_index = request.form["correct_option"]
        correct_answer = request.form[f"option{correct_index}"]

        supabase.table("quiz_questions") \
            .update({

                "question": request.form["question"],

                "option1": request.form["option1"],
                "option2": request.form["option2"],
                "option3": request.form["option3"],
                "option4": request.form["option4"],

                "correct": correct_answer,

                "question_type": request.form["question_type"],

                "display_order": int(request.form["display_order"]),

                "image_url": request.form["image_url"],

                "explanation": request.form["explanation"]

            }) \
            .eq("id", question_id) \
            .execute()

        return redirect(url_for(
            "manage_questions",
            quiz_id=question["quiz_id"]
        ))

    return render_template(
        "edit_question.html",
        question=question
    )







@app.route('/add-question/<int:quiz_id>', methods=['GET', 'POST'])
def add_question(quiz_id):

    if session.get("role") != "admin":
        return redirect(url_for("landing"))

    if request.method == "POST":
        correct_index = request.form["correct_option"]

        correct_answer = request.form[f"option{correct_index}"]

        supabase.table("quiz_questions").insert({

            "quiz_id": quiz_id,

            "question": request.form["question"],

            "option1": request.form["option1"],
            "option2": request.form["option2"],
            "option3": request.form["option3"],
            "option4": request.form["option4"],

            "correct": correct_answer,

            "question_type": request.form["question_type"],

            "display_order": int(request.form["display_order"]),

            "image_url": request.form["image_url"],

            "explanation": request.form["explanation"]

        }).execute()

        return redirect(url_for("manage_questions", quiz_id=quiz_id))

    return render_template(
        "add_question.html",
        quiz_id=quiz_id
    )








@app.route('/open-quiz', methods=['POST'])
def open_quiz():

    if session.get('role') != 'admin':
        return redirect(url_for('landing'))

    active_quiz = get_active_quiz()
    if active_quiz:
        supabase.table("quizzes").update({
            "quiz_open": True
        }).eq("id", active_quiz["id"]).execute()

    return redirect(url_for('admin'))


@app.route('/close-quiz', methods=['POST'])
def close_quiz():

    if session.get('role') != 'admin':
        return redirect(url_for('landing'))

    active_quiz = get_active_quiz()
    if active_quiz:
        supabase.table("quizzes").update({
            "quiz_open": False
        }).eq("id", active_quiz["id"]).execute()

    return redirect(url_for('admin'))




@app.route('/review/<int:result_id>')
def review(result_id):

    if session.get('role') != 'admin':
        return redirect(url_for('landing'))

    try:

        response = supabase.table("quiz_results2") \
            .select("*") \
            .eq("id", result_id) \
            .execute()

        if not response.data:
            return "Record not found"

        row = response.data[0]

        answers = json.loads(row['answers'])

        return render_template(
            'review.html',
            name=row['name'],
            email=row['email'],
            score=row['score'],
            total=row['total'],
            percentage=row['percentage'],
            answers=answers
        )

    except Exception as e:
        return f"Review Error: {e}"

@app.route('/download-csv')
def download_csv():

    if session.get('role') != 'admin':
        return redirect(url_for('landing'))

    return send_file(CSV_FILE, as_attachment=True)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing'))


if __name__ == '__main__':
    app.run(debug=True)
