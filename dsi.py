from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
from pymongo.errors import DuplicateKeyError

app = Flask(__name__)

# --- MongoDB Configuration ---
app.config["MONGO_URI"] = "mongodb+srv://haromedb:P8iZzZZfx9WviOBb@harodb.gtgicdm.mongodb.net/DSI-ERD-SIS?retryWrites=true&w=majority"
mongo = PyMongo(app)

# --- Helper: Clean student data for JSON ---
def clean_student(student):
    student["_id"] = str(student["_id"])
    if "birth_date" in student and isinstance(student["birth_date"], datetime):
        student["birth_date"] = student["birth_date"].strftime("%Y-%m-%d")
    if "program_id" in student and student["program_id"]:
        student["program_id"] = str(student["program_id"])
    return student

# --- Helper: Clean program data for dropdown ---
def clean_program(program):
    program["_id"] = str(program["_id"])
    return program

# --- Helper: Resolve program name for a student ---
def resolve_program_name(student):
    if "program_name" not in student or not student["program_name"]:
        if "program_id" in student and student["program_id"]:
            try:
                program = mongo.db.program.find_one({"_id": ObjectId(student["program_id"])})
                if program:
                    student["program_name"] = program.get("program_name")
            except:
                student["program_name"] = None
    return student

# --- Home route: show students table ---
@app.route('/')
def index():
    students_cursor = mongo.db.student.find()
    students_cleaned = []
    for s in students_cursor:
        s = clean_student(s)
        s = resolve_program_name(s)
        students_cleaned.append(s)

    programs_cursor = mongo.db.program.find()
    programs_cleaned = [clean_program(p) for p in programs_cursor]

    return render_template('table.html', students=students_cleaned, programs=programs_cleaned)

# --- CREATE Student ---
@app.route('/students', methods=['POST'])
def create_student():
    data = request.get_json()
    if not data or not data.get("first_name") or not data.get("last_name") or not data.get("email"):
        return jsonify({"error": "first_name, last_name, and email are required"}), 400

    # Generate new student ID
    last_student = mongo.db.student.find_one({"_id": {"$regex": "^1990-.*-MN-0$"}}, sort=[("_id", -1)])
    next_seq_int = 1
    if last_student:
        try:
            last_seq_int = int(last_student["_id"].split('-')[1])
            next_seq_int = last_seq_int + 1
        except:
            pass
    new_id = f"1990-{str(next_seq_int).zfill(5)}-MN-0"

    # Resolve program name
    program_name = None
    if data.get("program_id"):
        try:
            program = mongo.db.program.find_one({"_id": ObjectId(data["program_id"])})
            if program:
                program_name = program.get("program_name")
        except:
            pass

    student = {
        "_id": new_id,
        "first_name": data["first_name"],
        "last_name": data["last_name"],
        "middle_name": data.get("middle_name", ""),
        "birth_date": datetime.strptime(data["birth_date"], "%Y-%m-%d") if data.get("birth_date") else None,
        "email": data["email"],
        "student_type": data.get("student_type", "regular"),
        "program_id": ObjectId(data["program_id"]) if data.get("program_id") else None,
        "program_name": program_name,
        "active": data.get("active", True)
    }

    try:
        mongo.db.student.insert_one(student)
        return jsonify({"message": "Student created", "student": clean_student(student)}), 201
    except DuplicateKeyError:
        return jsonify({"error": "A student with this email already exists."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- READ All Students ---
@app.route('/students', methods=['GET'])
def get_all_students():
    students = mongo.db.student.find()
    cleaned = []
    for s in students:
        s = clean_student(s)
        s = resolve_program_name(s)
        cleaned.append(s)
    return jsonify(cleaned)

# --- READ Single Student ---
@app.route('/student/<string:student_id>', methods=['GET'])
def get_student(student_id):
    student = mongo.db.student.find_one({"_id": student_id})
    if not student:
        return jsonify({"error": "Student not found"}), 404
    student = clean_student(student)
    student = resolve_program_name(student)
    return jsonify(student)

# --- UPDATE Student ---
@app.route('/student/<string:student_id>', methods=['PUT'])
def update_student(student_id):
    data = request.get_json()
    update_data = {}

    for key in ["first_name", "last_name", "middle_name", "email", "student_type", "active"]:
        if key in data:
            update_data[key] = data[key]

    # Program change
    if "program_id" in data:
        try:
            update_data["program_id"] = ObjectId(data["program_id"])
            program = mongo.db.program.find_one({"_id": ObjectId(data["program_id"])})
            update_data["program_name"] = program["program_name"] if program else None
        except:
            update_data["program_id"] = None
            update_data["program_name"] = None

    if "birth_date" in data:
        try:
            update_data["birth_date"] = datetime.strptime(data["birth_date"], "%Y-%m-%d")
        except:
            update_data["birth_date"] = None

    result = mongo.db.student.update_one({"_id": student_id}, {"$set": update_data})
    if result.matched_count == 0:
        return jsonify({"error": "Student not found"}), 404

    student = mongo.db.student.find_one({"_id": student_id})
    student = clean_student(student)
    student = resolve_program_name(student)
    return jsonify({"message": "Student updated", "student": student})

# --- DELETE Student ---
@app.route('/student/<string:student_id>', methods=['DELETE'])
def delete_student(student_id):
    result = mongo.db.student.delete_one({"_id": student_id})
    if result.deleted_count == 0:
        return jsonify({"error": "Student not found"}), 404
    return jsonify({"message": "Student deleted"})

if __name__ == "__main__":
    app.run(debug=True)
