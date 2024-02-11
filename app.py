from flask import Flask, request, jsonify
import os
from linkedin import Linkedin  # Make sure to adjust the import path based on your project structure

app = Flask(__name__)

@app.route('/')
def home():
    return "HOME"


@app.route('/apply', methods=['POST'])
def apply_jobs():
    # Extract credentials and additional questions from the request
    data = request.json
    email = data['email']
    password = data['password']
    additional_questions_path = data['additional_questions_path']
    
    # Initialize and run the Linkedin bot
    bot = Linkedin(email=email, password=password, additional_questions_path=additional_questions_path)
    result = bot.linkJobApply()  # Ensure this method returns some result or status
    
    return jsonify({"message": "Application process completed.", "result": result})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

