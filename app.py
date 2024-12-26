from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
CORS(app)  # To enable Cross-Origin Resource Sharing

# Task model definition
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    entity_name = db.Column(db.String(100), nullable=False)
    task_type = db.Column(db.String(50), nullable=False)
    time_of_task = db.Column(db.String(20), nullable=False)
    contact_person = db.Column(db.String(100), nullable=False)
    note = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(10), default='open')  # Default status is 'open'

# Create the database within an app context
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return jsonify({"messages": "Welcome to the Task Management API!"})

# API Route to get all tasks
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([{
        'id': task.id,
        'date_created': task.date_created,
        'entity_name': task.entity_name,
        'task_type': task.task_type,
        'time_of_task': task.time_of_task,
        'contact_person': task.contact_person,
        'note': task.note,
        'status': task.status
    } for task in tasks])

# API Route to create a new task
@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.json
    new_task = Task(
        entity_name=data['entity_name'],
        task_type=data['task_type'],
        time_of_task=data['time_of_task'],
        contact_person=data['contact_person'],
        note=data.get('note'),
        status=data.get('status', 'open')  # Default status is 'open'
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"message": "Task created successfully!"}), 201

# API Route to update a task
@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.json
    task.entity_name = data.get('entity_name', task.entity_name)
    task.task_type = data.get('task_type', task.task_type)
    task.time_of_task = data.get('time_of_task', task.time_of_task)
    task.contact_person = data.get('contact_person', task.contact_person)
    task.note = data.get('note', task.note)
    task.status = data.get('status', task.status)
    db.session.commit()
    return jsonify({"message": "Task updated successfully!"})

# API Route to delete a task
@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted successfully!"})

# API Route to filter and sort tasks
@app.route('/api/tasks/filter', methods=['GET'])
def filter_tasks():
    filters = {}
    if 'contact_person' in request.args:
        filters['contact_person'] = request.args['contact_person']
    if 'status' in request.args:
        filters['status'] = request.args['status']
    if 'task_type' in request.args:
        filters['task_type'] = request.args['task_type']
    
    tasks = Task.query.filter_by(**filters).all()
    
    return jsonify([{
        'id': task.id,
        'date_created': task.date_created,
        'entity_name': task.entity_name,
        'task_type': task.task_type,
        'time_of_task': task.time_of_task,
        'contact_person': task.contact_person,
        'note': task.note,
        'status': task.status
    } for task in tasks])

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', 5000, app)
