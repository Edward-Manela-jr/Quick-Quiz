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

QUIZ_OPEN = True
#QUIZ_OPEN = False

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
