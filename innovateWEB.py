from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify, render_template, send_file
load_dotenv()
KEY = os.getenv("GEMINI_API_KEY")
from src.innovate import Innovate, getDIR
WI = Innovate(KEY)
from flask import Flask, render_template, request, jsonify
import time

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

import shutil
import os

@app.route("/process", methods=["POST"])
def process():
    try:
        data = request.json.get("user_input")
        app.logger.info("Received input: %s", data)

        # Generate project (assumes WI.generate is synchronous)
        WI.generate(data + " Also make a explanation.md, explaining the entire project..", "website")
        project_dir = getDIR()
        app.logger.info("Project directory: %s", project_dir)

        # Make sure project_dir actually exists
        if not project_dir or not os.path.exists(project_dir):
            raise FileNotFoundError(f"Project dir not found: {project_dir}")

        # Build zip
        zip_path = f"{project_dir}.zip"
        # If an old zip exists, remove it
        if os.path.exists(zip_path):
            os.remove(zip_path)

        # shutil.make_archive takes base_name without .zip
        # If project_dir contains backslashes, that's fine — shutil will create zip next to it.
        shutil.make_archive(project_dir, 'zip', project_dir)
        app.logger.info("Created zip at: %s", zip_path)

        # Return the zip as attachment
        # download_name works on modern Flask; if older version, use attachment_filename
        return send_file(
            zip_path,
            as_attachment=True,
            download_name=os.path.basename(zip_path),
            mimetype='application/zip'
        )
    except Exception as e:
        # Log with traceback for CLI debugging
        app.logger.exception("Error in /process")
        # Return plain JSON error and 500 so the frontend can show the server error text
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5289, use_reloader=False)