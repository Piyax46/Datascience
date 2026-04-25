import json
from collections import Counter

class SymptomRecommender:
    def __init__(self, data_path='processed_data.json'):
        with open(data_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.all_symptoms = self._get_all_unique_symptoms()

    def _get_all_unique_symptoms(self):
        symptoms = set()
        for record in self.data:
            for s in record['symptoms']:
                symptoms.add(s)
        return list(symptoms)

    def _normalize(self, symptom):
        """Normalize symptom: strip whitespace only (do NOT lowercase Thai text)."""
        return symptom.strip()

    def recommend(self, current_symptoms, gender=None, age=None, top_n=5):
        # Normalize input: strip only, keep Thai characters as-is
        current_symptoms = [self._normalize(s) for s in current_symptoms]

        related_records = []
        for record in self.data:
            record_symptoms = [self._normalize(s) for s in record['symptoms']]
            if any(s in record_symptoms for s in current_symptoms):
                related_records.append(record)

        if not related_records:
            return self._get_popular_symptoms(exclude=current_symptoms, top_n=top_n)

        # Weighted count: give higher weight to demographically similar patients
        counts = Counter()
        for record in related_records:
            weight = 1
            if gender and record.get('gender') == gender:
                weight += 1
            if age is not None and record.get('age') is not None:
                age_diff = abs(record['age'] - age)
                if age_diff <= 5:
                    weight += 2
                elif age_diff <= 10:
                    weight += 1

            for s in record['symptoms']:
                norm = self._normalize(s)
                if norm not in current_symptoms:
                    counts[norm] += weight

        recommended = [s for s, _ in counts.most_common(top_n)]

        if len(recommended) < top_n:
            popular = self._get_popular_symptoms(
                exclude=current_symptoms + recommended,
                top_n=top_n - len(recommended)
            )
            recommended.extend(popular)

        return recommended

    def _get_popular_symptoms(self, exclude=[], top_n=5):
        counts = Counter()
        for record in self.data:
            for s in record['symptoms']:
                norm = self._normalize(s)
                if norm not in exclude:
                    counts[norm] += 1
        return [s for s, _ in counts.most_common(top_n)]


if __name__ == "__main__":
    recommender = SymptomRecommender()
    test_symptoms = ["ท้องเสีย"]
    recommendations = recommender.recommend(test_symptoms, gender="male", age=26)
    print(f"Input: Male, 26Y, symptoms={test_symptoms}")
    print(f"Recommended: {recommendations}")
