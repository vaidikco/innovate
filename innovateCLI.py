from src.innovate import Innovate
if __name__ == "__main__":
    cli = Innovate(api_key="AIzaSyBraenCIuVM6jRPCSCQkWylfnFnu6cqK8I")
    cli.ascii()
    while True:
        user_input = input("? ").strip()
        if user_input.lower() in ['exit', 'quit']:
            break
        cli.generate(user_input)