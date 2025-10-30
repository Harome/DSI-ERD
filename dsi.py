from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
from pymongo.errors import DuplicateKeyError

# --- Initialize Flask ---
app = Flask(__name__)

# --- MongoDB Configuration ---
app.config["MONGO_URI"] = "mongodb+srv://haromedb:P8iZzZZfx9WviOBb@harodb.gtgicdm.mongodb.net/DSI-ERD-SIS?retryWrites=true&w=majority"
mongo = PyMongo(app)

# --- Helper to clean student data for JSON ---
def clean_student(student):
    student["_id"] = str(student["_id"])
    if "birth_date" in student and isinstance(student["birth_date"], datetime):
        student["birth_date"] = student["birth_date"].strftime("%Y-%m-%d")
    
    # --- Check if program_id is not None before str() ---
    if "program_id" in student and student["program_id"]:
        student["program_id"] = str(student["program_id"])
    return student

# --- Clean program data for the dropdown ---
def clean_program(program):
    program["_id"] = str(program["_id"])
    return program

# --- Homepage / Table ---
@app.route('/')
def index():
    students_cursor = mongo.db.student.find()
    students_cleaned = [clean_student(s) for s in students_cursor]
    
    # --- Fetch and clean programs ---
    programs_cursor = mongo.db.program.find()
    programs_cleaned = [clean_program(p) for p in programs_cursor]

    # --- Pass 'programs' to the template ---
    return render_template('table.html', students=students_cleaned, programs=programs_cleaned)

# --- CREATE Student ---
@app.route('/students', methods=['POST'])
def create_student():
    data = request.get_json()
    if not data or not data.get("first_name") or not data.get("last_name") or not data.get("email"):
        return jsonify({"error": "first_name, last_name, and email are required"}), 400
    
    last_student = mongo.db.student.find_one(
        {"_id": {"$regex": "^1990-.*-MN-0$"}}, 
        sort=[("_id", -1)]
    )
    
    next_seq_int = 1
    
    if last_student:
        try:
            last_id_parts = last_student["_id"].split('-')
            last_seq_str = last_id_parts[1]
            next_seq_int = int(last_seq_str) + 1
        except (IndexError, ValueError, TypeError):
            pass 

    next_seq_str = str(next_seq_int).zfill(5)
    new_id = f"1990-{next_seq_str}-MN-0"

    student = {
        "_id": new_id,
        "first_name": data["first_name"],
        "last_name": data["last_name"],
        "middle_name": data.get("middle_name", ""),
        "birth_date": None,
        "email": data["email"],
        "student_type": data.get("student_type", "regular"),
        "program_id": ObjectId(data["program_id"]) if data.get("program_id") else None,
        "active": data.get("active", True)
    }

    # Convert birth_date to datetime if provided
    if data.get("birth_date"):
        try:
            student["birth_date"] = datetime.strptime(data["birth_date"], "%Y-%m-%d")
        except:
            student["birth_date"] = None

    try:
        # Try to insert the new student
        result = mongo.db.student.insert_one(student)
        student["_id"] = str(result.inserted_id)
        return jsonify({"message": "Student created", "student": clean_student(student)}), 201

    except DuplicateKeyError as e:
        # This code runs if the email is a duplicate
        return jsonify({"error": "A student with this email address already exists."}), 400
        
    except Exception as e:
        # This catches any other unexpected errors
        return jsonify({"error": str(e)}), 500

# --- READ All Students (API) ---
@app.route('/students', methods=['GET'])
def get_all_students():
    students = mongo.db.student.find()
    cleaned = [clean_student(s) for s in students]
    return jsonify(cleaned)

# --- READ Single Student ---
@app.route('/student/<string:student_id>', methods=['GET'])
def get_student(student_id):
    student = mongo.db.student.find_one({"_id": student_id})
    if not student:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(clean_student(student))

# --- UPDATE Student ---
@app.route('/student/<string:student_id>', methods=['PUT'])
def update_student(student_id):
    data = request.get_json()
    update_data = {}

    for key in ["first_name", "last_name", "middle_name", "email", "student_type", "active"]:
        if key in data:
            update_data[key] = data[key]

    # --- Convert program_id string back to ObjectId ---
    if "program_id" in data:
        try:
            # Convert the string ID from the form back to an ObjectId
            update_data["program_id"] = ObjectId(data["program_id"]) if data.get("program_id") else None
        except:
            update_data["program_id"] = None # Handle invalid ID string

    if "birth_date" in data:
        try:
            update_data["birth_date"] = datetime.strptime(data["birth_date"], "%Y-%m-%d")
        except:
            update_data["birth_date"] = None

    result = mongo.db.student.update_one({"_id": student_id}, {"$set": update_data})
    if result.matched_count == 0:
        return jsonify({"error": "Student not found"}), 404
    student = mongo.db.student.find_one({"_id": student_id})
    return jsonify({"message": "Student updated", "student": clean_student(student)})

# --- DELETE Student ---
@app.route('/student/<string:student_id>', methods=['DELETE'])
def delete_student(student_id):
    result = mongo.db.student.delete_one({"_id": student_id})
    if result.deleted_count == 0:
        return jsonify({"error": "Student not found"}), 404
    return jsonify({"message": "Student deleted"})


# --- Run Flask App ---
if __name__ == "__main__":
    app.run(debug=True)
