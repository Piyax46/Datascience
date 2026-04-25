# Agnos Symptom Recommender — Data Science Assignment

## Solution Overview

### Main Task: Symptom Recommender System

The system uses a **demographic-weighted collaborative filtering** approach — similar to how Netflix recommends content based on what similar users watched:

```
Patient Input (gender, age, current symptoms)
        │
        ▼
┌─────────────────────────────────────────────┐
│  Step 1: Match historical records           │
│  Find all 1000 records that share at least  │
│  one symptom with the patient's input       │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  Step 2: Demographic weighting              │
│  • Same gender            → +1 point        │
│  • Age difference ≤ 5 yr  → +2 points       │
│  • Age difference ≤ 10 yr → +1 point        │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  Step 3: Frequency ranking                  │
│  Count weighted co-occurring symptoms       │
│  Return Top-N most frequent ones            │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
            Recommended Symptoms
```

**Key design decisions:**
- Thai text is **not lowercased** — avoids breaking Thai character matching
- **Graceful fallback** to globally popular symptoms when no match found
- Modular design: recommender logic is separate from API layer

### Bonus Task: RAG Chatbot

```
User Query
    │
    ▼
┌────────────────────────────────────────────┐
│  TF-IDF Vectorizer (char n-gram 2–4)       │
│  Optimized for Thai language               │
└───────────────────┬────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────┐
│  Cosine Similarity Retrieval               │
│  Find Top-K most relevant forum posts      │
└───────────────────┬────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────┐
│  Response Formatting                       │
│  Show retrieved posts + source links       │
│  + medical disclaimer                      │
└───────────────────┬────────────────────────┘
                    │
                    ▼
              Answer with sources
```

---

## Project Structure

```
Data Science/
├── dataset.csv           # 1000 patient records (raw input)
├── processed_data.json   # Cleaned & structured symptom data
├── forum_data.json       # Scraped Agnos forum posts (RAG database)
│
├── preprocess.py         # CSV → processed_data.json
├── recommender.py        # Core recommendation logic
├── app.py                # Flask REST API (port 5000)
├── test_api.py           # Automated API tests
│
├── scraper.py            # Scrapes agnoshealth.com/forums
├── chatbot.py            # RAG retrieval logic
├── ui.py                 # Streamlit UI (port 8501)
│
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

---

## Setup & Installation

### Requirements
- Python 3.8 or higher
- pip

### Step 1 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 2 — Prepare data (already included, but can re-run)

```bash
python preprocess.py
```

### Step 3 — Run the API

```bash
python app.py
```

API will be available at: `http://localhost:5000`

### Step 4 — Run the Streamlit UI (Bonus)

Open a **second terminal**, then:

```bash
streamlit run ui.py
```

UI will be available at: `http://localhost:8501`

---

## API Documentation

### `GET /`
Health check.

**Response:**
```json
{
  "status": "online",
  "service": "Agnos Symptom Recommender API"
}
```

---

### `POST /recommend`
Get recommended symptoms based on patient input.

**Request body (JSON):**
```json
{
  "symptoms": ["ท้องเสีย"],
  "gender": "male",
  "age": 26,
  "top_n": 5
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| symptoms | array[string] | ✅ | Current symptoms in Thai |
| gender | string | ❌ | "male" or "female" |
| age | integer | ❌ | Patient age |
| top_n | integer | ❌ | Number of results (default 5, max 20) |

**Response:**
```json
{
  "current_symptoms": ["ท้องเสีย"],
  "recommendations": ["ถ่ายเหลว", "ปวดท้อง", "อาเจียน", "คลื่นไส้", "ท้องเสียปวดท้องน้อย"]
}
```

---

### `GET /symptoms`
List all unique symptoms in the dataset.

**Response:**
```json
{
  "total": 318,
  "symptoms": ["กลืนลำบาก", "กลืนเจ็บ", ...]
}
```

---

## How to Test

### Option 1 — Run automated test script (recommended)

Make sure the API is running first (`python app.py`), then:

```bash
python test_api.py
```

Results will be saved to `test_results.json`.

---

### Option 2 — curl (Mac / Linux / PowerShell)

**Mac / Linux:**
```bash
curl -X POST http://localhost:5000/recommend \
  -H "Content-Type: application/json" \
  -d '{"symptoms": ["ท้องเสีย"], "gender": "male", "age": 26}'
```

**Windows PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/recommend" -Method POST -ContentType "application/json" -Body '{"symptoms": ["ท้องเสีย"], "gender": "male", "age": 26}'
```

**Windows CMD (single line):**
```cmd
curl -X POST http://localhost:5000/recommend -H "Content-Type: application/json" -d "{\"symptoms\": [\"\u0e17\u0e49\u0e2d\u0e07\u0e40\u0e2a\u0e35\u0e22\"], \"gender\": \"male\", \"age\": 26}"
```

---

### Option 3 — Python script (works on all platforms)

Create a file `quick_test.py` and run it:

```python
import requests

response = requests.post("http://localhost:5000/recommend", json={
    "symptoms": ["ท้องเสีย"],
    "gender": "male",
    "age": 26
})
print(response.json())
```

```bash
python quick_test.py
```

---

### Option 4 — Streamlit UI

Run `streamlit run ui.py` and open `http://localhost:8501` in your browser.

---

## Evaluation Criteria Checklist

| Criteria | Status | Notes |
|----------|--------|-------|
| Creativity | ✅ | Demographic-weighted collaborative filtering with age proximity scoring |
| Practicality | ✅ | Modular code, easy to extend and maintain |
| Accuracy | ✅ | Weighted by gender + age similarity for better personalization |
| API | ✅ | Flask REST API with input validation and error handling |
| Documentation | ✅ | README with architecture diagrams and multi-platform test instructions |
| Chat Interface (Bonus) | ✅ | Streamlit UI with RAG chatbot tab |
| Website Scraper (Bonus) | ✅ | scraper.py auto-scrapes agnoshealth.com/forums |
