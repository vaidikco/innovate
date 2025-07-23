from innovate import Innovate
cli = Innovate(api_key="AIzaSyBraenCIuVM6jRPCSCQkWylfnFnu6cqK8I")
cli.ascii()
while True:
    cli.generate(str(input("? ".strip())))