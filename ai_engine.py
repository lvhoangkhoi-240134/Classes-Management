import google.generativeai as genai
import json
import re

def generate_smart_mcqs(text, num_questions, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Bạn là một chuyên gia giáo dục. Hãy tạo ra đúng {num_questions} câu hỏi trắc nghiệm (MCQ) khó từ văn bản này.
        Mỗi câu phải có 4 đáp án (A, B, C, D) và 1 giải thích chi tiết.
        
        BẮT BUỘC TRẢ VỀ ĐÚNG DẠNG JSON MẢNG (LIST) CHỨA CÁC OBJECT, KHÔNG THÊM TEXT BÊN NGOÀI:
        [
          {{
            "q": "Nội dung câu hỏi?", 
            "options": ["A. Đáp án 1", "B. Đáp án 2", "C. Đáp án 3", "D. Đáp án 4"], 
            "answer": "A. Đáp án 1", 
            "explanation": "Giải thích chi tiết..."
          }}
        ]
        
        Văn bản bài học: 
        {text[:15000]}
        """
        
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        
        # Cứu tinh 1: Tìm đúng mảng JSON bằng Regex
        json_match = re.search(r'\[.*\]', raw_text, re.DOTALL)
        if json_match:
            json_text = json_match.group(0)
            data = json.loads(json_text)
            
            # Cứu tinh 2: Ngăn chặn lỗi TypeError (string indices must be integers)
            if isinstance(data, list) and len(data) > 0:
                if isinstance(data[0], str):
                    return {"error": "AI trả về mảng chuỗi thay vì mảng dữ liệu. Vui lòng thử lại với số lượng câu hỏi ít hơn."}
                elif isinstance(data[0], dict):
                    return data # Trả về mảng chuẩn
            
            return {"error": "Cấu trúc dữ liệu AI trả về không hợp lệ."}
        else:
            return {"error": "Không tìm thấy định dạng JSON trong câu trả lời của AI."}

    except json.JSONDecodeError:
         return {"error": "AI trả về JSON bị lỗi cú pháp. Vui lòng Generate lại."}
    except Exception as e:
        return {"error": f"Lỗi hệ thống AI: {str(e)}"}
