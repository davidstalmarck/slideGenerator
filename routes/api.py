from flask import Blueprint, request, jsonify, send_file
from services.openai_prompt import generate_response
from services.pptx_utils import save_pptx, assemble_all_pptx

api_bp = Blueprint("api", __name__)

@api_bp.route("/create", methods=["POST"])
def create():
    data = request.json
    prompt = data.get("prompt", "")
    step = data.get("step", "overview")
    png_path = generate_response(prompt, step)
    return send_file(png_path, mimetype="image/png", as_attachment=False)

@api_bp.route("/create-with-image", methods=["POST"])
def create_with_image():
    prompt = request.form.get("prompt", "")
    step = request.form.get("step", "overview")
    image = request.files.get("image")
    image_bytes = image.read() if image else None
    png_path = generate_response(prompt, step, image=image_bytes)
    return send_file(png_path, mimetype="image/png", as_attachment=False)

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
