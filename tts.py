import os
import concurrent.futures
import asyncio
import asyncio
import edge_tts
from gtts import gTTS

# Voice mapping based on language and gender
# fallback to default edge-tts language strings if exact gender match isn't available
VOICE_MAP = {
    'te': {'M': 'te-IN-MohanNeural', 'F': 'te-IN-ShrutiNeural'},
    'hi': {'M': 'hi-IN-MadhurNeural', 'F': 'hi-IN-SwaraNeural'},
    'ta': {'M': 'ta-IN-ValluvarNeural', 'F': 'ta-IN-PallaviNeural'},
    'ml': {'M': 'ml-IN-MidhunNeural', 'F': 'ml-IN-SobhanaNeural'},
    'kn': {'M': 'kn-IN-GaganNeural', 'F': 'kn-IN-SapnaNeural'},
    'es': {'M': 'es-ES-AlvaroNeural', 'F': 'es-ES-ElviraNeural'},
    'fr': {'M': 'fr-FR-HenriNeural', 'F': 'fr-FR-DeniseNeural'},
    'en': {'M': 'en-US-GuyNeural', 'F': 'en-US-AriaNeural'}
}

async def generate_speech_async(text, voice, output_path):
    """Async generation of speech via edge-tts."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def generate_speech(text, language='te', gender='F', output_path='output.mp3'):
    """
    Converts translated text into speech using Edge TTS.
    Selects voice based on language and gender ('M' or 'F').
    """
    try:
        if not text.strip():
            return None
            
        # Select the correct voice string
        lang_voices = VOICE_MAP.get(language, VOICE_MAP['en']) # default to en if missing
        voice = lang_voices.get(gender, lang_voices['F'])
            
        asyncio.run(generate_speech_async(text, voice, output_path))
        return output_path
    except Exception as edge_err:
        print(f"Edge TTS failed with error: {edge_err}. Falling back to gTTS...")
        try:
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(output_path)
            return output_path
        except Exception as e:
            print(f"Error generating speech after fallback: {e}")
            return None

def _process_single_tts(sub_dict, language, output_dir):
    """Worker function to generate TTS for a single subtitle."""
    filename = f"sub_{sub_dict['index']}.mp3"
    filepath = os.path.join(output_dir, filename)
    
    sub_dict['audio_file'] = None
    text_to_speak = sub_dict.get('translated_text', '')
    gender = sub_dict.get('gender', 'F')
    
    if text_to_speak.strip():
        saved_path = generate_speech(text_to_speak, language=language, gender=gender, output_path=filepath)
        if saved_path:
            sub_dict['audio_file'] = f"audio/{filename}"
            
    return sub_dict

def process_tts_for_subtitles(subtitles, language='te', output_dir='static/audio'):
    """
    Generates individual audio files for each translated subtitle concurrently.
    
    Args:
        subtitles (list): List of subtitle dicts with 'translated_text'.
        language (str): Target language code.
        output_dir (str): Directory to save the audio files.
        
    Returns:
        list: The subtitles list with 'audio_path' appended.
    """
    os.makedirs(output_dir, exist_ok=True)
    processed_subs = []
    
    print(f"Generating TTS for {len(subtitles)} subtitles...")
    # Use fewer workers for TTS to avoid rate limiting from Google TTS
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(_process_single_tts, dict(sub), language, output_dir) for sub in subtitles]
        for future in concurrent.futures.as_completed(futures):
            processed_subs.append(future.result())
            
    # Sort to maintain original indexing
    processed_subs.sort(key=lambda x: x['index'])
        
    return processed_subs
    
