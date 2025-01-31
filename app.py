import os
from flask import Flask, render_template, jsonify, request
import requests
from requests.exceptions import RequestException
from config import Config
import json  # Add this import for pretty printing

app = Flask(__name__)
app.config.from_object(Config)

def get_headers():
    return {
        'Authorization': f'Token {Config.s2_tocken}',
        'Content-Type': 'application/json'
    }

@app.route('/')
def index():
    try:
        response = requests.get(
            f"{app.config['S2_API_BASE_URL']}/show/?stage=Active",
            headers=get_headers()
        )
        shows = []
        if response.status_code == 200:
            all_shows = response.json()
            # Filter and simplify show data
            shows = [
                {
                    'show_name': show.get('show_name', ''),
                    'id': show.get('id', ''),
                    'status': show.get('status', ''),
                    'stage': show.get('stage', '')
                }
                for show in all_shows
                if show.get('stage') == 'Active'
            ]
            shows = sorted(shows, key=lambda x: x['show_name'])
        return render_template('index.html', shows=shows)
    except Exception as e:
        return render_template('index.html', error=str(e))

@app.route('/show/<int:show_id>/tasks')
def get_show_tasks(show_id):
    try:
        response = requests.get(
            f"{app.config['S2_API_BASE_URL']}/object_tree/?show_id={show_id}",
            headers=get_headers()
        )
        if response.status_code == 200:
            tasks = response.json()
            # Pretty print the tasks dictionary
            print(f"\n=== TASKS API RESPONSE FOR SHOW {show_id} ===")
            print(json.dumps(tasks, indent=2))
            print("========================\n")
            return jsonify(tasks)
        return jsonify({"error": "Failed to fetch tasks"}), 400
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
