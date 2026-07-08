from google import genai
import json
import re

def generate_smart_mcqs(text, num_questions, api_key):
    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        You are an expert academic tutor. Extract deep conceptual knowledge from the text.
        CRITICAL RULES:
        1. DO NOT reference slides, images, or document structure.
        2. Focus on core concepts, logic, and cause-and-effect.
        3. Create {num_questions} difficult multiple-choice questions.
        4. Each question must have 4 options and a detailed explanation.
        
        RETURN ONLY A VALID JSON ARRAY OF OBJECTS, WITH NO ADDITIONAL TEXT OR MARKDOWN:
        [
          {{"q": "Question text?", "options": ["A. ...", "B. ...", "C. ...", "D. ..."], "answer": "A. ...", "explanation": "..."}}
        ]
        
        Text material: 
        {text[:15000]}
        """
        
        response = client.models.generate_content(
            model='gemini-3.5-flash',
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
