from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add current directory to path to import your FileOrganizer
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import your existing FileOrganizer class
from data_hygiene import FileOrganizer

app = Flask(__name__)
CORS(app)

# Global organizer instance
organizer = None


@app.route('/scan', methods=['POST'])
def scan_directory():
    """Scan directory using your existing FileOrganizer"""
    global organizer

    data = request.json
    directory = data.get('directory')

    if not directory or not os.path.exists(directory):
        return jsonify({"error": "Invalid directory"}), 400

    try:
        # Use your existing FileOrganizer
        organizer = FileOrganizer(directory, [], [], [])
        files, folders = organizer.scandir()

        return jsonify({
            "message": "Scan complete",
            "files": len(files),
            "folders": len(folders)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/apply_rules', methods=['POST'])
def apply_rules():
    """Apply rules using your existing FileOrganizer methods"""
    global organizer

    if not organizer:
        return jsonify({"error": "No directory scanned"}), 400

    data = request.json
    rules = data.get('rules', {})

    try:
        results = []

        # Use your existing methods
        if rules.get('naming'):
            organizer.namefile()
            results.append("Applied naming conventions")

        if rules.get('organize'):
            organizer.sortfilebytype(organizer.path)
            results.append("Organized files by type")

        if rules.get('group_similar'):
            organizer.sortfilebyname(organizer.path)
            results.append("Grouped similar files")

        if rules.get('detect_duplicates'):
            duplicates = organizer.detectduplicates()
            results.append(f"Found {len(duplicates)} duplicate groups")

        if rules.get('cleanup'):
            organizer.deleteemptyfolders()
            organizer.deleteemptyfiles()
            results.append("Cleaned up empty files/folders")

        return jsonify({"results": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/test', methods=['GET'])
def test():
    return jsonify({"status": "Server working", "organizer": organizer is not None})

if __name__ == '__main__':
    print("Starting simple HTTP server for FileOrganizer...")
    print("Run your Java frontend to connect")
    app.run(host='localhost', port=5000, debug=False)
