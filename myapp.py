from flask import Flask, request, jsonify
from flask_cors import CORS
from flasgger import Swagger, swag_from
import shutil
import whisper
from google import genai

app = Flask(__name__)


CORS(app, origins=["localhost:5000","*"], supports_credentials=True, 
     allow_headers="*", methods=["GET", "POST", "OPTIONS"])
swagger = Swagger(app)

# Initialize Google AI client
client = genai.Client(api_key="AIzaSyDqke_QuuoauIY_UUP-aaqdnY21Of7r6Rc")

def get_ai_response(prompt):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text

# Load Whisper model once
whisper_model = whisper.load_model("large")  # or "base" for faster tests

@app.route("/", methods=["GET"])
@swag_from({
    "responses": {
        200: {
            "description": "Root endpoint",
            "content": {
                "application/json": {
                    "example": {"message": "Hello World"}
                }
            }
        }
    }
})
def root():
    return jsonify({"message": "Hello World"})

@app.route("/upload-audio/", methods=["POST"])
@swag_from({
    "parameters": [
        {
            "name": "file",
            "in": "formData",
            "type": "file",
            "required": True,
            "description": "Audio file to transcribe"
        }
    ],
    "responses": {
        200: {
            "description": "Transcribed text and AI response",
            "content": {
                "application/json": {
                    "example": {
                        "filename": "audio.wav",
                        "content_type": "audio/wav",
                        "input": "Hello world",
                        "response": "AI explanation"
                    }
                }
            }
        }
    }
})
def upload_audio():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    file_path = f"uploaded_{file.filename}"
    file.save(file_path)

    # Transcribe audio
    result = whisper_model.transcribe(file_path)

    # Generate AI response
    ai_text = get_ai_response(result["text"])

    return jsonify({
        "filename": file.filename,
        "content_type": file.content_type,
        "input": result["text"],
        "response": ai_text
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=True)
