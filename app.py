from flask import Flask, request, jsonify, render_template
from parser import handle_packet

app = Flask(__name__)

@app.route('/')
def index():
    print("Received")
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    file_data = file.read()
    result = handle_packet(file_data)
    
    return result

if __name__ == '__main__':
    print("Running")
    app.run(debug=True)
