import os
import json
from flask import Flask, jsonify, request

app = Flask(__name__)

# Path to the JSON file where tasks will be saved
TASKS_FILE = 'tasks.json'

# A function to load tasks from the JSON file
def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r') as file:
            return json.load(file)
    return []

# A function to save tasks to the JSON file
def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as file:
        json.dump(tasks, file)

# Load tasks from the file when the app starts
tasks = load_tasks()

# Route to get all tasks
@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(tasks)

# Route to add a new task
@app.route('/tasks', methods=['POST'])
def add_task():
    data = request.get_json()

    # Log the received data
    app.logger.debug(f"Received task data: {data}")

    # Check if the name is missing and log it
    if not data.get('name'):
        app.logger.debug("Task name is missing!")
        return jsonify({'error': 'Task name is required!'}), 400

    task = {
        'name': data.get('name'),
        'description': data.get('description', ''),
        'due_date': data.get('due_date'),
        'priority': data.get('priority', 'Medium'),
        'status': data.get('status', 'Not Started')
    }

    # Append the task to the list and save the tasks to the file
    tasks.append(task)
    save_tasks(tasks)
    
    app.logger.debug(f"Task added: {task}")
    return jsonify(task), 201

# Route to delete a task by its name
@app.route('/tasks/<string:task_name>', methods=['DELETE'])
def delete_task(task_name):
    # Search for the task by name
    task_to_delete = next((task for task in tasks if task['name'] == task_name), None)

    if task_to_delete:
        tasks.remove(task_to_delete)
        save_tasks(tasks)  # Save tasks after deletion
        return jsonify({'message': f"Task '{task_name}' deleted successfully."}), 200
    else:
        return jsonify({'error': 'Task not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
