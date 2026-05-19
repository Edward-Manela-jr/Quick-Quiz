from flask import Flask, render_template, request, redirect, url_for, session, send_file
import csv
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'quiz_secret_key'

CSV_FILE = 'results.csv'

admin_db = {
    "admin": "123"
}

quiz_data = [
    {
        "id": 1,
        "text": "What does ENSO stand for?",
        "options": [
            "Eastern Northern Seasonal Oscillation",
            "El Niño Southern Oscillation",
            "Equatorial Neutral Sea Oscillation",
            "Environmental Northern Sea Oscillation"
        ],
        "correct": "El Niño Southern Oscillation"
    },

    {
        "id": 2,
        "text": "What does MJO stand for?",
        "options": [
            "Major Jet Oscillation",
            "Monsoon Jet Organisation",
            "Madden Julian Oscillation",
            "Marine Julian Oscillation"
        ],
        "correct": "Madden Julian Oscillation"
    },
    {
    "id": 3,
    "text": "In which layer of the atmosphere does weather occur?",
    "options": [
        "Stratosphere",
        "Troposphere",
        "Stratopause",
        "Thermosphere"
    ],
    "correct": "Troposphere"
},

{
    "id": 4,
    "text": "Which part of the climate system do snow, sea ice, glaciers and ice sheets form?",
    "options": [
        "Hydrosphere",
        "Biosphere",
        "Atmosphere",
        "Cryosphere"
    ],
    "correct": "Cryosphere"
},

{
    "id": 5,
    "text": "The rate at which temperature changes with height is called:",
    "options": [
        "Lapse rate",
        "Energy balance",
        "Coriolis force",
        "Tropopause"
    ],
    "correct": "Lapse rate"
},

{
    "id": 6,
    "text": "What are the components of the climate system?",
    "options": [
        "Troposphere, stratosphere, mesosphere, thermosphere, atmosphere",
        "Cryosphere, stratosphere, mesosphere, thermosphere, Biosphere",
        "Atmosphere, biosphere, cryosphere, hydrosphere, lithosphere",
        "Biosphere, lithosphere, mesosphere, thermosphere, atmosphere"
    ],
    "correct": "Atmosphere, biosphere, cryosphere, hydrosphere, lithosphere"
},

{
    "id": 7,
    "text": "Which Ocean is primarily associated with ENSO events?",
    "options": [
        "Atlantic Ocean",
        "Indian Ocean",
        "Pacific Ocean",
        "Arctic Ocean"
    ],
    "correct": "Pacific Ocean"
},
{
    "id": 8,
    "text": "What is the warm phase of ENSO called?",
    "options": [
        "Trade wind",
        "La Niña",
        "Monsoon",
        "El Niño"
    ],
    "correct": "El Niño"
},

{
    "id": 9,
    "text": "Which of the following is the largest contributor to human-induced global warming?",
    "options": [
        "Oxygen",
        "Nitrogen",
        "Carbon dioxide",
        "Helium"
    ],
    "correct": "Carbon dioxide"
},

{
    "id": 10,
    "text": "Which greenhouse gas is primarily produced from livestock and rice cultivation?",
    "options": [
        "Methane (CH4)",
        "Oxygen (O2)",
        "Hydrogen (H2)",
        "Neon (Ne)"
    ],
    "correct": "Methane (CH4)"
},

{
    "id": 11,
    "text": "Which sector is a major source of greenhouse gas emissions globally?",
    "options": [
        "Agriculture",
        "Industrial processes",
        "Energy",
        "All of the above"
    ],
    "correct": "All of the above"
},

{
    "id": 12,
    "text": "Ocean currents primarily help to redistribute:",
    "options": [
        "Rocks and sediments only",
        "Heat energy around the Earth",
        "Earth’s magnetic field",
        "Solar radiation from space"
    ],
    "correct": "Heat energy around the Earth"
},
{
    "id": 13,
    "text": "The transfer of heat from the ocean to the atmosphere through evaporation is mainly in the form of:",
    "options": [
        "Latent heat",
        "Nuclear energy",
        "Gravitational energy",
        "Mechanical energy only"
    ],
    "correct": "Latent heat"
},

{
    "id": 14,
    "text": "Which ocean current is typically warm and influences coastal climates by increasing temperatures?",
    "options": [
        "Cold currents",
        "Deep ocean currents only",
        "Warm currents",
        "Subsurface currents only"
    ],
    "correct": "Warm currents"
},

{
    "id": 15,
    "text": "Upwelling in the ocean brings:",
    "options": [
        "Warm surface water downward",
        "Cold, nutrient-rich water to the surface",
        "Atmospheric gases into the ocean",
        "Freshwater into deep ocean basins"
    ],
    "correct": "Cold, nutrient-rich water to the surface"
},

{
    "id": 16,
    "text": "_________ is the main force that drives surface ocean currents.",
    "options": [
        "Earthquakes",
        "Volcanoes",
        "Lunar tides only",
        "Wind patterns"
    ],
    "correct": "Wind patterns"
},

{
    "id": 17,
    "text": "The Coriolis effect influences ocean currents by:",
    "options": [
        "Increasing ocean salinity",
        "Heating ocean water directly",
        "Deflecting currents due to Earth’s rotation",
        "Stopping all ocean movement"
    ],
    "correct": "Deflecting currents due to Earth’s rotation"
},
{
    "id": 18,
    "text": "According to WMO, what distinguishes climate change from climate variability?",
    "options": [
        "Climate change is driven entirely by the moon’s gravity",
        "Climate change persists for extended periods, typically decades or longer",
        "Climate change only affects the ocean, not the atmosphere",
        "Climate change is completely reversible within 2 – 7 years"
    ],
    "correct": "Climate change persists for extended periods, typically decades or longer"
},

{
    "id": 19,
    "text": "How often do ENSO events generally occur?",
    "options": [
        "Every 2 – 7 years",
        "Once every century",
        "Every 20 years",
        "Every month"
    ],
    "correct": "Every 2 – 7 years"
},

{
    "id": 20,
    "text": "Approximately how long does one complete MJO cycle take?",
    "options": [
        "1 – 3 days",
        "7 – 10 days",
        "2 – 3 years",
        "30 – 60 days"
    ],
    "correct": "30 – 60 days"
},

{
    "id": 21,
    "text": "The Madden-Julian Oscillation (MJO) mainly affects weather patterns in the:",
    "options": [
        "Tropics",
        "Polar regions",
        "Mediterranean region",
        "Arctic Ocean"
    ],
    "correct": "Tropics"
},

{
    "id": 22,
    "text": "ENSO events can influence:",
    "options": [
        "Global weather and climate patterns",
        "Only ocean temperatures",
        "Only rainfall in Europe",
        "Earthquakes and volcanoes directly"
    ],
    "correct": "Global weather and climate patterns"
},
{
    "id": 23,
    "text": "During a La Niña event, sea surface temperatures in the central and eastern Pacific Ocean are generally:",
    "options": [
        "Warmer than average",
        "Cooler than average",
        "Unchanged",
        "Extremely hot everywhere"
    ],
    "correct": "Cooler than average"
},

{
    "id": 24,
    "text": "MJO is characterised by:",
    "options": [
        "Changes in ocean salinity only",
        "Permanent cooling of the atmosphere",
        "Westward movement of hurricanes only",
        "Eastward movement of clouds, rainfall, winds and pressure"
    ],
    "correct": "Eastward movement of clouds, rainfall, winds and pressure"
},

{
    "id": 25,
    "text": "The MJO can influence:",
    "options": [
        "Only earthquakes",
        "Ocean tides only",
        "Tropical rainfall and cyclone activity",
        "Solar radiation directly"
    ],
    "correct": "Tropical rainfall and cyclone activity"
},

{
    "id": 26,
    "text": "El Niño conditions are typically associated with:",
    "options": [
        "Stronger than normal trade winds",
        "Weakened trade winds in the Pacific",
        "Cooler ocean temperatures in the Pacific",
        "Increased snowfall everywhere in the world"
    ],
    "correct": "Weakened trade winds in the Pacific"
},

{
    "id": 27,
    "text": "Which atmospheric pressure pattern is linked to ENSO?",
    "options": [
        "Southern Oscillation",
        "North Atlantic Oscillation",
        "Arctic Oscillation",
        "Indian Ocean Dipole"
    ],
    "correct": "Southern Oscillation"
},
{
    "id": 28,
    "text": "The Ekman spiral dictates that surface water transport is deflected at what angle to the prevailing wind?",
    "options": [
        "0° (parallel)",
        "45°",
        "90° (right angle)",
        "180° (opposite)"
    ],
    "correct": "90° (right angle)"
},

{
    "id": 29,
    "text": "Which ENSO phase is often linked to enhanced rainfall in some parts of southern Africa?",
    "options": [
        "El Niño",
        "Neutral phase",
        "Monsoon phase",
        "La Niña"
    ],
    "correct": "La Niña"
},

{
    "id": 30,
    "text": "Which of the following is a possible effect of El Niño over Zambia?",
    "options": [
        "Reduced atmospheric circulation",
        "Permanent climate change",
        "Increased dry spells/drought",
        "None of the above"
    ],
    "correct": "Increased dry spells/drought"
},

{
    "id": 31,
    "text": "How does a Positive Indian Ocean Dipole (IOD) uniquely affect Zambia’s rainfall patterns?",
    "options": [
        "Increases rainfall across the entire country",
        "Increases rainfall in the Northeast, suppresses it in the south",
        "Suppresses rainfall in the Northeast, increases in the South",
        "Has no measurable effect"
    ],
    "correct": "Increases rainfall in the Northeast, suppresses it in the south"
},

{
    "id": 32,
    "text": "Figure 1 below displays rainfall totals for February from 1935 to 1985 for a hypothetical observation station. What does this figure depict?",
    "image": "q32.png",
    "options": [
        "Ozone depletion",
        "Global warming only",
        "Climate Change",
        "Climate variability"
    ],
    "correct": "Climate variability"
},
{
    "id": 33,
    "text": "Figure 2 below shows annual rainfall totals at a hypothetical weather observation station. What does this plot depict?",
    "image": "q33.png",
    "options": [
        "Ozone depletion",
        "Climate change",
        "Climate variability and climate change",
        "Climate variability"
    ],
    "correct": "Climate variability and climate change"
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

    if request.method == 'POST':

        name = request.form.get('name')
        email = request.form.get('email')

        # Prevent multiple attempts using same email
        if os.path.exists(CSV_FILE):

            with open(CSV_FILE, 'r') as file:

                reader = csv.reader(file)
                next(reader, None)

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

    with open(CSV_FILE, 'r') as file:

        reader = csv.reader(file)
        next(reader)

        for index, row in enumerate(reader):

            results.append({
                'id': index,
                'name': row[0],
                'email': row[1],
                'score': row[2],
                'total': row[3],
                'percentage': row[4],
                'answers': row[5],
                'date': row[6]
            })

    return render_template('admin.html', results=results)


@app.route('/review/<int:result_id>')
def review(result_id):

    if session.get('role') != 'admin':
        return redirect(url_for('landing'))

    with open(CSV_FILE, 'r') as file:

        reader = list(csv.reader(file))

        row = reader[result_id + 1]

        answers = json.loads(row[5])

        return render_template(
            'review.html',
            name=row[0],
            email=row[1],
            score=row[2],
            total=row[3],
            percentage=row[4],
            answers=answers
        )


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
