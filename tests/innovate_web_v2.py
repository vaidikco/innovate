import os
import subprocess
import zipfile
import random
import string
import re
import dotenv
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session, jsonify
from google import genai

# ========== Config ==========

dotenv.load_dotenv()
key = os.getenv("API-KEY")

# Gemini client setup (new style)
client = genai.Client(api_key="AIzaSyBraenCIuVM6jRPCSCQkWylfnFnu6cqK8I")
model_name = "gemini-2.5-pro"

app = Flask(__name__)
app.secret_key = "secret-key"
LOG_PATH = "agent.log"

# ========== Helpers ==========

def log(msg):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    line = f"{timestamp} {msg}\n"
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line)

langs = {"python", "html", "js", "javascript", "css", "ts", "typescript", "bash", "sh", "json"}

def clean_block(block):
    lines = block.strip().splitlines()
    cleaned = "\n".join(lines[1:]) if lines and lines[0].strip().lower() in langs else block.strip()
    return cleaned + "\n\n# Powered by Innovate CLI, a product of vaidik.co\n"

def create_project_folder():
    os.makedirs("projects", exist_ok=True)
    suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
    rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    folder = os.path.abspath(f"projects/project_{suffix}_{rand}")
    os.makedirs(folder, exist_ok=True)
    return folder

def generate_steps(prompt):
    sys_prompt = (
        "You're a code execution planner. From the user's request, generate a clean list of executable steps.\n"
        "Use ONLY this format:\n"
        "[CMD] shell command\n"
        "[CD] target_directory\n"
        "[CREATE] path/to/file.ext:\n```\nfile contents\n```\n"
        "[APPEND] path/to/file.ext:\n```\nappended content\n```\n"
        "No explanations. No markdown headings. Only actionable steps."
    )
    full_prompt = f"{sys_prompt}\nUser prompt: {prompt}"

    response = client.models.generate_content(
        model=model_name,
        contents=full_prompt,
    )
    return response.text

def parse_steps(text):
    pattern = r"\[(CMD|CD|CREATE|APPEND|EDIT)\](.*?)\n(?:```(.*?)```)?"
    return re.findall(pattern, text, re.DOTALL)

def execute_steps(steps, folder):
    current_dir = folder
    for i, (step_type, content, block) in enumerate(steps, 1):
        log(f"\n--- Step {i} [{step_type}] ---\n{content.strip()}")
        try:
            if step_type == "CMD":
                subprocess.run(content.strip(), shell=True, cwd=current_dir)
            elif step_type == "CD":
                new_dir = os.path.join(current_dir, content.strip())
                os.makedirs(new_dir, exist_ok=True)
                current_dir = new_dir
            elif step_type == "CREATE":
                path = os.path.join(current_dir, content.strip().rstrip(":"))
                os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(clean_block(block))
            elif step_type == "APPEND":
                path = os.path.join(current_dir, content.strip().rstrip(":"))
                with open(path, "a", encoding="utf-8") as f:
                    f.write("\n" + clean_block(block))
        except Exception as e:
            log(f"[ERROR] Step {i} failed: {e}")

# ========== Routes ==========

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        prompt = request.form.get("prompt", "").strip()
        if not prompt:
            flash("Prompt cannot be empty!", "danger")
            return redirect(url_for("index"))

        folder = create_project_folder()
        session["project_folder"] = folder
        session["zip_path"] = folder + ".zip"

        with open(LOG_PATH, "w", encoding="utf-8") as f:
            f.write("")  # reset log

        log(f"🔧 Prompt: {prompt}")
        raw_output = generate_steps(prompt)
        log("📋 Generated Raw Output:\n" + raw_output)
        steps = parse_steps(raw_output)
        execute_steps(steps, folder)

        # zip project
        zip_path = session["zip_path"]
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, os.path.dirname(folder))
                    zipf.write(full_path, rel_path)

        return redirect(url_for("index"))

    return render_template("index.html")

@app.route("/logs")
def logs():
    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            return jsonify(f.read().splitlines())
    except:
        return jsonify([])

@app.route("/download")
def download():
    zip_path = session.get("zip_path")
    if zip_path and os.path.exists(zip_path):
        return send_file(zip_path, as_attachment=True)
    else:
        flash("⚠️ Zip file not found!", "danger")
        return redirect(url_for("index"))

# ========== Run ==========

if __name__ == "__main__":
    app.run(debug=True, port=5200)
