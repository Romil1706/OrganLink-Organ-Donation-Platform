from flask import Flask, render_template, request, redirect, session
import mysql.connector
import joblib
from flask import send_from_directory
import os
from werkzeug.utils import secure_filename
from gemini_extractor import extract_medical_data
from ai_matcher import predict_match
model = joblib.load("organlink_model.pkl")
app = Flask(__name__)
app.secret_key = "organlink123"
# =========================
# DATABASE CONNECTION
# =========================

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Mkg@281005",
    database="organlink"
)

cursor = db.cursor(buffered=True)

# =========================
# HOME PAGE
# =========================

@app.route('/')
def home():
    return render_template('index.html')

# =========================
# REGISTER PAGE
# =========================

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        session['fullname'] = request.form['fullname']
        session['email'] = request.form['email']
        session['password'] = request.form['password']
        session['age'] = request.form['age']
        session['gender'] = request.form['gender']
        session['blood_group'] = request.form['blood_group']
        session['phone'] = request.form['phone']
        session['role'] = request.form['role']

        return redirect('/terms')

    return render_template('register.html')

# =========================
# LOGIN PAGE
# =========================

@app.route('/login', methods=['GET', 'POST'])
def login():

    error = None

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        sql = """
        SELECT * FROM accounts
        WHERE email=%s AND password=%s
        """

        cursor.execute(sql, (email, password))
        user = cursor.fetchone()

        if user:
            session['user_id'] = user[0]
            session['fullname'] = user[1]
            session['email'] = user[2]
            session['role'] = user[4]
            role = user[4]

            if role == "admin":
                return redirect('/admin')

            elif role == "hospital":
                return redirect('/hospital')

            elif role == "donor":
                return redirect('/donor')

            elif role == "recipient":
                return redirect('/recipient')

    return render_template('login.html', error=error)
@app.route('/hospital')
def hospital():
    return render_template('hospital.html')
# =========================
# DONOR DASHBOARD
# =========================

@app.route('/donor')
def donor():
    return render_template('donor.html')

# =========================
# RECIPIENT DASHBOARD
# =========================

@app.route('/recipient')
def recipient():
    return render_template('recipient.html')

@app.route('/profile')
def profile():

    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']

    cursor.execute(
        "SELECT * FROM accounts WHERE id=%s",
        (user_id,)
    )

    user = cursor.fetchone()

    return render_template(
        'profile.html',
        user=user
    )
@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')
@app.route('/view-donors')
def view_donors():

    cursor.execute(
        "SELECT fullname,email,age,gender,blood_group,phone FROM accounts WHERE role='donor'"
    )

    donors = cursor.fetchall()

    return render_template(
        'view_donors.html',
        donors=donors
    )
@app.route('/view-recipients')
def view_recipients():

    cursor.execute(
        "SELECT fullname,email,age,gender,blood_group,phone FROM accounts WHERE role='recipient'"
    )

    recipients = cursor.fetchall()

    return render_template(
        'view_recipients.html',
        recipients=recipients
    )
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():

    user_id = session['user_id']

    if request.method == 'POST':

        age = request.form['age']
        gender = request.form['gender']
        blood_group = request.form['blood_group']
        phone = request.form['phone']

        cursor.execute("""
            UPDATE accounts
            SET age=%s,
                gender=%s,
                blood_group=%s,
                phone=%s
            WHERE id=%s
        """, (age, gender, blood_group, phone, user_id))

        db.commit()

        return redirect('/profile')

    cursor.execute(
        "SELECT * FROM accounts WHERE id=%s",
        (user_id,)
    )

    user = cursor.fetchone()

    return render_template(
        'edit_profile.html',
        user=user
    )
 
@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/organ-registration', methods=['GET', 'POST'])
def organ_registration():

    if request.method == 'POST':

        organs = request.form.getlist('organs')
        donor_status = request.form['donor_status']

        user_id = session['user_id']

        for organ in organs:

            cursor.execute("""
                INSERT INTO organ
                (user_id, organ, donor_status, status)
                VALUES (%s,%s,%s,%s)
            """, (
                user_id,
                organ,
                donor_status,
                "Pending"
            ))

        db.commit()

        return redirect('/donor')

    return render_template('organ_registration.html')
@app.route('/donation-status')
def donation_status():

    user_id = session['user_id']

    cursor.execute("""
    SELECT organ,
           donor_status,
           status
    FROM organ
    WHERE user_id=%s
""",(user_id,))

    registrations = cursor.fetchall()

    return render_template(
        'donation_status.html',
        registrations=registrations
    )
@app.route('/medical-reports', methods=['GET', 'POST'])
def medical_reports():

    # ==========================================
    # CHECK LOGIN
    # ==========================================

    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']

    # ==========================================
    # UPLOAD REPORT
    # ==========================================

    if request.method == 'POST':

        report_name = request.form['report_name']

        file = request.files.get('report')

        if file and allowed_file(file.filename):

            # ==========================================
            # CREATE SAFE FILE NAME
            # ==========================================

            filename = f"{user_id}_{secure_filename(file.filename)}"

            pdf_path = os.path.join(
                app.config['UPLOAD_FOLDER'],
                filename
            )

            # ==========================================
            # SAVE PDF
            # ==========================================

            file.save(pdf_path)

            # ==========================================
            # SAVE ORIGINAL REPORT INFORMATION
            # ==========================================

            cursor.execute("""
                INSERT INTO uploaded_reports
                (
                    user_id,
                    report_name,
                    pdf_file
                )
                VALUES (%s, %s, %s)
            """, (
                user_id,
                report_name,
                filename
            ))

            # ==========================================
            # RUN GEMINI EXTRACTION
            # ==========================================

            medical_data = extract_medical_data(
                pdf_path
            )

            print("\n==============================")
            print("GEMINI EXTRACTED MEDICAL DATA")
            print("==============================")
            print(medical_data)
            print("==============================\n")

            # ==========================================
            # ONLY SAVE IF GEMINI DID NOT RETURN ERROR
            # ==========================================

            if "error" not in medical_data:

                cursor.execute("""
                    INSERT INTO medical_reports
                    (
                        user_id,
                        blood_group,
                        hemoglobin,
                        creatinine,
                        egfr,
                        hiv_status,
                        hepatitis_b_status,
                        hepatitis_c_status,
                        hla_a1,
                        hla_a2,
                        hla_b1,
                        hla_b2,
                        hla_dr1,
                        hla_dr2,
                        crossmatch_result,
                        report_date
                    )
                    VALUES
                    (
                        %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s, %s
                    )
                """, (

                    user_id,

                    medical_data.get(
                        "blood_group",
                        "Not Found"
                    ),

                    medical_data.get(
                        "hemoglobin",
                        "Not Found"
                    ),

                    medical_data.get(
                        "creatinine",
                        "Not Found"
                    ),

                    medical_data.get(
                        "egfr",
                        "Not Found"
                    ),

                    medical_data.get(
                        "hiv_status",
                        "Not Found"
                    ),

                    medical_data.get(
                        "hepatitis_b_status",
                        "Not Found"
                    ),

                    medical_data.get(
                        "hepatitis_c_status",
                        "Not Found"
                    ),

                    medical_data.get(
                        "hla_a1",
                        "Not Found"
                    ),

                    medical_data.get(
                        "hla_a2",
                        "Not Found"
                    ),

                    medical_data.get(
                        "hla_b1",
                        "Not Found"
                    ),

                    medical_data.get(
                        "hla_b2",
                        "Not Found"
                    ),

                    medical_data.get(
                        "hla_dr1",
                        "Not Found"
                    ),

                    medical_data.get(
                        "hla_dr2",
                        "Not Found"
                    ),

                    medical_data.get(
                        "crossmatch_result",
                        "Not Found"
                    ),

                    medical_data.get(
                        "report_date",
                        "Not Found"
                    )

                ))

            else:

                print(
                    "Gemini extraction failed:",
                    medical_data["error"]
                )

            # ==========================================
            # SAVE DATABASE CHANGES
            # ==========================================

            db.commit()

            # Prevent duplicate form submission
            return redirect('/medical-reports')

    # ==========================================
    # LOAD USER REPORTS
    # ==========================================

    cursor.execute("""
        SELECT
            report_name,
            pdf_file,
            uploaded_at
        FROM uploaded_reports
        WHERE user_id=%s
        ORDER BY uploaded_at DESC
    """, (user_id,))

    reports = cursor.fetchall()

    return render_template(
        'medical_reports.html',
        reports=reports
    )
@app.route('/verify-donors')
def verify_donors():

    cursor.execute("""
        SELECT id,
               fullname,
               email,
               blood_group,
               phone,
               verification_status
        FROM accounts
        WHERE role='donor'
    """)

    donors = cursor.fetchall()
    print(donors)
    return render_template(
        'verify_donors.html',
        donors=donors
    )
@app.route('/verify-user/<int:user_id>')
def verify_user(user_id):

    cursor.execute("""
        UPDATE accounts
        SET verification_status='Verified'
        WHERE id=%s
    """,(user_id,))

    db.commit()

    return redirect(request.referrer)
@app.route('/verify-recipients')
def verify_recipients():

    cursor.execute("""
        SELECT id,
               fullname,
               email,
               age,
               gender,
               blood_group,
               phone,
               verification_status
        FROM accounts
        WHERE role='recipient'
    """)

    recipients = cursor.fetchall()

    return render_template(
        'verify_recipients.html',
        recipients=recipients
    )
@app.route('/hospital-reports')
def hospital_reports():

    cursor.execute("""
        SELECT
            accounts.fullname,
            accounts.role,
            uploaded_reports.report_name,
            uploaded_reports.pdf_file,
            uploaded_reports.uploaded_at

        FROM uploaded_reports

        JOIN accounts
        ON uploaded_reports.user_id = accounts.id
    """)

    reports = cursor.fetchall()

    return render_template(
        'hospital_reports.html',
        reports=reports
    )
@app.route('/view-hospitals')
def view_hospitals():

    cursor.execute("""
        SELECT
            fullname,
            email,
            phone,
            address,
            area
        FROM accounts
        WHERE role='hospital'
    """)

    hospitals = cursor.fetchall()

    return render_template(
        'view_hospitals.html',
        hospitals=hospitals
    )


@app.route('/add-hospital', methods=['GET', 'POST'])
def add_hospital():

    if request.method == 'POST':

        fullname = request.form['fullname']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        address = request.form['address']
        area = request.form['area']

        cursor.execute("""
            INSERT INTO accounts
            (
                fullname,
                email,
                password,
                role,
                phone,
                address,
                area
            )
            VALUES(%s,%s,%s,%s,%s,%s,%s)
        """, (
            fullname,
            email,
            password,
            'hospital',
            phone,
            address,
            area
        ))

        db.commit()

        return redirect('/view-hospitals')

    return render_template('add_hospital.html')
@app.route('/view-users')
def view_users():

    cursor.execute("""
        SELECT
        id,
        fullname,
        email,
        role
        FROM accounts
    """)

    users = cursor.fetchall()

    return render_template(
        'view_users.html',
        users=users
    )
@app.route('/system')
def system():

    cursor.execute(
        "SELECT COUNT(*) FROM accounts"
    )
    total_users = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM accounts WHERE role='donor'"
    )
    total_donors = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM accounts WHERE role='recipient'"
    )
    total_recipients = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM accounts WHERE role='hospital'"
    )
    total_hospitals = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM organ"
    )
    total_registrations = cursor.fetchone()[0]

    return render_template(
        'system.html',
        total_users=total_users,
        total_donors=total_donors,
        total_recipients=total_recipients,
        total_hospitals=total_hospitals,
        total_registrations=total_registrations
    )
@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/accept-terms', methods=['POST'])
def accept_terms():

    sql = """
    INSERT INTO accounts
    (fullname,email,password,role,age,gender,blood_group,phone)
    VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
    """

    values = (
        session['fullname'],
        session['email'],
        session['password'],
        session['role'],
        session['age'],
        session['gender'],
        session['blood_group'],
        session['phone']
    )

    cursor.execute(sql, values)
    db.commit()

    session.clear()

    return redirect('/login')


@app.route('/hospital-add-recipient', methods=['GET', 'POST'])
def hospital_add_recipient():

    if request.method == 'POST':

        fullname = request.form['fullname']
        email = request.form['email']
        password = request.form['password']
        age = request.form['age']
        gender = request.form['gender']
        blood_group = request.form['blood_group']
        phone = request.form['phone']

        cursor.execute("""
            INSERT INTO accounts
            (
                fullname,
                email,
                password,
                role,
                age,
                gender,
                blood_group,
                phone,
                verification_status
            )
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,(
            fullname,
            email,
            password,
            'recipient',
            age,
            gender,
            blood_group,
            phone,
            'Verified'
        ))

        db.commit()

        return redirect('/verify-recipients')

    return render_template(
        'hospital_add_recipient.html'
    )
@app.route('/ai-matching')
def ai_matching():
    return render_template('ai_matching.html')
# =========================
# RUN APP
# =========================

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )
@app.route('/view-report/<filename>')
def view_report(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename
    )
@app.route('/download-report/<filename>')
def download_report(filename):

    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename,
        as_attachment=True
    )
@app.route('/organ-request', methods=['GET', 'POST'])
def organ_request():

    if request.method == 'POST':

        organ = request.form['organ']
        urgency = request.form['urgency']
        condition = request.form['condition']

        cursor.execute("""
        INSERT INTO recipient_requests
        (user_id, organ, urgency, condition_details)
        VALUES (%s,%s,%s,%s)
        """, (
            session['user_id'],
            organ,
            urgency,
            condition
        ))

        db.commit()

        return redirect('/request-status')

    return render_template('organ_request.html')
@app.route('/request-status')
def request_status():

    cursor.execute("""
        SELECT organ,
               urgency,
               status
        FROM recipient_requests
        WHERE user_id=%s
    """, (session['user_id'],))

    requests = cursor.fetchall()

    return render_template(
        'request_status.html',
        requests=requests
    )
@app.route('/waiting-list')
def waiting_list():

    user_id = session['user_id']

    cursor.execute("""
        SELECT id, organ, urgency, created_at
        FROM recipient_requests
        WHERE user_id = %s
    """, (user_id,))

    my_request = cursor.fetchone()

    if not my_request:
        return render_template(
            'waiting_list.html',
            position="No Request Found",
            request=None
        )

    organ = my_request[1]

    cursor.execute("""
        SELECT user_id
        FROM recipient_requests
        WHERE organ = %s
        ORDER BY
        CASE urgency
            WHEN 'High' THEN 1
            WHEN 'Medium' THEN 2
            WHEN 'Low' THEN 3
        END,
        created_at ASC
    """, (organ,))

    waiting_list = cursor.fetchall()

    position = 1

    for row in waiting_list:
        if row[0] == user_id:
            break
        position += 1

    return render_template(
        'waiting_list.html',
        position=position,
        request=my_request
    )

@app.route('/ai-compatibility')
def ai_compatibility():

    # Make sure the user is logged in
    if 'fullname' not in session:
        return redirect('/login')

    recipient = {
        "fullname": session['fullname'],
        "blood_group": "O+",
        "organ": "Kidney"
    }

    # Demo data only — not database/model predictions
    matches = [
        {
            "id": 1,
            "name": "Rahul Patel",
            "blood_group": "O+",
            "organ": "Kidney",
            "score": 95
        },
        {
            "id": 2,
            "name": "Priya Shah",
            "blood_group": "O+",
            "organ": "Kidney",
            "score": 87
        },
        {
            "id": 3,
            "name": "Amit Kumar",
            "blood_group": "O+",
            "organ": "Kidney",
            "score": 76
        }
    ]

    # Remove duplicate donors by unique ID
    unique_matches = []
    seen_ids = set()

    for donor in matches:
        if donor["id"] not in seen_ids:
            unique_matches.append(donor)
            seen_ids.add(donor["id"])

    # Sort from highest to lowest score
    unique_matches.sort(
        key=lambda donor: float(donor["score"]),
        reverse=True
    )

    return render_template(
        'ai_compatibility.html',
        recipient=recipient,
        matches=unique_matches
    )

@app.route('/hospital-ai-matching')
def hospital_ai_matching():

    if session['role'] != 'hospital':
        return redirect('/login')

    cursor.execute("""
        SELECT
            a.id,
            a.fullname,
            a.blood_group
        FROM accounts a
        JOIN recipient_requests r
        ON a.id = r.user_id
        WHERE a.role='recipient'
    """)

    recipients = cursor.fetchall()

    return render_template(
        'hospital_ai_matching.html',
        recipients=recipients
    )
@app.route('/run-ai-matching', methods=['POST'])
def run_ai_matching():

    if session['role'] != 'hospital':
        return redirect('/login')

    recipient_id = request.form['recipient_id']

    # ==========================================
    # RECIPIENT DETAILS
    # ==========================================

    cursor.execute("""
        SELECT
            a.fullname,
            a.age,
            a.gender,
            a.blood_group,
            r.organ
        FROM accounts a
        JOIN recipient_requests r
            ON a.id = r.user_id
        WHERE a.id=%s
    """, (recipient_id,))

    recipient = cursor.fetchone()

    if not recipient:
        return "Recipient not found"

    recipient_name = recipient[0]
    recipient_age = recipient[1]
    recipient_gender = recipient[2]
    recipient_blood = recipient[3]
    recipient_organ = recipient[4]

    # ==========================================
    # RECIPIENT MEDICAL REPORT
    # ==========================================

    cursor.execute("""
        SELECT
            hla_a1,
            hla_a2,
            hla_b1,
            hla_b2,
            hla_dr1,
            hla_dr2,
            crossmatch_result
        FROM medical_reports
        WHERE user_id=%s
        ORDER BY id DESC
        LIMIT 1
    """, (recipient_id,))

    recipient_report = cursor.fetchone()

    if not recipient_report:
        return "Recipient medical report not found"

   # ==========================================
# DONORS
# ==========================================

    cursor.execute("""
        SELECT
        a.id,
        a.fullname,
        a.age,
        a.gender,
        a.blood_group,
        o.organ
    FROM accounts a
    JOIN organ o
        ON a.id = o.user_id
    WHERE a.role='donor'
""")

    donors = cursor.fetchall()
    print("\n========== ALL DONORS ==========")
    for d in donors:
        print(d)
    print("================================\n")

    matches = []

    # ==========================================
    # CHECK DONORS
    # ==========================================

    for donor in donors:

        donor_id = donor[0]
        donor_name = donor[1]
        donor_age = donor[2]
        donor_gender = donor[3]
        donor_blood = donor[4]
        donor_organ = donor[5]

        # ==========================================
        # DONOR MEDICAL REPORT
        # ==========================================

        cursor.execute("""
            SELECT
                hla_a1,
                hla_a2,
                hla_b1,
                hla_b2,
                hla_dr1,
                hla_dr2,
                crossmatch_result
            FROM medical_reports
            WHERE user_id=%s
            ORDER BY id DESC
            LIMIT 1
        """, (donor_id,))

        donor_report = cursor.fetchone()

        if not donor_report:
            continue

        # ==========================================
        # HLA SCORE
        # ==========================================

        hla_match_score = 0

        if donor_report[0] == recipient_report[0]:
            hla_match_score += 15

        if donor_report[1] == recipient_report[1]:
            hla_match_score += 15

        if donor_report[2] == recipient_report[2]:
            hla_match_score += 15

        if donor_report[3] == recipient_report[3]:
            hla_match_score += 15

        if donor_report[4] == recipient_report[4]:
            hla_match_score += 20

        if donor_report[5] == recipient_report[5]:
            hla_match_score += 20

        # ==========================================
        # AI PREDICTION
        # ==========================================
        print("DONOR:", donor_name)
        print("donor_age:", donor_age)
        print("donor_gender:", donor_gender)
        print("donor_blood:", donor_blood)
        print("donor_organ:", donor_organ)

        print("recipient_age:", recipient_age)
        print("recipient_gender:", recipient_gender)
        print("recipient_blood:", recipient_blood)
        print("recipient_organ:", recipient_organ)

        print("hla_match_score:", hla_match_score)
        print("crossmatch:", donor_report[6])
        ai_prediction, ai_probability = predict_match(

            donor_age=donor_age,
            donor_gender=donor_gender,
            donor_blood_group=donor_blood,
            donor_organ=donor_organ,

            recipient_age=recipient_age,
            recipient_gender=recipient_gender,
            recipient_blood_group=recipient_blood,
            required_organ=recipient_organ,

            hla_match_score=hla_match_score,

            crossmatch_result=donor_report[6]
        )

        # ==========================================
        # LABEL
        # ==========================================

        if ai_prediction == 1:
            prediction = "Compatible"
        else:
            prediction = "Not Compatible"

        matches.append({

            "id": donor_id,

            "name": donor_name,

            "blood_group": donor_blood,

            "organ": donor_organ,

            "hla_score": hla_match_score,

            "prediction": prediction,

            "ai_probability": ai_probability

        })

    # ==========================================
    # SORT BY AI CONFIDENCE
    # ==========================================

    matches.sort(
        key=lambda x: x['ai_probability'],
        reverse=True
    )

    # ==========================================
    # DISPLAY RESULTS
    # ==========================================

    return render_template(

        'matching_results.html',

        recipient_name=recipient_name,

        recipient_blood=recipient_blood,

        recipient_organ=recipient_organ,

        matches=matches

    )
if __name__ == '__main__':
    app.run(debug=True)

