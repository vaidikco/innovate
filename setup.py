import os
import subprocess
import sys
import time
import shutil
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from tkinter.font import Font
from PIL import Image, ImageTk
from colorama import Fore, init

init(autoreset=True)

try:
    import pythoncom
    import win32com.client
except ImportError:
    subprocess.call([sys.executable, "-m", "pip", "install", "pywin32"])
    import pythoncom
    import win32com.client

# ========== Functions ==========
def install(package):
    subprocess.call([sys.executable, "-m", "pip", "install", "--quiet", "--upgrade", package])

def add_to_path(directory):
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ) as key:
            try:
                existing_path, _ = winreg.QueryValueEx(key, "Path")
            except FileNotFoundError:
                existing_path = ""
        if directory.lower() in existing_path.lower():
            return "Already in PATH"
        else:
            new_path = existing_path + ";" + directory if existing_path else directory
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
            return "Added to PATH"
    except Exception as e:
        return f"Failed to update PATH: {e}"

def create_shortcut(exe_path, shortcut_name="Innovate CLI"):
    start_menu_path = os.path.join(os.environ["ProgramData"], "Microsoft", "Windows", "Start Menu", "Programs")
    shortcut_path = os.path.join(start_menu_path, f"{shortcut_name}.lnk")
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.TargetPath = exe_path
    shortcut.WorkingDirectory = os.path.dirname(exe_path)
    shortcut.IconLocation = exe_path
    shortcut.save()
    return shortcut_path

# ========== GUI Setup ==========
class InstallerApp:
    def __init__(self, root):
        self.root = root
        root.title("Innovate CLI Installer")
        root.geometry("600x400")
        root.configure(bg="#121212")

        self.font = Font(family="Segoe UI", size=12)

        self.title_label = tk.Label(root, text="Innovate CLI Installer", font=("Segoe UI", 20, "bold"), fg="#00FFAA", bg="#121212")
        self.title_label.pack(pady=20)

        self.key_label = tk.Label(root, text="Enter your Gemini API Key:", fg="white", bg="#121212", font=self.font)
        self.key_label.pack(pady=(10, 0))

        self.api_entry = tk.Entry(root, width=50, font=self.font)
        self.api_entry.pack(pady=5)

        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=30)

        self.status_label = tk.Label(root, text="Status: Waiting to start...", fg="white", bg="#121212", font=self.font)
        self.status_label.pack(pady=5)

        self.install_btn = tk.Button(root, text="Install", command=self.run_installation, font=self.font, bg="#00AAFF", fg="white", width=20)
        self.install_btn.pack(pady=20)

    def update_status(self, msg):
        self.status_label.config(text=f"Status: {msg}")

    def run_installation(self):
        threading.Thread(target=self.install_process).start()

    def install_process(self):
        self.progress["value"] = 0
        self.update_status("Installing dependencies")
        for i, pkg in enumerate(["google-genai", "fade", "python-dotenv", "colorama", "pywin32"]):
            install(pkg)
            self.progress["value"] += 10
            self.root.update_idletasks()

        time.sleep(1)

        self.update_status("Creating .env file")
        api_key = self.api_entry.get().strip()
        with open(".env", "w") as f:
            f.write(f"GEMINI_API_KEY={api_key}\n")
        self.progress["value"] += 10

        self.update_status("Copying files to C:\\innovate")
        install_path = "C:\\innovate"
        try:
            if not os.path.exists(install_path):
                shutil.copytree(os.getcwd(), install_path)
            else:
                self.update_status("Directory exists. Skipping copy.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy directory: {e}")
            return
        self.progress["value"] += 30

        self.update_status("Adding to PATH")
        path_status = add_to_path(install_path)
        self.progress["value"] += 20

        self.update_status("Creating Start Menu shortcut")
        exe_path = os.path.join(install_path, "innovate.exe")
        create_shortcut(exe_path)
        self.progress["value"] += 20

        self.update_status("Installation complete!")
        messagebox.showinfo("Done", "Innovate CLI installed successfully!")


if __name__ == "__main__":
    root = tk.Tk()
    app = InstallerApp(root)
    root.mainloop()
