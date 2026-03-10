from subtitle_reader import read_subtitles
from translator import translate_subtitles
from tts import process_tts_for_subtitles

print("Reading...")
subs = read_subtitles('sample_subtitles.srt')
print(f"Read {len(subs)} subtitles.")

print("Translating...")
translated = translate_subtitles(subs, 'te')
print("Translated.")

print("TTS...")
processed = process_tts_for_subtitles(translated, 'te', 'static/audio')
print("Done TTS.")
print(processed)
