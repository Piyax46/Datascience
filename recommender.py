import json
from collections import Counter

class SymptomRecommender:
    def __init__(self, data_path='processed_data.json'):
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = []
        self.all_symptoms = self._get_all_unique_symptoms()

    def _get_all_unique_symptoms(self):
        symptoms = set()
        for record in self.data:
            for s in record.get('symptoms', []):
                symptoms.add(s)
        return list(symptoms)

    def recommend(self, current_symptoms, gender=None, age=None, top_n=5):
        # Normalize current symptoms
        current_symptoms = [s.strip() for s in current_symptoms] # Thai doesn't need lower()
        
        # Scoring map for symptoms
        symptom_scores = Counter()
        
        # Find records and calculate weights
        for record in self.data:
            record_symptoms = record.get('symptoms', [])
            
            # Check if this record shares any symptom with the input
            shared = [s for s in current_symptoms if s in record_symptoms]
            if not shared:
                continue
                
            # Base weight: +1 for shared symptom
            weight = 1.0
            
            # Step 2: Demographic weighting (from README)
            if gender and record.get('gender') == gender:
                weight += 1.0 # Same gender
                
            if age and record.get('age') is not None:
                try:
                    age_diff = abs(int(record['age']) - int(age))
                    if age_diff <= 5:
                        weight += 2.0 # Age difference <= 5 yr
                    elif age_diff <= 10:
                        weight += 1.0 # Age difference <= 10 yr
                except (ValueError, TypeError):
                    pass
            
            # Step 3: Frequency ranking
            for s in record_symptoms:
                if s not in current_symptoms:
                    symptom_scores[s] += weight
        
        # If no recommendations found, return most popular overall
        if not symptom_scores:
            return self._get_popular_symptoms(exclude=current_symptoms, top_n=top_n)
            
        # Sort and return top N
        recommended = [s for s, score in symptom_scores.most_common(min(top_n, 20))]
        
        # Fill remaining slots if needed
        if len(recommended) < top_n:
            popular = self._get_popular_symptoms(exclude=current_symptoms + recommended, top_n=top_n - len(recommended))
            recommended.extend(popular)
            
        return recommended

    def _get_popular_symptoms(self, exclude=[], top_n=5):
        counts = Counter()
        for record in self.data:
            for s in record.get('symptoms', []):
                if s not in exclude:
                    counts[s] += 1
        return [s for s, count in counts.most_common(top_n)]

if __name__ == "__main__":
    recommender = SymptomRecommender()
    # Test with example: Male, 26 Y, ท้องเสีย
    test_symptoms = ["ท้องเสีย"]
    results = recommender.recommend(test_symptoms, gender="male", age=26)
    print(f"Input: {test_symptoms}, gender: male, age: 26")
    print(f"Recommended: {results}")
