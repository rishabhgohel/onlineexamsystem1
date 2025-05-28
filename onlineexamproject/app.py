import math
from flask import Flask, render_template, request, jsonify,redirect,url_for,Response,flash,session
import os
from flask_mysqldb import MySQL
import warnings
import utils
import datetime
import cv2
import mysql.connector
import time
import json 
import csv
from werkzeug.utils import secure_filename

#variables
studentInfo=None
camera=None
profileName=None
conn=None

#Flak's Application Confguration
warnings.filterwarnings("ignore")
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'str'
os.path.dirname("../templates")

#Flak's Database Configuration
app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'rishabh8001'  
app.config['MYSQL_PASSWORD'] = 'MyNew330@sql'  
app.config['MYSQL_DB'] = 'onlineexam'  
app.config['MYSQL_HOST'] = 'localhost'
app.config['UPLOAD_FOLDER'] = 'uploads'  # Folder to save uploaded files
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = { 'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mysql = MySQL(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/add_question', methods=['POST'])
def add_question():
    if request.method == 'POST':
        question = request.form['question']
        question_type = request.form['question_type']
        correct_answer = request.form['correct_answer']

        # Handle MCQ options
        option1 = request.form.get('option1', None)
        option2 = request.form.get('option2', None)
        option3 = request.form.get('option3', None)
        option4 = request.form.get('option4', None)

        # Insert the question into the database
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO questions (Question, QuestionType, Option1, Option2, Option3, Option4, CorrectAnswer)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (question, question_type, option1, option2, option3, option4, correct_answer))
        mysql.connection.commit()
        cur.close()

        flash("Question added successfully!", "success")
        return redirect(url_for('adminStudents'))

@app.route('/schedule_exam', methods=['POST'])
def schedule_exam():
    if request.method == 'POST':
        subject_id = request.form['subject_id']
        exam_date = request.form['exam_date']
        exam_time = request.form['exam_time']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO exams (SubjectID, ExamDate, ExamTime) VALUES (%s, %s, %s)", (subject_id, exam_date, exam_time))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('aadmin_panel'))        


@app.route('/upload_question_bank', methods=['POST'])
def upload_question_bank():
    if 'question_bank' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('adminStudents'))

    file = request.files['question_bank']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('adminStudents'))

    # Save the file and process it
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Process the file (e.g., extract questions and save to database)
    process_question_bank(filepath)

    flash('Question Bank uploaded successfully!', 'success')
    return redirect(url_for('adminStudents'))

def process_question_bank(filepath):
    """Process the uploaded question bank file and save questions to the database."""
    # Clear old questions
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM questions")
    mysql.connection.commit()

    # Process the new file
    if filepath.endswith('.csv'):
        with open(filepath, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                question = row['Question']
                question_type = row['Type']
                option1 = row.get('Option1', None)
                option2 = row.get('Option2', None)
                option3 = row.get('Option3', None)
                option4 = row.get('Option4', None)
                correct_answer = row['CorrectAnswer'].strip().lower()

                # Insert the question into the database
                cur.execute("""
                    INSERT INTO questions (Question, QuestionType, Option1, Option2, Option3, Option4, CorrectAnswer)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (question, question_type, option1, option2, option3, option4, correct_answer))
    mysql.connection.commit()
    cur.close()

def extract_questions(filepath):
    """Extract questions from the uploaded file."""
    questions = []
    with open(filepath, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 6:  
                questions.append({
                    'title': row[0],
                    'choices': [row[1], row[2], row[3], row[4]],
                    'answer': row[5]
                })
    return questions

def save_questions_to_db(questions):
    """Save extracted questions to the database."""
    cur = mysql.connection.cursor()
    for question in questions:
        cur.execute("""
            INSERT INTO questions (Subject, Title, Choice1, Choice2, Choice3, Choice4, Answer)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, ('Maths', question['title'], question['choices'][0], question['choices'][1], question['choices'][2], question['choices'][3], question['answer']))
    mysql.connection.commit()
    cur.close()

#Function to show face detection's Rectangle in Face Input Page
def capture_by_frames():
    global camera
    utils.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  
    if not utils.cap.isOpened():
        print("Error: Unable to access the camera.")
        return
    while True:
        success, frame = utils.cap.read()  # Read the camera frame
        if not success:
            print("Error: Failed to read frame from the camera.")
            break
        detector = cv2.CascadeClassifier('Haarcascades/haarcascade_frontalface_default.xml')
        if detector.empty():
            print("Error: Haarcascade file not found or invalid.")
        faces = detector.detectMultiScale(frame, 1.2, 6)
        # Draw rectangles around detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

#Function to run Cheat Detection when we start run the Application
@app.before_request
def start_loop():
    pass

#Login Related
@app.route('/')
def main():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    global studentInfo
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM students where Email='" + username + "' and Password='" + password + "'")
        data = cur.fetchone()
        if data is None:  
            flash('Your Email or Password is incorrect, try again.', category='error')
            return redirect(url_for('main'))
        else:
            id, name, email,password, role = data
            studentInfo={ "Id": id, "Name": name, "Email": email, "Password": password}
            if role == 'STUDENT':
                utils.Student_Name = name
                return redirect(url_for('rules'))
            else:
                return redirect(url_for('adminStudents'))

@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    # Add a flash message
    flash("You have been logged out successfully.", "success")
    # Redirect to the login page
    return redirect(url_for('main'))

#Student Related
@app.route('/rules')
def rules():
    return render_template('ExamRules.html')

@app.route('/faceInput')
def faceInput():
    return render_template('ExamFaceInput.html')

@app.route('/video_capture')
def video_capture():
    return Response(capture_by_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/saveFaceInput')
def saveFaceInput():
    global profileName
    if utils.cap.isOpened():
        utils.cap.release()

    cam = cv2.VideoCapture(0)  # Use the default camera (index 0)
    if not cam.isOpened():
        print("Error: Unable to access the camera.")
        return "Error: Unable to access the camera.", 500

    success, frame = cam.read()  # Read the camera frame
    if not success or frame is None:
        print("Error: Failed to capture frame from the camera.")
        cam.release()
        return "Error: Failed to capture frame from the camera.", 500

    profileName = f"{studentInfo['Name']}_{utils.get_resultId():03}" + "Profile.jpg"
    cv2.imwrite(profileName, frame)
    utils.move_file_to_output_folder(profileName, 'Profiles')
    cam.release()
    return redirect(url_for('confirmFaceInput'))

@app.route('/confirmFaceInput')
def confirmFaceInput():
    profile = profileName
  #  utils.fr.encode_faces()
    return render_template('ExamConfirmFaceInput.html', profile = profile)

@app.route('/systemCheck')
def systemCheck():
    return render_template('ExamSystemCheck.html')

@app.route('/systemCheck', methods=["POST"])
def systemCheckRoute():
    if request.method == 'POST':
        examData = request.json
        output = 'exam'
        if 'Not available' in examData['input'].split(';'): output = 'systemCheckError'
    return jsonify({"output": output})

@app.route('/systemCheckError')
def systemCheckError():
    return render_template('ExamSystemCheckError.html')

@app.route('/exam', methods=["GET", "POST"])
def exam():
    global studentInfo
    import os, json

    if request.method == "GET":
        if not studentInfo:
            flash("Please login first.", "error")
            return redirect(url_for('main'))

        cur = mysql.connection.cursor()
        cur.execute("SELECT QuestionID, Question, Option1, Option2, Option3, Option4, CorrectAnswer FROM questions")
        questions = cur.fetchall()
        cur.close()
        return render_template('Exam.html', questions=questions)

    elif request.method == "POST":
        examData = request.json
        print("✅ POST data received:", examData)

        if examData['input'] != '':
            totalMark = math.floor(float(examData['input']) * 1)  # Student's score
            cur = mysql.connection.cursor()
            cur.execute("SELECT COUNT(*) FROM questions")  # Get total number of questions
            total_questions = cur.fetchone()[0]
            cur.close()

            total_marks = total_questions  
            passing_marks = total_marks / 2  

            # Determine pass/fail status
            status = "Pass" if totalMark >= passing_marks else "Fail"
            link = 'showResultPass' if status == "Pass" else 'showResultFail'
            exam_date = time.strftime("%Y-%m-%d", time.localtime(time.time()))
            profile_img = profileName if profileName else "default.jpg"

            result_entry = {
                "Id": utils.get_resultId(),
                "Name": studentInfo['Name'],
                "TotalMark": totalMark,
                "Status": status,
                "Date": exam_date,
                "StId": studentInfo['Id'],
                "Link": profile_img,
                "Grade": status
            }

            result_path = "result.json"
            try:
                with open(result_path, "r") as f:
                    result_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                result_data = []

            result_data.append(result_entry)

            with open(result_path, "w") as f:
                json.dump(result_data, f, indent=4)

            resultStatus = f"{studentInfo['Name']};{status};{totalMark};{exam_date};{profile_img}"
            return jsonify({"output": resultStatus, "link": link})
        else:
            return jsonify({"output": "", "link": ""})


@app.route('/showResultPass/<result_status>')
def showResultPass(result_status):
    return render_template('ExamResultPass.html',result_status=result_status)

@app.route('/showResultFail/<result_status>')
def showResultFail(result_status):
    return render_template('ExamResultFail.html',result_status=result_status)

@app.route('/log_tab_switch', methods=['POST'])
def log_tab_switch():
    global studentInfo
    if request.method == 'POST':
        data = request.json
        tab_switch_count = data.get('tabSwitchCount', 0)
        print(f"Tab switch detected. Count: {tab_switch_count}")

        # Log the tab switch event
        with open('tab_switch_logs.txt', 'a') as log_file:
            log_file.write(f"Student ID: {studentInfo['Id']}, Tab Switch Count: {tab_switch_count}, Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Handle warnings and failure
        if tab_switch_count == 1:
            return jsonify({"message": "Warning issued", "action": "warn"})
        elif tab_switch_count >= 2:
            # Automatically fail the student
            utils.write_json({
                "Id": utils.get_resultId(),
                "Name": studentInfo['Name'],
                "TotalMark": 0,
                "Status": "Fail",
                "Date": time.strftime("%Y-%m-%d", time.localtime(time.time())),
                "StId": studentInfo['Id'],
                "link": profileName if profileName else "default.jpg",
                "Grade": "Cheating detected"
            }, "result.json")
            return jsonify({"message": "Student failed due to cheating", "action": "fail"})

        return jsonify({"message": "Tab switch logged successfully", "action": "none"})

#Admin Related
@app.route('/adminResults')
def adminResults():
    try:
        with open("result.json", "r") as f:
            data = json.load(f)
        results = [
            (r["Name"], r["TotalMark"], r["Grade"], r["Date"], r["Status"])
            for r in data
        ]
    except:
        results = []
    return render_template("Students.html", results=results)

@app.route('/adminStudents')
def adminStudents():
    cur = mysql.connection.cursor()

    # Fetch students for the Students section
    cur.execute("SELECT * FROM students WHERE Role='STUDENT'")
    students = cur.fetchall()

    # Fetch questions
    cur.execute("SELECT QuestionID, Question, QuestionType, CorrectAnswer FROM questions")
    questions = cur.fetchall()
    
    cur.close()
    return render_template('Students.html',students=students,questions=questions)

@app.route('/insertStudent', methods=['POST'])
def insertStudent():
    if request.method == "POST":
        name = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO students (Name, Email, Password, Role) VALUES (%s, %s, %s, %s)", (name, email, password,role))
        mysql.connection.commit()
        return redirect(url_for('adminStudents'))

@app.route('/deleteStudent/<int:student_id>', methods=['POST'])
def deleteStudent(student_id):
    try:
        # Delete the student record from the database
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM students WHERE ID = %s", (student_id,))
        mysql.connection.commit()
        cur.close()
        flash("Student deleted successfully!", "success")
    except Exception as e:
        flash(f"An error occurred: {e}", "danger")
    return redirect(url_for('adminStudents'))

@app.route('/updateStudent', methods=['POST', 'GET'])
def updateStudent():
    if request.method == 'POST':
        id_data = request.form['id']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("""
               UPDATE students
               SET Name=%s, Email=%s, Password=%s
               WHERE ID=%s
            """, (name, email, password, id_data))
        mysql.connection.commit()
        return redirect(url_for('adminStudents'))

@app.route('/add_student', methods=['POST'])
def add_student():
    if request.method == 'POST':
        # Get data from the request
        student_name = request.form['StudentName']
        email = request.form['Email']
        password = request.form['Password']
        role = request.form['Role']

        # Insert data into the database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO students (StudentName, Email, Password, Role) VALUES (%s, %s, %s, %s)",
                    (student_name, email, password, role))
        mysql.connection.commit()
        cur.close()

        flash("Student added successfully!", "success")
        return redirect(url_for('adminStudents'))
    return render_template('student.html')
    
@app.route('/delete_question/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM questions WHERE QuestionID = %s", (question_id,))
        mysql.connection.commit()
        cur.close()
        flash("Question deleted successfully!", "success")
    except Exception as e:
        flash(f"An error occurred: {e}", "danger")
    return redirect(url_for('adminStudents'))

@app.route('/api/results', methods=['GET'])
def api_results():
    try:
        with open("result.json", "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    return jsonify({"results": data})

if __name__ == '__main__':
    # Set the working directory to the project folder
    project_folder = os.path.dirname(os.path.abspath(__file__))
    print(os.getcwd()) 
    app.run(debug=True)


