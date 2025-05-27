from concurrent.futures import ProcessPoolExecutor, as_completed
import uuid
from openai import OpenAI
import os
import time
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

def generate_response(prompt, step, image=None, max_retries=3):
    """
    Generates PowerPoint Python code from OpenAI, executes it to create a PPTX, converts the PPTX to PNG, and returns the PNG path.
    Retries on failure by appending the error message to the prompt.
    """

    system_message = (
        "You are a Python expert generating PowerPoint presentations using the python-pptx library. "
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

    attempt = 0
    while attempt < max_retries:
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]

        if image:
            messages.append({"role": "user", "content": "Attached image."})

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.7
            )

            raw_code = response.choices[0].message.content
            python_code = clean_code(raw_code)

            # Execute the generated code and convert the PPTX to PNG
            png_path = run_pptx_code_and_convert_to_png(python_code)

            return png_path  # Successful return path to the PNG

        except Exception as e:
            error_message = f"\nEncountered error: {str(e)}"
            prompt += error_message
            attempt += 1
            print(f"Attempt {attempt} failed: {e}. Retrying...")
            #time.sleep(1)

    print("Maximum retries reached, returning None.")
    return None

def generate_multiple_designs(prompts, steps, images=None):
    results = []
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = []
        for idx, prompt in enumerate(prompts):
            step = steps[idx] if steps else "overview"
            image = images[idx] if images else None
            # Use a unique file_prefix for each job
            file_prefix = f"output_{idx}_{uuid.uuid4().hex[:8]}"
            future = executor.submit(generate_response, prompt, step, image, 5, file_prefix)
            futures.append(future)
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(f"Completed design, result path: {result}")
    return results

def generate_multiple_designs(prompt, step, image=None):
    results = []
    
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = []
        N = 4
        for idx in range(N):
            filename = f'output_{idx}.pptx'
            # Update the prompt to ensure unique output filenames
            modified_prompt = f"{prompt}\nSave the file as '{filename}'."

            future = executor.submit(generate_response, modified_prompt, step, image)
            futures.append(future)

        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(f"Completed design, result path: {result}")

    return results
