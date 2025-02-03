from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app, origins=["*"]) # contoh

API_KEY = os.environ.get("API_KEY")

def verify_api_key():
    key = request.headers.get("X-API-KEY")
    if not key or key != API_KEY:
        return jsonify({"error": "Unauthorized", "message": "Invalid or missing API Key"}), 401
    return None

@app.route('/')
def index():
    auth = verify_api_key()
    if auth:
        return auth
    return jsonify({"message": "Hello ab, welcome back!"})

@app.route('/project', methods=['POST'])
def add_project():
    auth = verify_api_key()
    if auth:
        return auth

    conn = sqlite3.connect('project.db')
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO projects (title, categories, description) VALUES (?, ?, ?)",
                       (request.json.get("title"), request.json.get("categories"), request.json.get("description")))
        conn.commit()
        new_id = cursor.lastrowid  # Mendapatkan ID yang baru di-insert
        new_project = {
            "id": new_id,
            "title": request.json.get("title"),
            "categories": request.json.get("categories"),
            "description": request.json.get("description")
        }
        return jsonify({"message": "Project successfully added.", "project": new_project}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Failed to add project", "message": str(e)}), 500
    finally:
        conn.close()


@app.route('/project/<int:project_id>', methods=['GET'])
def get_project_by_id(project_id):
    conn = sqlite3.connect('project.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    project = cursor.fetchone()
    conn.close()
    if project:
        # Mengubah tuple menjadi dictionary
        project_dict = {
            "id": project[0],
            "title": project[1],
            "categories": project[2],
            "description": project[3]
        }
        return jsonify(project_dict)
    return jsonify({"error": "Project not found"}), 404


@app.route('/project', methods=['GET'])
def get_projects():
    auth = verify_api_key()
    if auth:
        return auth

    conn = sqlite3.connect('project.db')
    cursor = conn.cursor()

    category = request.args.get('category')

    if category:
        cursor.execute("SELECT * FROM projects WHERE categories = ?", (category,))
    else:
        cursor.execute("SELECT * FROM projects")

    projects = cursor.fetchall()
    conn.close()

    project_list = []
    for project in projects:
        project_dict = {
            "id": project[0],
            "title": project[1],
            "categories": project[2],
            "description": project[3]
        }
        project_list.append(project_dict)

    if category:
        return jsonify({
            "message": f"Projects in category '{category}'.",
            "projects": project_list
        }), 200
    else:
        return jsonify({
            "message": "All projects.",
            "projects": project_list
        }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not Found", "message": "The requested resource could not be found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred"}), 500

if __name__ == '__main__':
    app.run()
