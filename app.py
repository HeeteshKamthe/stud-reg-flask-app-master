# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import db, Student
from config import Config
import re
import traceback

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Client-side validation is handled in HTML (JS), server-side here.

def validate_form(name, email, phone, course, address):
    """Server-side validation"""
    if not name or not email or not phone or not course or not address:
        return False, "All fields are required."
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False, "Invalid email format."
    if not re.match(r"^\+?[1-9]?\d{9,15}$", phone):
        return False, "Invalid phone number (e.g., +1234567890)."
    if len(name) < 2:
        return False, "Name must be at least 2 characters."
    return True, "Valid"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    course = request.form['course']
    address = request.form['address']

    is_valid, message = validate_form(name, email, phone, course, address)
    if not is_valid:
        flash(message, 'error')
        return redirect(url_for('index'))

    # Check if email already exists
    existing = Student.query.filter_by(email=email).first()
    if existing:
        flash("Email already registered.", 'error')
        return redirect(url_for('index'))

    # Store in DB
    student = Student(name=name, email=email, phone=phone, course=course, address=address)
    db.session.add(student)
    db.session.commit()

    flash("Student registered successfully!", 'success')
    return redirect(url_for('index'))

@app.route('/view')
def view_students():
    students = Student.query.all()
    return render_template('view.html', students=students)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    student = Student.query.get_or_404(id)
    if request.method == 'POST':
        student.name = request.form['name']
        student.email = request.form['email']
        student.phone = request.form['phone']
        student.course = request.form['course']
        student.address = request.form['address']
        db.session.commit()
        flash("Student updated successfully!", 'success')
        return redirect(url_for('view_students'))
    return render_template('edit.html', student=student)

@app.route('/delete/<int:id>')
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash("Student deleted successfully!", 'success')
    return redirect(url_for('view_students'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creates tables if they don't exist
    app.run(host='0.0.0.0', port=5000, debug=True)
