from innovate import Innovate
from flask import Flask, request, render_template, redirect, url_for, flash, session, send_file
import os, zipfile

app = Flask(__name__)
app.secret_key = "your-secret-key"

engine = Innovate(api_key="AIzaSyBraenCIuVM6jRPCSCQkWylfnFnu6cqK8I")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        prompt = request.form.get("prompt", "").strip()
        if not prompt:
            flash("Prompt cannot be empty.", "danger")
            return redirect(url_for("index"))

        folder = engine.generate(prompt)

        # Create ZIP
        zip_path = folder + ".zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, os.path.dirname(folder))
                    zipf.write(full_path, rel_path)

        session["zip_path"] = zip_path
        flash("✅ Project created! Download below.", "success")
        return redirect(url_for("index"))

    return render_template("index.html")

@app.route("/download")
def download():
    zip_path = session.get("zip_path")
    if zip_path and os.path.exists(zip_path):
        return send_file(zip_path, as_attachment=True)
    flash("⚠️ No project zip found!", "danger")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, port=5200)
