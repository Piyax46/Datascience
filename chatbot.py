import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class AgnosChatbot:
    def __init__(self, data_path='forum_data.json'):
        with open(data_path, 'r', encoding='utf-8') as f:
            self.documents = json.load(f)

        # Use both title and url slug as text (full content if available)
        self.doc_texts = [self._build_doc_text(doc) for doc in self.documents]

        # Remove empty docs
        self.documents = [d for d, t in zip(self.documents, self.doc_texts) if t.strip()]
        self.doc_texts = [t for t in self.doc_texts if t.strip()]

        self.vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 4))
        if self.doc_texts:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.doc_texts)
        else:
            self.tfidf_matrix = None

    def _build_doc_text(self, doc):
        """Combine all text fields in a document for richer retrieval."""
        parts = []
        if doc.get('title'):
            parts.append(doc['title'])
        if doc.get('content'):
            parts.append(doc['content'])
        # Extract readable text from URL slug
        url = doc.get('url', '')
        slug = url.split('/')[-1]
        from urllib.parse import unquote
        parts.append(unquote(slug).replace('-', ' '))
        return ' '.join(parts)

    def retrieve(self, query, top_k=3):
        if self.tfidf_matrix is None or len(self.doc_texts) == 0:
            return []
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        top_indices = similarities.argsort()[-top_k:][::-1]

        results = []
        for idx in top_indices:
            if similarities[idx] > 0.05:  # Lower threshold for Thai char n-grams
                doc = self.documents[idx].copy()
                doc['score'] = float(similarities[idx])
                results.append(doc)
        return results

    def generate_response(self, query):
        retrieved_docs = self.retrieve(query)

        if not retrieved_docs:
            return (
                "ขออภัยค่ะ ไม่พบข้อมูลที่เกี่ยวข้องในบอร์ดสุขภาพของ Agnos\n"
                "โปรดปรึกษาแพทย์โดยตรงเพื่อความปลอดภัยนะคะ"
            )

        # Build context from retrieved documents
        context_lines = []
        for doc in retrieved_docs:
            title = doc.get('title', '').strip()
            url = doc.get('url', '')
            if title:
                context_lines.append(f"• {title}\n  🔗 {url}")

        context = "\n\n".join(context_lines)

        response = (
            f"จากการค้นหาข้อมูลใน Agnos Health Forum พบเนื้อหาที่เกี่ยวข้องกับคำถามของคุณ:\n\n"
            f"{context}\n\n"
            f"⚠️ ข้อมูลนี้เป็นเพียงการปรึกษาเบื้องต้นจากฟอรัมเท่านั้น "
            f"กรุณาปรึกษาแพทย์ผู้เชี่ยวชาญผ่านแอป Agnos เพื่อการวินิจฉัยที่แม่นยำค่ะ"
        )

        return response


if __name__ == "__main__":
    chatbot = AgnosChatbot()
    queries = ["เจ็บหน้าอก หายใจไม่ออก", "ผื่นคัน", "ท้องเสีย ปวดท้อง"]
    for q in queries:
        print(f"\nUser: {q}")
        print(f"Chatbot: {chatbot.generate_response(q)}")
