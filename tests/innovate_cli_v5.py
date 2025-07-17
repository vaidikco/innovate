import os
import sys
import time
import json
import uuid
import shutil
import random
import subprocess
from datetime import datetime
from google import genai
from dotenv import load_dotenv

# Load API key
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# Logging setup
def log(msg):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open("agent.log", "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {msg}\n")
    print(f"{timestamp} {msg}")

# Generate a project ID and directory
def create_project_dir():
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = uuid.uuid4().hex[:5]
    project_name = f"project_{now}_{slug}"
    full_path = os.path.join("projects", project_name)
    os.makedirs(full_path, exist_ok=True)
    return full_path

# Get user prompt
def get_user_prompt():
    return input("\nWhat do you want to build today?\n> ").strip()

# Ask for generation mode
def select_mode():
    print(
        "\n=== Select Mode ===\n"
        "[1] ⚡ Quick Mode (faster, simpler, ~30 sec thinking)\n"
        "[2] 🧠 Deep Mode (slower, better quality)\n"
    )
    while True:
        choice = input("Choose [1 or 2]: ").strip()
        if choice == "1":
            return "quick"
        elif choice == "2":
            return "deep"
        else:
            print("Invalid input. Please type 1 or 2.")

# Ask for output type
def select_output_type():
    print(
        "\n=== Output Type ===\n"
        "[1] App / CLI / Website Project\n"
        "[2] Webpage (single file beautiful HTML)\n"
    )
    while True:
        choice = input("Choose [1 or 2]: ").strip()
        if choice == "1":
            return "app"
        elif choice == "2":
            return "webpage"
        else:
            print("Invalid input. Please type 1 or 2.")

# Compose prompt with system instructions
def generate_steps(prompt, mode="quick", output_type="app"):
    sys_prompt = (
        "You are Innovate CLI, a precise and minimal code generation agent built by vaidik.co.\n"
        "From the user’s request, break the project into sequential executable steps using ONLY the following format:\n\n"
        "[CMD] shell command\n"
        "[CD] path/to/directory\n"
        "[CREATE] path/to/file.ext:\n```\nfile contents\n```\n"
        "[APPEND] path/to/file.ext:\n```\nappended content\n```\n\n"
        "DO NOT explain anything. DO NOT add markdown. DO NOT return anything outside the above formats.\n"
    )

    if output_type == "webpage":
        sys_prompt += (
            "\n\nSTRICT RULES FOR WEBPAGE MODE:\n"
            "- Only output ONE HTML file. No external CSS or JS.\n"
            "- The file should be named `index.html`.\n"
            "- Use TailwindCSS via CDN.\n"
            "- Use the Inter font via Google Fonts.\n"
            "- Embed all CSS in <style> blocks if needed.\n"
            "- Generate a modern, beautiful webpage with full layout (nav, hero, sections, footer).\n"
            "- It must be around 600+ lines (repeat blocks/dummy content if needed).\n"
            "- No `style.css`, `script.js`, or asset folders.\n"
            "- Again: ONE `index.html` file only."
        )

    if mode == "deep":
        sys_prompt += "\n\nBe structured, comprehensive, elegant, and follow best coding practices."

    full_prompt = f"{sys_prompt}\n\nUser prompt: {prompt}"

    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=full_prompt
    )
    return response.text

# Execute generated steps
def execute_steps(response, root_dir):
    current_dir = root_dir
    os.makedirs(current_dir, exist_ok=True)
    os.chdir(current_dir)

    blocks = response.split("\n--- ")
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        if block.startswith("Step"):
            _, rest = block.split("] ", 1)
            if rest.startswith("CMD"):
                cmd = rest[4:].strip()
                log(f"Running command: {cmd}")
                subprocess.run(cmd, shell=True)
            elif rest.startswith("CD"):
                path = rest[3:].strip()
                new_dir = os.path.join(current_dir, path)
                os.makedirs(new_dir, exist_ok=True)
                current_dir = new_dir
                os.chdir(current_dir)
                log(f"Changed working directory to {current_dir}")
            elif rest.startswith("CREATE"):
                path, content = parse_file_block(rest[7:])
                full_path = os.path.join(current_dir, path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)
                log(f"Created file: {path}")
            elif rest.startswith("APPEND"):
                path, content = parse_file_block(rest[7:])
                full_path = os.path.join(current_dir, path)
                with open(full_path, "a", encoding="utf-8") as f:
                    f.write(content)
                log(f"Appended to file: {path}")

# Parse code blocks from [CREATE]/[APPEND]
def parse_file_block(block):
    parts = block.strip().split(":\n```", 1)
    path = parts[0].strip()
    content = parts[1].strip().removesuffix("```").strip()
    return path, content

# Compress final output folder
def zip_project(path):
    shutil.make_archive(path, 'zip', path)
    log(f"Project zipped: {path}.zip")

# === Main flow ===
if __name__ == "__main__":
    print("███ Innovate CLI v5 — Powered by Gemini 2.5 Pro ███")
    mode = select_mode()
    output_type = select_output_type()
    user_prompt = get_user_prompt()
    log(f"Prompt: {user_prompt} | Mode: {mode} | Type: {output_type}")

    project_dir = create_project_dir()
    log(f"Project directory created at: {project_dir}")

    response_text = generate_steps(user_prompt, mode=mode, output_type=output_type)
    with open(os.path.join(project_dir, "generation.txt"), "w", encoding="utf-8") as f:
        f.write(response_text)

    execute_steps(response_text, project_dir)
    zip_project(project_dir)

    print(f"\n✅ Project generated at: {project_dir}")
    print(f"📦 Zipped version: {project_dir}.zip")
