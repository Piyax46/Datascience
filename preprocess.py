import pandas as pd
import json
import re

def clean_symptom(text):
    if not text:
        return ""
    # Basic cleaning
    text = text.strip().lower()
    # Remove some common noise words
    noise = ['มี', 'อาการ', 'รู้สึก']
    for n in noise:
        text = text.replace(n, '')
    return text.strip()

def preprocess_data(file_path):
    df = pd.read_csv(file_path)
    
    patient_symptoms = []
    
    for idx, row in df.iterrows():
        try:
            if pd.isna(row['summary']):
                continue
            summary = json.loads(row['summary'])
            yes_symptoms = [clean_symptom(s['text']) for s in summary.get('yes_symptoms', [])]
            
            # search_term often contains multiple symptoms separated by comma
            search_terms = []
            if not pd.isna(row['search_term']):
                terms = re.split(r'[,/]', str(row['search_term']))
                search_terms = [clean_symptom(t) for t in terms]
            
            # Combine and unique
            all_symptoms = list(set(yes_symptoms + search_terms))
            # Filter out noise
            all_symptoms = [s for s in all_symptoms if s and len(s) > 1 and s not in ['nan', 'previous treatment', 'การรักษาก่อนหน้า', 'none']]
            
            if all_symptoms:
                patient_symptoms.append({
                    'gender': row['gender'],
                    'age': row['age'],
                    'symptoms': all_symptoms
                })
        except Exception as e:
            pass
            
    return patient_symptoms

if __name__ == "__main__":
    data = preprocess_data('dataset.csv')
    print(f"Total records processed: {len(data)}")
    
    # Save processed data for later use
    with open('processed_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
