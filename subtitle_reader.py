import pysrt

def read_subtitles(file_path):
    """
    Reads a subtitle file (.srt) and extracts information.
    
    Args:
        file_path (str): The path to the .srt file.
        
    Returns:
        list: A list of dictionaries containing 'index', 'start', 'end', and 'text' for each subtitle.
    """
    try:
        subs = pysrt.open(file_path)
        extracted_subs = []
        for index, sub in enumerate(subs):
            # sub.start and sub.end give the timestamp. We can convert to total seconds.
            start_time = sub.start.ordinal / 1000.0 # ordinal is total milliseconds
            end_time = sub.end.ordinal / 1000.0
            extracted_subs.append({
                'index': index + 1,
                'start': start_time,
                'end': end_time,
                'text': sub.text
            })
        return extracted_subs
    except Exception as e:
        print(f"Error reading subtitle file: {e}")
        return []

if __name__ == '__main__':
    # Simple test if run directly
    pass
