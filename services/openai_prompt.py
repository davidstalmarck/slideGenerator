from openai import OpenAI
import os
from dotenv import load_dotenv
from services.convert_pptx_to_png import run_pptx_code_and_convert_to_png, clean_code
load_dotenv()

client = OpenAI()

STEP_CONTEXT = {
    "overview": "You are helping design the overall structure of a presentation.",
    "design": "You are suggesting layout, colors, and visuals.",
    "content": "You are suggesting detailed bullet points or descriptions.",
    "animations": "You are suggesting slide transition and element animations."
}

def generate_response(prompt, step, image=None):
    """
    Generates PowerPoint Python code from OpenAI and returns path to PNG preview.
    """

    system_message = (
    "You are a Python expert generating PowerPoint presentations using the `python-pptx` library. "
    "Always begin the code with:\n"
    "from pptx import Presentation\n"
    "from pptx.util import Inches\n"
    "from pptx.dml.color import RGBColor\n"
    "Only return valid Python code that creates a PowerPoint file called 'output.pptx'. "
    "The presentation must include exactly one slide based on the user's prompt. "
    "The code must be fully self-contained and runnable without requiring any external images, files, or internet access. "
    "You do not have access to any external files or images, so do not use or reference any local files like 'image.png' or URLs. "
    "Do not include more than one slide. Do not include explanations or any extra text."
)
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt}
    ]
    
    if image:
        # Optional: Extend with image handling if Vision API used
        messages.append({"role": "user", "content": "Attached image."})
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.7
    )

    raw_code = response.choices[0].message.content
    python_code = clean_code(raw_code)

    # Run the code + convert the pptx to PNG
    png_path = run_pptx_code_and_convert_to_png(python_code)
    
    return png_path  # Return path to Slide1.png