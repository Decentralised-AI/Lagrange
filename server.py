from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from model.chat import chat
import markdown
import os
import json
app = Flask(__name__)
CORS(app)  # Enable CORS on all routes

last_response = None  # Global variable to hold the last processed response
if os.path.isdir('C://Lagrange') is False:
    print('Creating Lagrange directory ----------------------------')
    os.mkdir('C://Lagrange')
else:
    print('Directory exists......continuing -----------------------------')

def create_file_node(file_path):
    """
    Create a file node with its name, path, and children.
    """
    return {
        "name": os.path.basename(file_path),
        "path": file_path,
        "children": []
    }

def create_directory_node(dir_path):
    """
    Recursively create a directory node with its name, path, and children.
    """
    node = create_file_node(dir_path)
    children = []
    for child_name in os.listdir(dir_path):
        child_path = os.path.join(dir_path, child_name)
        if os.path.isdir(child_path):
            children.append(create_directory_node(child_path))
        else:
            children.append(create_file_node(child_path))
    node["children"] = children
    return node

def update_file_tree(directory_path="C:\\Lagrange", output_file="C:\\Lagrange\\file_tree.json"):
    """
    Update the file tree of the specified directory and save it as a JSON file.
    """
    root_node = create_directory_node(directory_path)
    with open(output_file, "w") as json_file:
        json.dump(root_node, json_file, indent=4)
@app.route('/')
def page():
    return render_template('index.html')
@app.route('/send_string', methods=['GET'])
def send_string():
    global last_response
    if last_response:
        return last_response
    else:
        return "No message processed yet!"

@app.route('/input_t', methods=['POST'])
def input_t():
    global last_response
    if request.is_json:
        data = request.get_json()
        last_response = chat(data['message'],data['fileList'])
        print(last_response)
        return markdown.markdown(last_response), 200
    return "Invalid data", 400

@app.route('/input_m', methods=['POST'])
def input_m():
    if 'document' not in request.files:
        return "No document part", 400
    file = request.files['document']
    if file.filename == '':
        return "No selected file", 400
    if file:
        filename = file.filename
        os.mkdir('media')
        file.save(f"./media/{filename}")
        return f"Document {filename} received and saved.", 200
    return "Invalid data", 400
    
@app.route('/open-file', methods=['POST'])
def open_file():
    data = request.get_json()
    file_path = data.get('filePath')
    if file_path:
        try:
            path = os.path.join("C:/Lagrange/", file_path)
            os.startfile(path)
            return jsonify({'message': f'File "{file_path}" opened successfully.'}), 200
        except Exception as e:
            return jsonify({'error': f'Failed to open file: {e}'}), 500
    else:
        return jsonify({'error': 'File path not provided.'}), 400

@app.route('/get-json', methods=['GET'])
def read_json():
    try:
        update_file_tree()
        json_file_path = 'C:\\Lagrange\\file_tree.json'
        with open(json_file_path, 'r') as file:
            json_data = json.load(file)
        return jsonify(json_data)
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
