import google.generativeai as genai
import json

def analyze_subtitle_genders(subtitles, api_key):
    """
    Uses Gemini API to predict the gender (M/F) of the speaker for each subtitle line.
    
    Args:
        subtitles (list): List of subtitle dicts (index, start, end, text).
        api_key (str): Google Gemini API Key.
        
    Returns:
        dict: A mapping of subtitle index (int) to gender ('M' or 'F').
    """
    if not api_key:
        print("No Gemini API key provided. Defaulting all genders to Female.")
        return {sub['index']: 'F' for sub in subtitles}
        
    try:
        genai.configure(api_key=api_key)
        
        # We use the fast flash model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Format the context for the AI
        transcript = ""
        for sub in subtitles:
            transcript += f"[{sub['index']}] {sub['text'].replace(chr(10), ' ')}\n"
            
        prompt = f"""
        You are an AI tasked with determining the gender of the speaker for each line in a video transcript.
        Analyze the following chronological transcript and infer if the speaker is Male (M) or Female (F) based on context, conversational cues, or general probabilities.
        
        Transcript:
        {transcript}
        
        Respond ONLY with a valid JSON object mapping the index to the gender 'M' or 'F'.
        Example format:
        {{
            "1": "M",
            "2": "F",
            "3": "M"
        }}
        """
        
        response = model.generate_content(prompt)
        # Parse out JSON from markdown block if present
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3]
        elif text.startswith("```"):
            text = text[3:-3]
            
        gender_mapping_str = json.loads(text)
        
        # Convert string keys back to int
        gender_mapping = {int(k): v for k, v in gender_mapping_str.items()}
        
        # Fallback for any missing indices
        for sub in subtitles:
            if sub['index'] not in gender_mapping:
                gender_mapping[sub['index']] = 'F'
                
        return gender_mapping
        
    except Exception as e:
        print(f"Error during Gemini API gender analysis: {e}")
        # Default all to Female if API fails
        return {sub['index']: 'F' for sub in subtitles}
