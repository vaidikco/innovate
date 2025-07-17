import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel('gemini-1.5-flash')

def generate_quiz_question(difficulty="easy", q_type="MCQ"):
    prompt = f"Generate a unique {q_type} programming quiz question with a difficulty of {difficulty}. Provide the question, options (if MCQ), and the correct answer in a JSON format."
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating question: {e}"

def verify_code_answer(user_code, question):
    prompt = f"Given this question: '{question}', is the following code a correct solution? '{user_code}'. Respond with only 'Correct' or 'Incorrect' and a brief explanation."
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error verifying answer: {e}"

# Powered by Innovate CLI, a product of vaidik.co
