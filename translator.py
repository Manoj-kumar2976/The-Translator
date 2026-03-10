from deep_translator import GoogleTranslator

def translate_text(text, target_language='te', source_language='auto'):
    """
    Translates text to a selected language using Google Translate.
    
    Args:
        text (str): The text to translate.
        target_language (str): Target language code (e.g., 'te' for Telugu, 'ta' for Tamil). Default is Telugu.
        source_language (str): Source language code. Default is auto-detect.
        
    Returns:
        str: The translated text.
    """
    try:
        translator = GoogleTranslator(source=source_language, target=target_language)
        translation = translator.translate(text)
        return translation
    except Exception as e:
        print(f"Error translating text: {e}")
        # In case of error (e.g. rate limit), return original text or a placeholder
        return text

import concurrent.futures

def _translate_chunk(sub_chunk, target_language):
    """Worker function to translate a chunk of subtitles together for context."""
    valid_subs = [s for s in sub_chunk if s['text'].strip()]
    if not valid_subs:
        for s in sub_chunk:
            s['translated_text'] = ''
        return sub_chunk
        
    try:
        combined_text = "\n".join([s['text'].replace('\n', ' ').strip() for s in valid_subs])
        translator = GoogleTranslator(source='auto', target=target_language)
        translated_combined = translator.translate(combined_text)
        
        translated_lines = translated_combined.split('\n')
        
        # If the translation engine kept the line count identical, it's successful
        if len(translated_lines) == len(valid_subs):
            for i, sub in enumerate(valid_subs):
                sub['translated_text'] = translated_lines[i].strip()
            # Ensure empties are handled
            for s in sub_chunk:
                if 'translated_text' not in s: 
                     s['translated_text'] = ''
            return sub_chunk
    except Exception as e:
        print(f"Error in batch translation context window: {e}. Falling back to individual translation.")
        
    # Fallback to individual line-by-line translation if the bulk translation misaligns lines or errors
    for sub in sub_chunk:
        if not sub['text'].strip():
            sub['translated_text'] = ''
            continue
        try:
            translator = GoogleTranslator(source='auto', target=target_language)
            clean_text = sub['text'].replace('\n', ' ')
            sub['translated_text'] = translator.translate(clean_text)
        except Exception as e:
            print(f"Error translating subtitle {sub['index']}: {e}")
            sub['translated_text'] = sub['text'] # fallback
            
    return sub_chunk

def translate_subtitles(subtitles, target_language='te'):
    """
    Translates a list of subtitle dictionaries concurrently in context chunks.
    
    Args:
        subtitles (list): List of dictionaries containing subtitle data.
        target_language (str): Target language code.
        
    Returns:
        list: The same list with an added 'translated_text' field for each entry.
    """
    chunk_size = 15
    chunks = [subtitles[i:i + chunk_size] for i in range(0, len(subtitles), chunk_size)]
    
    translated_subs = []
    
    print(f"Translating {len(subtitles)} subtitles in {len(chunks)} context blocks...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(_translate_chunk, list(chunk), target_language) for chunk in chunks]
        for future in concurrent.futures.as_completed(futures):
            translated_subs.extend(future.result())
            
    # Sort by index to maintain original order
    translated_subs.sort(key=lambda x: x['index'])
        
    return translated_subs

if __name__ == '__main__':
    pass
