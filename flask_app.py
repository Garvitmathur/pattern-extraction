from flask import Flask, request, jsonify
import spacy
import os
import pandas as pd
from db_utils import process_excel, create_tables, get_connection

app = Flask(__name__)


nlp = spacy.load("en_core_web_sm")
 



create_tables()

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    file_path = os.path.join("uploads", file.filename)
    os.makedirs("uploads", exist_ok=True)
    file.save(file_path)
    
    try:
        process_excel(file_path)
        return jsonify({"message": " File uploaded and processed!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/match_patterns", methods=["POST"])
def match_patterns():
    data = request.json
    text = data.get("text", "")
    use_spacy = data.get("use_spacy", False)
    

    if not text:
        return jsonify({"error": "No text provided"}), 400
    
        

    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    
    
    cur.execute("SELECT pattern_instance, pattern_class, pattern_subclass FROM pattern_config")
    patterns = cur.fetchall()
    
    

    
    cur.execute("SELECT token_instance, token_class FROM token_info")
    tokens = cur.fetchall()

    conn.close()
    

    
    matched_patterns = [
        {"pattern_instance": p["pattern_instance"], "pattern_class": p["pattern_class"], "pattern_subclass": p["pattern_subclass"]}
        for p in patterns if p["pattern_instance"].lower() in text.lower()
    ]
                

 
    matched_tokens = [
        {"token_instance": t["token_instance"], "token_class": t["token_class"]}
        for t in tokens if t["token_instance"].lower() in text.lower()
    ]
    
    
    ner_entities = []
    if use_spacy:
        doc = nlp(text)
        ner_entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]

    response = {
        "patterns": matched_patterns,
        "tokens": matched_tokens,
        "ner_entities": ner_entities  
    }

   
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True, port=5060)

