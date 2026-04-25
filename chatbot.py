import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

class AgnosChatbot:
    def __init__(self, data_path='forum_data.json'):
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                self.documents = json.load(f)
        except FileNotFoundError:
            self.documents = []
        
        # Prepare text for vectorization
        # Combining title and content for better context
        self.doc_texts = []
        for doc in self.documents:
            text = doc.get('title', '') + " " + doc.get('content', '')
            self.doc_texts.append(text)
            
        # Optimized for Thai: Using character n-grams as mentioned in README
        # Thai doesn't have spaces between words, so char n-grams (2-4) are effective
        self.vectorizer = TfidfVectorizer(
            analyzer='char', 
            ngram_range=(2, 4),
            min_df=1
        )
        
        if self.doc_texts:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.doc_texts)
        else:
            self.tfidf_matrix = None

    def retrieve(self, query, top_k=3):
        if self.tfidf_matrix is None:
            return []
            
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # Get indices of top K results
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.05: # Slight threshold
                doc = self.documents[idx].copy()
                doc['similarity'] = float(similarities[idx])
                results.append(doc)
        return results

    def generate_response(self, query):
        retrieved_docs = self.retrieve(query)
        
        if not retrieved_docs:
            return "ขออภัยค่ะ ไม่พบข้อมูลที่เกี่ยวข้องใน Agnos Health Forum โปรดลองระบุอาการให้ชัดเจนยิ่งขึ้น หรือปรึกษาแพทย์โดยตรงเพื่อความปลอดภัยนะคะ"
        
        # Construct response with sources
        response = "จากการค้นหาข้อมูลใน Agnos Health Forum พบหัวข้อที่เกี่ยวข้องดังนี้ค่ะ:\n\n"
        
        for i, doc in enumerate(retrieved_docs, 1):
            title = doc.get('title', 'หัวข้อไม่มีชื่อ')
            url = doc.get('url', '#')
            # Snippet of content
            content = doc.get('content', '')
            snippet = content[:150] + "..." if len(content) > 150 else content
            
            response += f"{i}. **{title}**\n"
            if snippet:
                response += f"   > {snippet}\n"
            response += f"   [อ่านต่อที่นี่]({url})\n\n"
            
        response += "---\n*คำเตือน: ข้อมูลนี้เป็นเพียงการรวบรวมจากฟอรัมสุขภาพ ไม่สามารถทดแทนการวินิจฉัยโดยแพทย์ได้ โปรดปรึกษาแพทย์ผู้เชี่ยวชาญผ่านแอป Agnos ค่ะ*"
        
        return response

if __name__ == "__main__":
    chatbot = AgnosChatbot()
    test_query = "หายใจหอบเหนื่อย"
    print(f"Query: {test_query}")
    print(chatbot.generate_response(test_query))
