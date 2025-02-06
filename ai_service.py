import json
import google.generativeai as genai
from config import GEMINI_API_KEY

# Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)

def generate_course_outline(topic):
    """
    Generate a structured course outline using Gemini AI.
    The response is expected to be valid JSON following the specified schema.
    
    In this updated version, each module contains lessons whose titles include the 
    original topic keyword. This is to ensure that a relevant video can be searched for each lesson.
    """
    prompt = f"""
    You are an AI that creates structured learning courses.
    Given the topic "{topic}", create a well-structured course outline with modules and lessons.
    Each lesson title must include the topic "{topic}" to ensure video relevance when searching later.
    
    The response must be in valid JSON format without any extra text.
    Use the following JSON schema:
    
    {{
      "course_title": "string",
      "modules": [
        {{
          "module_title": "string",
          "lessons": [
            {{
              "lesson_title": "string",
              "description": "string"
            }}
          ]
        }}
      ]
    }}
    
    Ensure that:
    - The course title is descriptive.
    - There are multiple modules (e.g., Module 1, Module 2, ...).
    - Each module contains 3-5 lessons.
    - Each lesson title includes the keyword "{topic}".
    - Each lesson has a short description.
    """

    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    response = model.generate_content([{"text": prompt}])
    raw_text = response.text.strip()

    # Remove Markdown code fences if present
    if raw_text.startswith("```json") and raw_text.endswith("```"):
        raw_text = raw_text[len("```json"):].rstrip("```").strip()

    # Try parsing the cleaned text as JSON
    try:
        course_outline = json.loads(raw_text)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from Gemini: {e}")
        course_outline = {"error": "Invalid JSON response", "raw_response": raw_text}
    
    return course_outline
