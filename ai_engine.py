import google.generativeai as genai
import json
import re

def generate_smart_mcqs(text, num_questions, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Bạn là chuyên gia giáo dục. Dựa vào nội dung dưới, hãy tạo {num_questions} câu trắc nghiệm khó.
        Yêu cầu bắt buộc:
        1. Trả về đúng định dạng JSON: [{"q": "...", "options": ["A. ...", ...], "answer": "...", "explanation": "..."}]
        2. KHÔNG ĐƯỢC thêm bất kỳ lời dẫn hay ký tự nào ngoài mảng JSON này.
        3. Đáp án phải có định dạng "A. Nội dung", "B. Nội dung", ...
        
        Nội dung: {text[:20000]}
        """
        
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        
        # TÌM ĐOẠN DỮ LIỆU CÓ DẤU [ và ]
        start = raw_text.find('[')
        end = raw_text.rfind(']') + 1
        
        if start != -1 and end != -1:
            clean_json = raw_text[start:end]
            return json.loads(clean_json)
        else:
            raise ValueError("Không tìm thấy cấu trúc mảng [...] trong phản hồi của AI.")

    except Exception as e:
        return {"error": f"Lỗi xử lý dữ liệu: {str(e)}"}
