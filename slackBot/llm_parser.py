import os
import json
from datetime import datetime, timedelta
import re

def parse_task(raw_text):
    """
    Parse natural language task using OpenAI API or fallback to stub
    """
    try:
        # Try to use OpenAI API if available
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            return parse_with_openai(raw_text, api_key)
        else:
            print("[LLM] No OpenAI API key found, using stub parser")
            return parse_with_stub(raw_text)
    except Exception as e:
        print(f"[LLM] Error parsing with OpenAI: {e}")
        print("[LLM] Falling back to stub parser")
        return parse_with_stub(raw_text)

def parse_with_openai(raw_text, api_key):
    """
    Parse task using OpenAI API
    """
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        
        prompt = f"""
        Extract the following fields from this task instruction:
        - recipient: The person who should perform the task
        - task: The actual task to be performed
        - due_date: When the task should be done (in ISO format)
        - response_required: Whether a response is needed (true/false)
        - output: What output is expected (e.g., summary, confirmation, etc.)

        Input: "{raw_text}"

        Return only a valid JSON object with these fields.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Validate and clean the result
        return validate_and_clean_parsed_task(result, raw_text)
        
    except Exception as e:
        raise Exception(f"OpenAI API error: {e}")

def parse_with_stub(raw_text):
    """
    Fallback stub parser with basic pattern matching
    """
    # Basic pattern matching for common task formats
    text_lower = raw_text.lower()
    
    # Extract recipient (look for names after "remind", "ask", "tell")
    recipient = "Unknown"
    words = raw_text.split()
    
    # Look for patterns like "remind [name]", "ask [name]", "tell [name]"
    for i, word in enumerate(words):
        if word.lower() in ["remind", "ask", "tell"] and i + 1 < len(words):
            recipient = words[i + 1]
            break
    
    # Extract task (everything between recipient and date/time indicators)
    task = raw_text
    date_indicators = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", 
                      "today", "tomorrow", "next", "yesterday", "friday", "saturday", "sunday"]
    
    for indicator in date_indicators:
        if indicator in text_lower:
            parts = text_lower.split(indicator)
            if len(parts) > 1:
                task = parts[0].strip()
                break
    
    # Determine due date (simplified)
    due_date = datetime.now() + timedelta(days=1)  # Default to tomorrow
    if "yesterday" in text_lower:
        due_date = datetime.now() - timedelta(days=1)
    elif "today" in text_lower:
        due_date = datetime.now()
    elif "tomorrow" in text_lower:
        due_date = datetime.now() + timedelta(days=1)
    elif "friday" in text_lower:
        due_date = datetime.now() + timedelta(days=(4 - datetime.now().weekday()) % 7)
    elif "monday" in text_lower:
        due_date = datetime.now() + timedelta(days=(7 - datetime.now().weekday()) % 7)
    elif "next" in text_lower and "monday" in text_lower:
        due_date = datetime.now() + timedelta(days=(7 - datetime.now().weekday()) % 7 + 7)
    elif "next" in text_lower and "friday" in text_lower:
        due_date = datetime.now() + timedelta(days=(4 - datetime.now().weekday()) % 7 + 7)
    
    # Check if response is required
    response_required = any(word in text_lower for word in ["summarize", "reply", "response", "confirm"])
    
    # Determine output format
    output = "confirmation"
    if "summarize" in text_lower:
        output = "summary"
    
    return {
        "recipient": recipient,
        "task": task,
        "due_date": due_date.isoformat(),
        "response_required": response_required,
        "output": output
    }

def validate_and_clean_parsed_task(parsed, original_text):
    """
    Validate and clean the parsed task data
    """
    required_fields = ["recipient", "task", "due_date", "response_required", "output"]
    
    # Ensure all required fields are present
    for field in required_fields:
        if field not in parsed:
            print(f"[LLM] Missing field: {field}, using default")
            if field == "recipient":
                parsed[field] = "Unknown"
            elif field == "task":
                parsed[field] = original_text
            elif field == "due_date":
                parsed[field] = (datetime.now() + timedelta(days=1)).isoformat()
            elif field == "response_required":
                parsed[field] = False
            elif field == "output":
                parsed[field] = "confirmation"
    
    # Clean and validate the data
    parsed["recipient"] = str(parsed["recipient"]).strip()
    parsed["task"] = str(parsed["task"]).strip()
    parsed["response_required"] = bool(parsed["response_required"])
    parsed["output"] = str(parsed["output"]).strip()
    
    # Validate date format
    try:
        datetime.fromisoformat(parsed["due_date"].replace('Z', '+00:00'))
    except:
        print("[LLM] Invalid date format, using tomorrow")
        parsed["due_date"] = (datetime.now() + timedelta(days=1)).isoformat()
    
    return parsed 