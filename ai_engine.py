import google.generativeai as genai
import json

def generate_smart_mcqs(text, num_questions, api_key):
    """
    Hàm này gửi văn bản lên Google Gemini và yêu cầu trả về bộ câu hỏi hóc búa
    dưới định dạng JSON để Streamlit dễ dàng hiển thị.
    """
    try:
        # Cấu hình chìa khóa API
        genai.configure(api_key=api_key)
        
        # Sử dụng model Gemini 1.5 Flash (nhanh và thông minh)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Đây chính là "Super Prompt" để ép AI làm câu hỏi khó
        prompt = f"""
        Bạn là một giáo sư đại học khắt khe. Dựa vào văn bản dưới đây, hãy tạo ra đúng {num_questions} câu hỏi trắc nghiệm (MCQ) khó, đòi hỏi tư duy phân tích, suy luận logic chứ không chỉ copy chữ từ văn bản.
        Mỗi câu hỏi phải có 4 đáp án (chỉ 1 đáp án đúng) và 1 lời giải thích chi tiết tại sao các đáp án khác sai.
        
        BẮT BUỘC TRẢ VỀ ĐÚNG ĐỊNH DẠNG JSON DƯỚI ĐÂY (không thêm bất kỳ text nào khác, không dùng markdown ```json):
        [
          {{
            "q": "Câu hỏi suy luận...",
            "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
            "answer": "A. ...", 
            "explanation": "Giải thích chi tiết dựa trên nội dung..."
          }}
        ]
        
        VĂN BẢN BÀI HỌC:
        {text}
        """
        
        # Gửi yêu cầu lên Google
        response = model.generate_content(prompt)
        
        # Lấy kết quả và chuyển từ dạng Text sang mảng JSON (Dictionary)
        raw_text = response.text.strip()
        
        # Xử lý nếu AI lỡ trả về kèm markdown
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:-3].strip()
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:-3].strip()
            
        questions = json.loads(raw_text)
        return questions

    except Exception as e:
        return {"error": str(e)}
