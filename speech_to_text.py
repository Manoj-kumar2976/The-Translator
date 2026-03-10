import whisper
import os

def generate_subtitles_from_audio(audio_path, model_size='base'):
    """
    Uses OpenAI's Whisper model to transcribe an audio file into precise subtitles with timestamps.
    
    Args:
        audio_path (str): The path to the audio file.
        model_size (str): The Whisper model size ('tiny', 'base', 'small', 'medium', 'large').
        
    Returns:
        list: A list of subtitle dictionaries compatible with the translation pipeline.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found at {audio_path}")
        
    print(f"Loading Whisper model '{model_size}'...")
    # Load the model. The 'base' model requires about 1GB of VRAM/RAM and is decently fast.
    try:
        model = whisper.load_model(model_size)
    except Exception as e:
        print(f"Error loading Whisper model: {e}")
        raise e
        
    print(f"Transcribing audio file: {audio_path}")
    # Perform transcription
    result = model.transcribe(audio_path, verbose=False)
    
    # Extract segments to form our subtitle dictionary format
    subtitles = []
    
    for idx, segment in enumerate(result['segments']):
        # Whisper segments usually contain id, seek, start, end, text, tokens, etc.
        sub_dict = {
            'index': idx + 1,
            'start': segment['start'], # Float representing seconds
            'end': segment['end'],     # Float representing seconds
            'text': segment['text'].strip()
        }
        subtitles.append(sub_dict)
        
    print(f"Successfully generated {len(subtitles)} subtitle segments.")
    return subtitles

if __name__ == "__main__":
    pass
