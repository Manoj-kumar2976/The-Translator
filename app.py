import os
import shutil
from flask import Flask, render_template, request, jsonify


from subtitle_reader import read_subtitles
from translator import translate_subtitles
from tts import process_tts_for_subtitles
from youtube_extractor import download_youtube_audio, download_youtube_video
from speech_to_text import generate_subtitles_from_audio

app = Flask(__name__)

# Configurations
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join('static', 'audio'), exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/process-subtitles', methods=['POST'])
def process_subtitles():

    youtube_url = request.form.get('youtube_url', '').strip()

    if not youtube_url:
        return jsonify({'error': 'No YouTube URL provided'}), 400

    target_lang = request.form.get('target_language', 'te')

    audio_dir = os.path.join('static', 'audio')
    video_dir = os.path.join('static', 'videos')

    # Clean folders
    if os.path.exists(audio_dir):
        shutil.rmtree(audio_dir)
    os.makedirs(audio_dir, exist_ok=True)

    if os.path.exists(video_dir):
        shutil.rmtree(video_dir)
    os.makedirs(video_dir, exist_ok=True)

    try:

        # 1️⃣ Download YouTube audio
        print("Downloading audio...")
        audio_info = download_youtube_audio(
            youtube_url,
            output_dir=app.config['UPLOAD_FOLDER']
        )

        audio_path = audio_info['audio_path']

        # 2️⃣ Speech to text
        print("Generating subtitles...")
        subs = generate_subtitles_from_audio(audio_path, model_size='base')

        if not subs:
            return jsonify({
                'error': 'No speech detected'
            }), 400

        # 3️⃣ Translate subtitles
        print("Translating...")
        translated_subs = translate_subtitles(
            subs,
            target_language=target_lang
        )

        # Default voice
        for sub in translated_subs:
            sub['gender'] = 'F'

        # 4️⃣ Generate TTS
        print("Generating voice...")
        processed_subs = process_tts_for_subtitles(
            translated_subs,
            language=target_lang,
            output_dir=audio_dir
        )

        # 5️⃣ Download video preview
        print("Downloading video...")
        video_path = download_youtube_video(
            youtube_url,
            output_dir=video_dir
        )

        static_video_path = os.path.relpath(video_path, 'static').replace('\\', '/')

        return jsonify({
            "success": True,
            "subtitles": processed_subs,
            "video_file": static_video_path,
            "message": "Video processed successfully"
        })

    except Exception as e:
        import traceback
        traceback.print_exc()

        return jsonify({
            "error": str(e)
        }), 500
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)