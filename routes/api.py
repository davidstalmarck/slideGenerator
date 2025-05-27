from flask import Blueprint, request, jsonify, send_file
from services.openai_prompt import generate_response, generate_multiple_designs
from services.pptx_utils import save_pptx, assemble_all_pptx
import base64

api_bp = Blueprint("api", __name__)

@api_bp.route("/create", methods=["POST"])
def create():
    data = request.json
    prompts = data.get("prompts", [])
    step = data.get("step", "overview")

    png_paths = generate_multiple_designs(prompts, step)

    images_base64 = []
    for path in png_paths:
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            images_base64.append(f"data:image/png;base64,{encoded}")

    return jsonify({"images": images_base64})


@api_bp.route("/create-with-image", methods=["POST"])
def create_with_image():
    prompt = request.form.get("prompt", "")
    step = request.form.get("step", "overview")
    image = request.files.get("image")
    image_bytes = image.read() if image else None
    
    png_paths = generate_multiple_designs(prompt, step)

    images_base64 = []
    for path in png_paths:
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            images_base64.append(f"data:image/png;base64,{encoded}")

    return jsonify({"images": images_base64})

@api_bp.route("/save", methods=["POST"])
def save():
    data = request.json
    slides = data.get("slides", [])
    pptx_id = data.get("id", "default")
    filepath = save_pptx(slides, pptx_id)
    return jsonify({"status": "saved", "file": filepath})

@api_bp.route("/assemble", methods=["POST"])
def assemble():
    output_path = assemble_all_pptx()
    return jsonify({"status": "assembled", "file": output_path})
