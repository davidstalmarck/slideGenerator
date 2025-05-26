import tempfile
import subprocess
import os
import glob
import datetime
import shutil

def clean_code(content):
    """Remove Markdown-style code fences from code blocks."""
    return "\n".join([
        line for line in content.splitlines()
        if not line.strip().startswith("```")
    ])

def run_pptx_code_and_convert_to_png(code_str, pptx_name="output.pptx", output_dir="saved_pptx"):
    """
    Executes PowerPoint-generating Python code, converts it to PNG using LibreOffice,
    and saves the first slide image with a timestamped filename.

    Args:
        code_str (str): Python code that generates a .pptx file.
        pptx_name (str): Expected name of the generated .pptx file.
        output_dir (str): Directory where both .pptx and .png will be stored.

    Returns:
        str: Full path to the saved PNG slide with a unique timestamped filename.

    Raises:
        RuntimeError or FileNotFoundError if anything fails.
    """
    try:
        # Clean and display the code
        python_code = clean_code(code_str)
        print("Running generated code:\n", python_code)

        # Ensure output directory exists
        output_dir = os.path.abspath(output_dir)
        os.makedirs(output_dir, exist_ok=True)
        pptx_path = os.path.join(output_dir, pptx_name)

        # Save the Python code to a temp file
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(python_code)
            temp_filename = f.name

        # Run the code in the output directory
        exit_code = os.system(f"cd {output_dir} && python3 {temp_filename}")
        os.remove(temp_filename)

        if exit_code != 0:
            raise RuntimeError("Execution of generated Python code failed.")

        if not os.path.exists(pptx_path):
            raise FileNotFoundError(f"{pptx_path} was not created.")

        # Convert .pptx to PNG using LibreOffice
        subprocess.run([
            "/Applications/LibreOffice.app/Contents/MacOS/soffice",
            "--headless",
            "--convert-to", "png",
            pptx_path,
            "--outdir", output_dir
        ], check=True, capture_output=True)

        # Find any PNG slides (case-insensitive)
        png_files = sorted(
            glob.glob(os.path.join(output_dir, "output.png")) +
            glob.glob(os.path.join(output_dir, "output.PNG")),
            key=lambda f: int(''.join(filter(str.isdigit, f)))
        )

        if not png_files:
            raise FileNotFoundError("No PNG slides were generated.")

        # Create a timestamped filename and move the first slide there
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"slide_{timestamp}.png"
        new_filepath = os.path.join(output_dir, new_filename)
        shutil.move(png_files[0], new_filepath)

        return new_filepath

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"LibreOffice conversion failed: {e.stderr.decode()}") from e
    except Exception as e:
        raise RuntimeError(f"An error occurred: {e}")
