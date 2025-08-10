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
            "python", "html", "javascript", "js", "ts", "typescript", "bash", "sh", "json", "css"
        }:
            return "\n".join(lines[1:])
        return block.strip()

    def create_project_folder(self):
        os.makedirs("projects", exist_ok=True)
        suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
        rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
        folder = f"projects/project_{suffix}_{rand}"
        os.makedirs(folder, exist_ok=True)

        # Create innovate credits folder
        credits_dir = os.path.join(folder, "innovate")
        os.makedirs(credits_dir, exist_ok=True)
        with open(os.path.join(credits_dir, "credits.txt"), "w", encoding="utf-8") as f:
            f.write("Innovate CLI, product of vaidik.co\n")
            f.write("Version 0.5.4\n")
            f.write("Author: Vaidik K.\n")
            f.write("Website: innovate.vaidik.co\n")

        return folder


    def generate_steps(self, prompt):
        sys_prompt = (
            "You're a code execution planner known as Innovate CLI made by vaidik.co. From the user's request, "
            "generate a clean list of executable steps from the installation and the running procedure of the prompt given.\n"
            "Use ONLY this format:\n"
            "[CMD] shell command\n"
            "[CD] target_directory\n"
            "[CREATE] path/to/file.ext:\n```\nfile contents\n```\n"
            "[APPEND] path/to/file.ext:\n```\nappended content\n```\n"
            "No explanations. No markdown headings. Only actionable steps."
        )
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

    def generate(self, prompt: str):
        folder = self.create_project_folder()
        os.chdir(folder)
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
        raw_output = self.generate_steps(prompt)

        # --- Stop thinking spinner ---
        stop_event.set()
        spinner_thread.join()
        thinking_time = round(time.time() - (time.time() - 0), 2)  # we don't really need exact, just stop
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
        if configure=="":
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
    ╚═════╝╚══════╝╚═╝"""
            print(fade.random(banner))
            print("Welcome to Innovate CLI 0.6 !")
            print("> The tool which helps imaginations turn into a reality. One of the best coding tools that you can use.")
            print("> Official documentation available at innovate.vaidik.co/docs (in progress)")
            print("> If you're facing any errors or have suggestions, contact vk@vaidik.co or visit vaidik.co")
            print("> project by Vaidik K.")
        else:
            banner = f"""{configure}"""
            print("innovateCLI, product of vaidik.co")
