import yt_dlp
import os
import uuid

def download_youtube_audio(url, output_dir='uploads'):
    """
    Downloads the audio from a YouTube video and returns the path to the downloaded audio file.
    
    Args:
        url (str): The YouTube URL.
        output_dir (str): Directory to save the file.
        
    Returns:
        dict: A dictionary containing 'audio_path', 'video_id', 'title'.
    """
    os.makedirs(output_dir, exist_ok=True)
    video_id = str(uuid.uuid4())[:8] # Generate a unique ID for the file
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, f'%(title)s_{video_id}.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False,
        'no_warnings': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading audio from: {url}")
            info_dict = ydl.extract_info(url, download=True)
            title = info_dict.get('title', 'Unknown Title')
            
            # The postprocessor changes the extension to mp3
            expected_filename = f"{title}_{video_id}.mp3"
            # Ensure safe filename matching yt-dlp's sanitize
            safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
            # It's more reliable to let yt-dlp tell us the final file path or search for the mp3
            
            # Let's find the exact mp3 file in the directory that ends with our unique ID
            downloaded_file = None
            for file in os.listdir(output_dir):
                if file.endswith(f"_{video_id}.mp3"):
                    downloaded_file = os.path.join(output_dir, file)
                    break
                    
            if not downloaded_file:
                 raise Exception("Could not find the downloaded audio file.")
                 
            print(f"Successfully downloaded audio to: {downloaded_file}")
            return {
                'audio_path': downloaded_file,
                'video_id': video_id,
                'title': title
            }
            
    except Exception as e:
        print(f"Error downloading YouTube audio: {e}")
        raise e

def download_youtube_video(url, output_dir='uploads'):
    """
    Downloads the best video stream from a YouTube video for preview purposes.
    
    Args:
        url (str): The YouTube URL.
        output_dir (str): Directory to save the file.
        
    Returns:
        str: The path to the downloaded video file.
    """
    os.makedirs(output_dir, exist_ok=True)
    video_id = str(uuid.uuid4())[:8]
    
    # Download video in mp4 format, capped at 360p max for MUCH faster downloading
    ydl_opts = {
        'format': 'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]/best',
        'outtmpl': os.path.join(output_dir, f'video_{video_id}.%(ext)s'),
        'quiet': False,
        'no_warnings': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading video from: {url}")
            info_dict = ydl.extract_info(url, download=True)
            
            downloaded_file = None
            for file in os.listdir(output_dir):
                if file.startswith(f"video_{video_id}"):
                    downloaded_file = os.path.join(output_dir, file)
                    break
                    
            if not downloaded_file:
                 raise Exception("Could not find the downloaded video file.")
                 
            return downloaded_file
            
    except Exception as e:
        print(f"Error downloading YouTube video: {e}")
        raise e

if __name__ == "__main__":
    pass
