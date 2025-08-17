"""
innovatecli version 0.7.1,
all contents and code drafted by Vaidik K. and generative AI.
any concerns:
go to innovate.vaidik.co, or check the README.md to get a link for the discord server
"""
from src.innovate import Innovate
from dotenv import load_dotenv
import os

load_dotenv()

if __name__ == "__main__":
    api_key = os.getenv("GEMINI_API_KEY") or "YOUR_API_KEY"
    cli = Innovate(api_key=api_key)
    cli.ascii()

    while True:
        mode = input("Select mode (website/app): ").strip().lower()
        user_input = input("? ").strip()

        if user_input.lower() in ['exit', 'quit']:
            break

        cli.generate(user_input, mode)
