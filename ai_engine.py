from google import genai
import json
import re

def generate_smart_mcqs(text, num_questions, api_key):
    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        You are an educational expert. Create exactly {num_questions} difficult multiple-choice questions (MCQs) from the provided text.
        Each question must have 4 options (A, B, C, D) and 1 detailed explanation.
        
        YOU MUST RETURN ONLY A VALID JSON ARRAY OF OBJECTS, WITH NO ADDITIONAL TEXT OR MARKDOWN:
        [
          {{
            "q": "Question text here?", 
            "options": ["A. Option 1", "B. Option 2", "C. Option 3", "D. Option 4"], 
            "answer": "A. Option 1", 
            "explanation": "Detailed explanation here..."
          }}
        ]
        
        Text material: 
        {text[:15000]}
        """
        
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt
        )
        raw_text = response.text.strip()
        
        json_match = re.search(r'\[.*\]', raw_text, re.DOTALL)
        if json_match:
            json_text = json_match.group(0)
            data = json.loads(json_text)
            
            if isinstance(data, list) and len(data) > 0:
                if isinstance(data[0], str):
                    return {"error": "AI returned an array of strings instead of objects. Please try again with fewer questions."}
                elif isinstance(data[0], dict):
                    return data 
            
            return {"error": "Invalid data structure returned by AI."}
        else:
            return {"error": "Could not find JSON format in AI response."}

    except json.JSONDecodeError:
         return {"error": "AI returned malformed JSON. Please generate again."}
    except Exception as e:
        return {"error": f"AI System Error: {str(e)}"}
