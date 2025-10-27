from flask import Flask, render_template, jsonify
from flask_pymongo import PyMongo
from bson.json_util import dumps # A special tool to handle Mongo's 'ObjectId'
from bson.objectid import ObjectId # Imports ObjectId

# 1. Initialize the Flask App
app = Flask(__name__)

# 2. Configure the database connection 
app.config["MONGO_URI"] = "mongodb+srv://haromedb:P8iZzZZfx9WviOBb@harodb.gtgicdm.mongodb.net/DSI-ERD-SIS?retryWrites=true&w=majority"

# 3. Initialize PyMongo
mongo = PyMongo(app)

# 4. Create your first API route 
@app.route("/student/<string:student_id>")
def get_student(student_id):
    try:
        # 5. This is the "R" (Read) in CRUD!
        # It finds one document in the 'student' collection
        # where the '_id' matches the one from the URL.
        student = mongo.db.student.find_one_or_404({"_id": student_id})
        
        # 6. Convert the BSON (Mongo data) to JSON (web data)
        #    The 'dumps' function handles the special { "$date": ... }
        #    and { "$oid": ... } formats for you.
        return dumps(student)
        
    except Exception as e:
        return {"error": str(e)}, 404
    
@app.route("/students")
def get_all_students():
    try:
        # 1. Find ALL documents in the student collection
        all_students = mongo.db.student.find() 
        
        # 2. Dump them into JSON
        return dumps(all_students)
        
    except Exception as e:
        return {"error": str(e)}, 500

# A simple route for testing
@app.route('/')
def index():
    return render_template('index.html')

# This runs the app when you execute the file
if __name__ == "__main__":
    app.run(debug=True)