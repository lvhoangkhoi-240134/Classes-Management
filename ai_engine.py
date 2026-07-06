import google.generativeai as genai
import json
import re

def generate_smart_mcqs(text, num_questions, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Bạn là một chuyên gia giáo dục. Hãy tạo ra đúng {num_questions} câu hỏi trắc nghiệm (MCQ) khó từ văn bản này.
        Mỗi câu phải có 4 đáp án (A, B, C, D) và 1 giải thích.
        
        TRẢ VỀ ĐÚNG DẠNG JSON (không thêm text ngoài):
        [
          {{"q": "Câu hỏi?", "options": ["A. ...", "B. ...", "C. ...", "D. ..."], "answer": "A. ...", "explanation": "..."}}
        ]
        
        Văn bản: {text[:15000]} 
        """
        
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        
        # CHỖ NÀY LÀ CỨU TINH: Dùng Regex tìm đoạn JSON trong phản hồi
        json_match = re.search(r'\[.*\]', raw_text, re.DOTALL)
        if json_match:
            json_text = json_match.group(0)
            return json.loads(json_text)
        else:
            # Nếu không tìm thấy JSON, ném lỗi để app biết
            raise ValueError("AI did not return valid JSON format.")

    except Exception as e:
        return {"error": f"AI Parsing Error: {str(e)}"}
