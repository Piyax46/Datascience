from flask import Flask, request, jsonify
try:
    from flask_cors import CORS
    HAS_CORS = True
except ImportError:
    HAS_CORS = False

from recommender import SymptomRecommender
import os

app = Flask(__name__)
if HAS_CORS:
    CORS(app)

# Load recommender once at startup
recommender = SymptomRecommender('processed_data.json')


@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        "status": "online",
        "service": "Agnos Symptom Recommender API",
        "version": "1.0.0",
        "endpoints": {
            "POST /recommend": "Get symptom recommendations based on current symptoms",
            "GET /symptoms": "List all known symptoms in the dataset"
        }
    })


@app.route('/recommend', methods=['POST'])
def get_recommendation():
    """
    Recommend next possible symptoms based on current symptoms and patient profile.

    Request body (JSON):
    {
        "symptoms": ["ท้องเสีย"],     # required: list of current symptoms
        "gender": "male",              # optional: "male" | "female"
        "age": 26,                     # optional: integer age
        "top_n": 5                     # optional: number of recommendations (default 5)
    }

    Response:
    {
        "current_symptoms": [...],
        "recommendations": [...]
    }
    """
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    current_symptoms = data.get('symptoms', [])
    if not current_symptoms:
        return jsonify({"error": "'symptoms' field is required and must not be empty"}), 400

    if not isinstance(current_symptoms, list):
        return jsonify({"error": "'symptoms' must be a list of strings"}), 400

    gender = data.get('gender')
    age = data.get('age')
    top_n = data.get('top_n', 5)

    try:
        top_n = int(top_n)
        if not (1 <= top_n <= 20):
            top_n = 5
    except (ValueError, TypeError):
        top_n = 5

    recommendations = recommender.recommend(
        current_symptoms,
        gender=gender,
        age=age,
        top_n=top_n
    )

    return jsonify({
        "current_symptoms": current_symptoms,
        "recommendations": recommendations
    })


@app.route('/symptoms', methods=['GET'])
def list_symptoms():
    """Return all unique symptoms in the dataset."""
    return jsonify({
        "total": len(recommender.all_symptoms),
        "symptoms": sorted(recommender.all_symptoms)
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Agnos Symptom Recommender API on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
