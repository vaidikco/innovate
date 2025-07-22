import os
import subprocess
import re
import dotenv
import random
import fade
import string
from datetime import datetime
from google import genai as gemini_pro

# ==== Load API key from .env ====
dotenv.load_dotenv()
key = os.getenv("GEMINI_API_KEY")

# ==== Gemini 2.5 Pro Client Setup ====
try:
    key = os.getenv("GEMINI_API_KEY")
    client = gemini_pro.Client(api_key=key)
except Exception:
    # fallback to default key if .env or env var fails
    client = gemini_pro.Client(api_key="AIzaSyBraenCIuVM6jRPCSCQkWylfnFnu6cqK8I")

# ==== Logging ====
LOG_PATH = "agent.log"
def log(msg):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {msg}\n")
    print(f"{timestamp} {msg}")

# ==== Unique Project Folder Creator ====
def create_project_folder():
    os.makedirs("projects", exist_ok=True)
    suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
    rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    folder = f"projects/project_{suffix}_{rand}"
    os.makedirs(folder, exist_ok=True)
    return folder

# ==== Step Generator using Gemini 2.5 Pro ====
def generate_steps(prompt):
    sys_prompt = (
        "You're a code execution planner known as Innovate CLI made by vaidik.co . From the user's request, generate a clean list of executable steps from the installation and the running procedure of the prompt given.\n"
        "Use ONLY this format:\n"
        "[CMD] shell command\n"
        "[CD] target_directory\n"
        "[CREATE] path/to/file.ext:\n```\nfile contents\n```\n"
        "[APPEND] path/to/file.ext:\n```\nappended content\n```\n"
        "No explanations. No markdown headings. Only actionable steps."
    )
    full_prompt = f"{sys_prompt}\nUser prompt: {prompt}"
    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=full_prompt
    )
    return response.text

# ==== Step Parser ====
def parse_steps(text):
    pattern = r"\[(CMD|CD|CREATE|APPEND|EDIT)\](.*?)\n(?:```(.*?)```)?"
    return re.findall(pattern, text, re.DOTALL)

# ==== Code Block Cleaner ====
def clean_code_block(block):
    lines = block.strip().splitlines()
    if lines and lines[0].strip().lower() in {
        "python", "html", "javascript", "js", "ts", "typescript", "bash", "sh", "json", "css"
    }:
        return "\n".join(lines[1:]) + "\n\n# Powered by Innovate CLI, a product of vaidik.co"
    return block.strip() + "\n\n# Powered by Innovate CLI, a product of vaidik.co"

# ==== Step Executor ====
def execute_steps(steps):
    for i, (step_type, content, block) in enumerate(steps, 1):
        log(f"\n--- Step {i} [{step_type}] ---\n{content.strip()}")
        try:
            if step_type == "CMD":
                cmd = content.strip()
                log(f"Running command: {cmd}")
                subprocess.run(cmd, shell=True)
            elif step_type == "CD":
                new_dir = content.strip()
                os.makedirs(new_dir, exist_ok=True)
                os.chdir(new_dir)
                log(f"Changed working directory to {os.getcwd()}")
            elif step_type == "CREATE":
                file_path = content.strip().rstrip(":")
                os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(clean_code_block(block) + "\n")
                log(f"Created file: {file_path}")
            elif step_type == "APPEND":
                file_path = content.strip().rstrip(":")
                with open(file_path, "a", encoding="utf-8") as f:
                    f.write("\n" + clean_code_block(block) + "\n")
                log(f"Appended to file: {file_path}")
            else:
                log(f"[WARN] Unsupported step type: {step_type}")
        except Exception as e:
            log(f"[ERROR] Step {i} failed: {e}")

# ==== Main Runner ====
if __name__ == "__main__":
    banner = """
██╗      ██╗███╗   ██╗███╗   ██╗ ██████╗ ██╗   ██╗ █████╗ ████████╗███████╗
╚██╗     ██║████╗  ██║████╗  ██║██╔═══██╗██║   ██║██╔══██╗╚══██╔══╝██╔════╝
 ╚██╗    ██║██╔██╗ ██║██╔██╗ ██║██║   ██║██║   ██║███████║   ██║   █████╗  
 ██╔╝    ██║██║╚██╗██║██║╚██╗██║██║   ██║╚██╗ ██╔╝██╔══██║   ██║   ██╔══╝  
██╔╝     ██║██║ ╚████║██║ ╚████║╚██████╔╝ ╚████╔╝ ██║  ██║   ██║   ███████╗
╚═╝      ╚═╝╚═╝  ╚═══╝╚═╝  ╚═══╝ ╚═════╝   ╚═══╝  ╚═╝  ╚═╝   ╚═╝   ╚══════╝
                                                                            
 ██████╗██╗     ██╗                                                        
██╔════╝██║     ██║                                                        
██║     ██║     ██║                                                        
██║     ██║     ██║                                                        
╚██████╗███████╗██║                                                        
 ╚═════╝╚══════╝╚═╝              """
    print(fade.pinkred(banner))
    print("Welcome to Innovate CLI 0.5!")
    print("> The tool which helps imaginations turn into a reality. One of the best coding tools that you can use.")
    print("> Official documentation available at innovate.vaidik.co/docs")
    user_prompt = input("\nWhat do you want to build or do?\n> ").strip()
    log(f"🔧 Prompt: {user_prompt}")

    project_folder = create_project_folder()
    os.chdir(project_folder)
    log(f"📁 Working in project folder: {project_folder}")

    response_text = generate_steps(user_prompt)
    log("📋 Generated Raw Output:\n" + response_text)

    steps = parse_steps(response_text)
    execute_steps(steps)