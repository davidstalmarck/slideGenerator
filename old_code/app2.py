from flask import Flask, request, render_template, jsonify, send_file
from openai import OpenAI
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()
app = Flask(__name__)
CORS(app) # Allows all origins

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate-pptx", methods=["POST"])
def generate_pptx():
    user_prompt = request.form.get("user_prompt", "")
    system_message = (
    "You are a Python expert generating PowerPoint presentations using the `python-pptx` library. "
    "Only return valid Python code that creates a PowerPoint file called 'output.pptx'. "
    "The presentation must include exactly **one** slide based on the user's prompt. "
    "Do not include more than one slide. Do not include explanations or any extra text."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )

        python_code = response.choices[0].message.content
        print(python_code)
        python_code = clean_code(response.choices[0].message.content)
   
        # Save and execute the Python code
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode='w') as f:
            f.write(python_code)
            temp_filename = f.name

        exit_code = os.system(f"python3 {temp_filename}")
        os.remove(temp_filename)

        if exit_code != 0:
            return jsonify({"error": "Execution of generated code failed."}), 500
        output_filename = 'output.pptx'
        os.system(f"open {output_filename}")  # macOS
        return send_file(output_filename, as_attachment=True)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def clean_code(content):
    return "\n".join([
        line for line in content.splitlines()
        if not line.strip().startswith('```')
    ])


if __name__ == "__main__":
    app.run(debug=True)