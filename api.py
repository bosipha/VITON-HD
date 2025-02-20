from flask import Flask, request, jsonify, send_file
import os
import subprocess

app = Flask(__name__)

UPLOAD_FOLDER = 'datasets/test/image'
CLOTH_FOLDER = 'datasets/test/cloth'
RESULTS_FOLDER = 'results/viton_test'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(CLOTH_FOLDER):
    os.makedirs(CLOTH_FOLDER)
if not os.path.exists(RESULTS_FOLDER):
    os.makedirs(RESULTS_FOLDER)

@app.route('/')
def home():
    return jsonify({"message": "VITON-HD API is running!"})

@app.route('/try-on', methods=['POST'])
def try_on():
    # Ensure files are uploaded
    if 'model' not in request.files or 'clothing' not in request.files:
        return jsonify({"error": "Missing model or clothing image"}), 400

    model_file = request.files['model']
    clothing_file = request.files['clothing']

    model_path = os.path.join(UPLOAD_FOLDER, model_file.filename)
    clothing_path = os.path.join(CLOTH_FOLDER, clothing_file.filename)

    model_file.save(model_path)
    clothing_file.save(clothing_path)

    # Update test_pairs.txt with new entries
    with open("datasets/test_pairs.txt", "w") as f:
        f.write(f"{model_file.filename} {clothing_file.filename}\n")

    # Run VITON-HD
    command = [
        "python", "test.py", "--name", "viton_test", 
        "--dataset_dir", "datasets", "--dataset_list", "datasets/test_pairs.txt", 
        "--checkpoint_dir", "checkpoints", "--seg_checkpoint", "seg_final.pth", 
        "--gmm_checkpoint", "gmm_final.pth", "--alias_checkpoint", "alias_final.pth", 
        "--save_dir", "results"
    ]
    subprocess.run(command)

    # Get the generated image
    output_filename = f"{model_file.filename.split('.')[0]}_{clothing_file.filename.split('.')[0]}.jpg"
    output_path = os.path.join(RESULTS_FOLDER, output_filename)

    if not os.path.exists(output_path):
        return jsonify({"error": "Failed to generate try-on image"}), 500

    return send_file(output_path, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
