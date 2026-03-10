import os
import shutil
from flask import Flask, render_template, request, jsonify, url_for

# Automatically setup ffmpeg and ffprobe paths for yt-dlp and whisper
import static_ffmpeg
static_ffmpeg.add_paths()

from subtitle_reader import read_subtitles
from translator import translate_subtitles
from tts import process_tts_for_subtitles
from youtube_extractor import download_youtube_audio, download_youtube_video
from speech_to_text import generate_subtitles_from_audio

app = Flask(__name__)
# Configurations
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB max

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join('static', 'audio'), exist_ok=True)

@app.route('/')
def index():
    """Renders the main homepage."""
    return render_template('index.html')

@app.route('/api/process-subtitles', methods=['POST'])
def process_subtitles():
    """
    API endpoint to handle a YouTube URL, download the audio, transcribe it,
    translate the text, generate TTS audio, and download the video for playback.
    """
    youtube_url = request.form.get('youtube_url', '').strip()
    if not youtube_url:
        return jsonify({'error': 'No YouTube URL provided'}), 400
        
    target_lang = request.form.get('target_language', 'te')
    
    # Clear out old files to save space
    audio_dir = os.path.join('static', 'audio')
    video_dir = os.path.join('static', 'videos')
    
    if os.path.exists(audio_dir):
        shutil.rmtree(audio_dir)
    os.makedirs(audio_dir, exist_ok=True)
    
    if os.path.exists(video_dir):
        shutil.rmtree(video_dir)
    os.makedirs(video_dir, exist_ok=True)
    
    try:
        # 1. Download YouTube Audio
        print("Starting YouTube Audio Download...")
        audio_info = download_youtube_audio(youtube_url, output_dir=app.config['UPLOAD_FOLDER'])
        audio_path = audio_info['audio_path']
        
        # 2. Transcribe Audio (Speech-to-Text)
        print("Starting Speech-to-Text transcription...")
        subs = generate_subtitles_from_audio(audio_path, model_size='base')
        
        if not subs:
            return jsonify({'error': 'No speech detected or transcription failed.'}), 400
            
        # 3. Translate subtitles
        print("Translating subtitles...")
        translated_subs = translate_subtitles(subs, target_language=target_lang)
        
        # Removed dynamic voice gender integration as requested
        print("Assigning default voice...")
        for sub in translated_subs:
             sub['gender'] = 'F'
        
        # 4. Generate TTS 
        print("Generating TTS...")
        processed_subs = process_tts_for_subtitles(translated_subs, language=target_lang, output_dir=audio_dir)
        
        # 5. Download Video for Preview
        print("Downloading Video for preview...")
        video_path = download_youtube_video(youtube_url, output_dir=video_dir)
        
        # Extract just the static relative path for the frontend
        # e.g., 'static\videos\video_xyz.mp4' -> 'videos/video_xyz.mp4'
        static_video_path = os.path.relpath(video_path, 'static').replace('\\', '/')
        
        return jsonify({
            'success': True, 
            'subtitles': processed_subs,
            'video_file': static_video_path,
            'message': 'YouTube video processed successfully!'
        })
        
    except Exception as e:
         import traceback
         traceback.print_exc()
         return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)
