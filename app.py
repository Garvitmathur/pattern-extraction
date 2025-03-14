import streamlit as st
import requests
import pandas as pd

FLASK_API_URL = "http://127.0.0.1:5060"

st.title(" Pattern Extraction & NER Tool")



uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    files = {"file": uploaded_file.getvalue()}
   
    response = requests.post(f"{FLASK_API_URL}/upload", files=files)
    
    if response.status_code == 200: 
        st.success(" File uploaded and processed!")
    else:
        st.error(f" Upload failed: {response.json().get('error', 'Unknown error')}")


inptext = st.text_area("Enter text for processing:")


use_spacy = st.checkbox("Enable SpaCy NER")


if st.button("Submit"):
    if inptext.strip():
        response = requests.post(f"{FLASK_API_URL}/match_patterns", json={"text": inptext, "use_spacy": use_spacy})

        if response.status_code == 200:
            st.session_state["response_data"] = response.json()
            st.rerun()  
        else:
            st.error(" Error processing request.")


if "response_data" in st.session_state:
    response_data = st.session_state["response_data"]
    

    
    patterns = response_data.get("patterns", [])
    tokens = response_data.get("tokens", [])
    ner_entities = response_data.get("ner_entities", [])

    
    combined_data = {}

    for p in patterns:
        key = p.get("pattern_instance", "").lower()
        combined_data[key] = {
            "Matched Text": p.get("pattern_instance", ""),
            "Pattern Class": p.get("pattern_class", ""),
            "Pattern Subclass": p.get("pattern_subclass", ""),
            "Token Class": "",
            "Token Instance": ""
        }

    for t in tokens:
        key = t.get("token_instance", "").lower()
        if key in combined_data:
            combined_data[key]["Token Class"] = t.get("token_class", "")
            combined_data[key]["Token Instance"] = t.get("token_instance", "")
        else:
            combined_data[key] = {
                "Matched Text": t.get("token_instance", ""),
                "Pattern Class": "",
                "Pattern Subclass": "",
                "Token Class": t.get("token_class", ""),
                "Token Instance": t.get("token_instance", "")
                
            }

    
    if combined_data:
        df_combined = pd.DataFrame(combined_data.values()).drop_duplicates()
        st.write("Matched Patterns & Tokens")
        st.table(df_combined)

    
    if use_spacy and ner_entities:
        df_ner = pd.DataFrame(ner_entities)
        st.write(" SpaCy Named Entity Recognition (NER) Results")
        st.table(df_ner)



    


