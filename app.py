from flask import Flask, render_template, request, redirect, url_for, session, send_file
import csv
import os
import json
from datetime import datetime
from supabase import create_client

app = Flask(__name__)
app.secret_key = 'quiz_secret_key'

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

CSV_FILE = 'results.csv'

# QUIZ_OPEN = True
QUIZ_OPEN = False

admin_db = {
    "admin": "123"
}

quiz_data = [
        {
        "id": 1,
        "text": "Which gas makes up the largest percentage of the Earth's atmosphere?",
        "options": [
            "Oxygen",
            "Carbon Dioxide",
            "Nitrogen",
            "Argon"
        ],
        "correct": "Nitrogen"
    },

    {
        "id": 2,
        "text": "Which atmospheric layer contains most weather phenomena?",
        "options": [
            "Stratosphere",
            "Troposphere",
            "Mesosphere",
            "Thermosphere"
        ],
        "correct": "Troposphere"
    },

    {
        "id": 3,
        "text": "What is the average environmental lapse rate in the troposphere?",
        "options": [
            "3.5°C/km",
            "5.0°C/km",
            "6.5°C/km",
            "9.8°C/km"
        ],
        "correct": "6.5°C/km"
    },

    {
        "id": 4,
        "text": "Which variable gas is most important for weather processes?",
        "options": [
            "Ozone",
            "Methane",
            "Helium",
            "Water Vapour"
        ],
        "correct": "Water Vapour"
    },

    {
        "id": 5,
        "text": "The upper boundary of the troposphere is known as the:",
        "options": [
            "Mesopause",
            "Stratopause",
            "Tropopause",
            "Thermopause"
        ],
        "correct": "Tropopause"
    },

    {
        "id": 6,
        "text": "Why does temperature increase with height in the stratosphere?",
        "options": [
            "Increased atmospheric pressure",
            "Absorption of solar radiation by ozone",
            "Presence of water vapour",
            "Earth's surface heating"
        ],
        "correct": "Absorption of solar radiation by ozone"
    },

    {
        "id": 7,
        "text": "Most meteors burn up in which atmospheric layer?",
        "options": [
            "Troposphere",
            "Stratosphere",
            "Mesosphere",
            "Exosphere"
        ],
        "correct": "Mesosphere"
    },

    {
        "id": 8,
        "text": "Which atmospheric layer contains the ionosphere and auroras?",
        "options": [
            "Mesosphere",
            "Thermosphere",
            "Stratosphere",
            "Troposphere"
        ],
        "correct": "Thermosphere"
    },

    {
        "id": 9,
        "text": "A pressure of approximately 998 hPa is generally associated with:",
        "options": [
            "Strong high pressure",
            "Average sea-level pressure",
            "Moderately low pressure",
            "Deep storm system only"
        ],
        "correct": "Moderately low pressure"
    },

    {
        "id": 10,
        "text": "Why are jet streams important in forecasting?",
        "options": [
            "They increase atmospheric pressure",
            "They determine ocean currents",
            "They steer storms and influence severe weather development",
            "They generate ozone in the stratosphere"
        ],
        "correct": "They steer storms and influence severe weather development"
    },

    {
        "id": 11,
        "text": "The atmosphere is held around the Earth by gravity.",
        "options": [
            "True",
            "False"
        ],
        "correct": "True"
    },

    {
        "id": 12,
        "text": "Oxygen is the most abundant gas in the atmosphere.",
        "options": [
            "True",
            "False"
        ],
        "correct": "False"
    },

    {
        "id": 13,
        "text": "Water vapour acts as a greenhouse gas and contributes to cloud formation.",
        "options": [
            "True",
            "False"
        ],
        "correct": "True"
    },

    {
        "id": 14,
        "text": "Atmospheric pressure increases with altitude.",
        "options": [
            "True",
            "False"
        ],
        "correct": "False"
    },

    {
        "id": 15,
        "text": "Aviation meteorologists monitor turbulence, wind shear, icing, and jet streams to support flight safety.",
        "options": [
            "True",
            "False"
        ],
        "correct": "True"
    }

    # ADD THE REST OF YOUR QUESTIONS HERE
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

    if not QUIZ_OPEN:
        return render_template('quiz_closed.html')

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

    return render_template(
        'index.html',
        questions=quiz_data,
        user=session['student_name']
    )


@app.route('/submit', methods=['POST'])
def submit():

    if session.get('role') != 'student':
        return redirect(url_for('landing'))

    score = 0
    total = len(quiz_data)

    review_data = []
    answers_data = {}

    for q in quiz_data:

        answer = request.form.get(f"question_{q['id']}")

        correct = answer == q['correct']

        if correct:
            score += 1

        review_data.append({
            'question': q['text'],
            'user_answer': answer,
            'correct_answer': q['correct'],
            'is_correct': correct
        })

        answers_data[f"Q{q['id']}"] = {
            'answer': answer,
            'correct': q['correct'],
            'status': 'Correct' if correct else 'Wrong'
        }

    percentage = round((score / total) * 100, 2)


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

    try:

        response = supabase.table("quiz_results2") \
            .select("*") \
            .order("id", desc=True) \
            .execute()

        results = response.data

    except Exception as e:
        print("ADMIN ERROR:", e)

    return render_template('admin.html', results=results)


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
