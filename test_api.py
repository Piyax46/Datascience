import requests
import json

def test_recommendation():
    url = "http://127.0.0.1:5000/recommend"
    payloads = [
        {
            "symptoms": ["ท้องเสีย"],
            "gender": "male",
            "age": 26
        },
        {
            "symptoms": ["ไอ", "น้ำมูกไหล"],
            "gender": "female",
            "age": 30
        }
    ]
    headers = {'Content-Type': 'application/json'}
    
    results = []
    for payload in payloads:
        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            if response.status_code == 200:
                results.append({
                    "payload": payload,
                    "response": response.json()
                })
            else:
                results.append({
                    "payload": payload,
                    "error": response.status_code,
                    "message": response.text
                })
        except Exception as e:
            results.append({
                "payload": payload,
                "error": "Connection failed",
                "message": str(e)
            })

    with open('test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("Test completed. Results saved to test_results.json")

if __name__ == "__main__":
    test_recommendation()
