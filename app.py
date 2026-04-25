from flask import Flask, request, jsonify
from flask_cors import CORS
from recommender import SymptomRecommender
import os

app = Flask(__name__)
CORS(app)

# Load recommender
recommender = SymptomRecommender('processed_data.json')

@app.route('/recommend', methods=['POST'])
def get_recommendation():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    current_symptoms = data.get('symptoms', [])
    gender = data.get('gender')
    age = data.get('age')
    top_n = data.get('top_n', 5)
    
    if not current_symptoms:
        return jsonify({"error": "Symptoms are required"}), 400
    
    recommendations = recommender.recommend(current_symptoms, gender=gender, age=age, top_n=top_n)
    
    return jsonify({
        "current_symptoms": current_symptoms,
        "recommendations": recommendations
    })

@app.route('/symptoms', methods=['GET'])
def list_symptoms():
    symptoms = recommender.all_symptoms
    return jsonify({
        "total": len(symptoms),
        "symptoms": sorted(symptoms)
    })

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        "status": "online",
        "service": "Agnos Symptom Recommender API",
        "endpoints": {
            "/recommend": "POST - Get symptom recommendations",
            "/symptoms": "GET - List all unique symptoms"
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
