import os
import subprocess
import re
import dotenv
import random
import string
import sys
import time
import threading
import itertools
from datetime import datetime
from google import genai as gemini_pro
import fade
from colorama import Fore, Style, init as colorama_init

# Initialize colorama for colored output
colorama_init(autoreset=True)
dir = ""
# ------------------ Spinner Class ------------------
class Spinner:
    def __init__(self, text="Processing"):
        self.spinner = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
        self.running = False
        self.thread = None
        self.text = text

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._spin, daemon=True)
        self.thread.start()

    def _spin(self):
        while self.running:
            sys.stdout.write(f"\r{Fore.CYAN}{next(self.spinner)} {self.text}...{Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(0.1)

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        sys.stdout.write(f"\r{Fore.GREEN}✅ {self.text} complete!{Style.RESET_ALL}        \n")
        sys.stdout.flush()

    def think(self, seconds):
        """Show 'Thinking' with spinner for X seconds"""
        end_time = time.time() + seconds
        while time.time() < end_time:
            sys.stdout.write(f"\r{Fore.MAGENTA}{next(self.spinner)} Thinking...{Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write(f"\r{Fore.GREEN}💡 Done thinking!{Style.RESET_ALL}        \n")
        sys.stdout.flush()


class Innovate:
    LOG_PATH = "agent.log"

    def __init__(self, api_key=None):
        self.cwd = os.getcwd()
        dotenv.load_dotenv()

        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or "AIzaSyBraenCIuVM6jRPCSCQkWylfnFnu6cqK8I"
        self.client = gemini_pro.Client(api_key=self.api_key)

    def set_api_key(self, api_key: str):
        """Dynamically update the API key and Gemini client."""
        self.api_key = api_key
        self.client = gemini_pro.Client(api_key=self.api_key)
        self.log(f"[CONFIG] Gemini API key updated.")

    def log(self, msg, ts=True):
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        if ts == False:
            with open(self.LOG_PATH, "a", encoding="utf-8") as f:
                f.write(f"{timestamp} {msg}\n")
                print(f"{msg}")
        else:
             timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
             with open(self.LOG_PATH, "a", encoding="utf-8") as f:
                f.write(f"{timestamp} {msg}\n")
                print(f"[{timestamp}] {msg}")

    def clean_code_block(self, block):
        lines = block.strip().splitlines()
        if lines and lines[0].strip().lower() in {
            "python", "html", "javascript", "js", "ts", "typescript", "bash", "sh", "json", "css", "tsx", "jsx", "java", "c", "cpp", "csharp", "go", "ruby", "php", "swift", "kotlin", "sql"
        }:
            return "\n".join(lines[1:])
        return block.strip()

    def create_project_folder(self, prompt: str) -> str:
        print(f"{Fore.CYAN}Creating project folder...{Fore.RESET}")
        os.makedirs("projects", exist_ok=True)
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=(
                f"Generate ONLY a short, creative, unique project name (2–4 words max) "
                f"for this idea: {prompt}. "
                f"Do not include quotes, punctuation, or extra text."
            )
        )

        raw_name = (response.text or "project").strip()

        safe_name = re.sub(r"[^a-zA-Z0-9_-]", "-", raw_name).lower()
        safe_name = re.sub(r"-+", "-", safe_name).strip("-")

        # Add timestamp + random suffix to avoid collisions
        suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
        rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        folder_name = f"{safe_name}-{rand}"

        folder = os.path.join("projects", folder_name)
        os.makedirs(folder, exist_ok=True)

        credits_dir = os.path.join(folder, "innovate")
        os.makedirs(credits_dir, exist_ok=True)
        with open(os.path.join(credits_dir, "credits.txt"), "w", encoding="utf-8") as f:
            f.write("Innovate CLI, product of vaidik.co\n")
            f.write(f"Prompt: {prompt}")
            f.write("Version 0.7.1\n")
            f.write("Author: Vaidik K.\n")
            f.write("Website: innovate.vaidik.co\n")
            f.write("<<? end of file ?>>")

        return folder

    def get_mode_prompt(self, mode):
        """Return a different system prompt based on mode."""
        if mode.lower() == "website":
            return (
                """You're Innovate CLI (Website Mode) by vaidik.co.
From the user's request, generate executable steps to set up and run a complete WEBSITE project.
Focus on HTML, CSS, JavaScript, backend setup if needed, and deployment instructions.
The UI and UX **must be world-class**, visually stunning, highly polished, and responsive across all devices, using cutting-edge design trends, animations, typography, and layouts — **never compromise on design quality or detail**.
You may produce long, highly detailed code to achieve perfection in look and feel.
Prioritize a premium, modern, elegant, and professional style. Also default properties --ts (no tailwind vanilla css) --eslint --app --src-dir --import-alias '@/*'
Use ONLY this format:

"Use ONLY this format:\n"
                "[CMD] shell command\n"
                "[CD] target_directory\n"
                "[CREATE] path/to/file.ext:\n```\nfile contents\n```\n"
                "[APPEND] path/to/file.ext:\n```\nappended content\n```\n"
                "No explanations, no markdown headings, only actionable steps."

No explanations, no markdown headings, only actionable steps."


"""
            )
        elif mode.lower() == "app":
            return (
                "You're Innovate CLI (App Mode) by vaidik.co. "
                "From the user's request, generate executable steps to build a full APPLICATION project. "
                "Focus on app frameworks (e.g., React Native, Flutter, Python apps, etc.), "
                "installation, configuration, and execution.\n"
                "Use ONLY this format:\n"
                "[CMD] shell command\n"
                "[CD] target_directory\n"
                "[CREATE] path/to/file.ext:\n```\nfile contents\n```\n"
                "[APPEND] path/to/file.ext:\n```\nappended content\n```\n"
                "No explanations, no markdown headings, only actionable steps."
            )
        else:
            raise ValueError("Invalid mode. Please choose 'website' or 'app'.")

    def generate_steps(self, prompt, mode):
        sys_prompt = self.get_mode_prompt(mode)
        full_prompt = f"{sys_prompt}\nUser prompt: {prompt}"
        response = self.client.models.generate_content(
            model="gemini-2.5-pro",
            contents=full_prompt
        )
        return response.text

    def parse_steps(self, text):
        pattern = r"\[(CMD|CD|CREATE|APPEND|EDIT)\](.*?)\n(?:```(.*?)```)?"
        return re.findall(pattern, text, re.DOTALL)

    def execute_steps(self, steps):
        for i, (step_type, content, block) in enumerate(steps, 1):
            self.log(f"\n--- Step {i} [{step_type}] ---\n{content.strip()}")
            try:
                if step_type == "CMD":
                    cmd = content.strip()
                    self.log(f"Running command: {cmd}")
                    subprocess.run(cmd, shell=True)
                elif step_type == "CD":
                    new_dir = content.strip()
                    os.makedirs(new_dir, exist_ok=True)
                    os.chdir(new_dir)
                    self.log(f"Changed working directory to {os.getcwd()}")
                elif step_type == "CREATE":
                    file_path = content.strip().rstrip(":")
                    os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(self.clean_code_block(block) + "\n")
                    self.log(f"Created file: {file_path}")
                elif step_type == "APPEND":
                    file_path = content.strip().rstrip(":")
                    with open(file_path, "a", encoding="utf-8") as f:
                        f.write("\n" + self.clean_code_block(block) + "\n")
                    self.log(f"Appended to file: {file_path}")
                else:
                    self.log(f"[WARN] Unsupported step type: {step_type}")
            except Exception as e:
                self.log(f"[ERROR] Step {i} failed: {e}")

    def generate(self, prompt: str, mode: str):
        global dir
        folder = self.create_project_folder(prompt=prompt)
        os.chdir(folder)
        dir=folder
        self.log(f"{Fore.LIGHTYELLOW_EX}Building folder structure in {folder}...{Fore.RESET}", ts=False)

        # --- Thinking spinner with live seconds ---
        stop_event = threading.Event()

        def thinking_spinner():
            spinner_cycle = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
            start_time = time.time()
            while not stop_event.is_set():
                elapsed = int(time.time() - start_time)
                sys.stdout.write(f"\r{Fore.MAGENTA}{next(spinner_cycle)} Thinking for {elapsed} seconds...{Style.RESET_ALL}")
                sys.stdout.flush()
                time.sleep(0.1)

        spinner_thread = threading.Thread(target=thinking_spinner)
        spinner_thread.start()

        # --- Call Gemini ---
        raw_output = self.generate_steps(prompt, mode)

        # --- Stop thinking spinner ---
        stop_event.set()
        spinner_thread.join()
        sys.stdout.write(f"\r{Fore.GREEN}💡 Done thinking!{Style.RESET_ALL}        \n")
        sys.stdout.flush()

        # Log & parse
        self.log("📋 Generated Raw Output:\n" + raw_output)
        steps = self.parse_steps(raw_output)

        # --- Processing spinner while executing ---
        proc_spinner = Spinner("Processing")
        proc_spinner.start()
        self.execute_steps(steps)
        proc_spinner.stop()

        os.chdir(self.cwd)  # reset to original directory

    def ascii(self, configure=""):
        if configure == "":
            banner = r"""
            ▄█  ███▄▄▄▄   ███▄▄▄▄    ▄██████▄   ▄█    █▄     ▄████████     ███        ▄████████ 
        ███  ███▀▀▀██▄ ███▀▀▀██▄ ███    ███ ███    ███   ███    ███ ▀█████████▄   ███    ███ 
        ███▌ ███   ███ ███   ███ ███    ███ ███    ███   ███    ███    ▀███▀▀██   ███    █▀  
        ███▌ ███   ███ ███   ███ ███    ███ ███    ███   ███    ███     ███   ▀  ▄███▄▄▄     
        ███▌ ███   ███ ███   ███ ███    ███ ███    ███ ▀███████████     ███     ▀▀███▀▀▀     
        ███  ███   ███ ███   ███ ███    ███ ███    ███   ███    ███     ███       ███    █▄  
        ███  ███   ███ ███   ███ ███    ███ ███    ███   ███    ███     ███       ███    ███ 
        █▀    ▀█   █▀   ▀█   █▀   ▀██████▀   ▀██████▀    ███    █▀     ▄████▀     ██████████ 
                                                                                            
    ▄████████  ▄█        ▄█                                                                  
    ███    ███ ███       ███                                                                  
    ███    █▀  ███       ███▌                                                                 
    ███        ███       ███▌                                                                 
    ███        ███       ███▌                                                                 
    ███    █▄  ███       ███                                                                  
    ███    ███ ███▌    ▄ ███                                                                  
    ████████▀  █████▄▄██ █▀           
            """
            try:
                from fade import fire as fade_fire
                print(fade_fire(banner))
            except ImportError:
                print(banner)

            print("\n🌟 Welcome to \033[1;36mInnovate CLI 0.7.1\033[0m 🌟")
            print("————————————————————————————————————————————————————")
            print("🚀 The tool that helps imaginations turn into reality.")
            print("💻 Build stunning projects with AI-powered precision.")
            print("")
            print(f"{Fore.CYAN}🌐 WEBSITE MODE{Style.RESET_ALL}  →  Create world-class websites")
            print("   • Modern, responsive, and visually stunning designs")
            print("   • HTML, CSS, JS, backend setup & deployment(coming soon!).")
            print("   • React and Next.js along with other NPM frameworks are now compatible(vanilla css only).")
            print("")
            print(f"{Fore.MAGENTA}📱 APP MODE{Style.RESET_ALL}      →  Build full-featured applications")
            print("   • Python apps, C, JS, and more")
            print("   • End-to-end setup, configuration, and execution")
            print("")
            print("📚 Docs: \033[4minnovate.vaidik.co/docs\033[0m (in progress)")
            print("📩 Support: vk@vaidik.co | \033[4mvaidik.co\033[0m")
            print(f"💡 Project by: {Fore.YELLOW}Vaidik K.{Style.RESET_ALL}")
            print("————————————————————————————————————————————————————\n")

        else:
            print(configure)
            print("innovateCLI, product of vaidik.co")




def getDIR():
    return dir