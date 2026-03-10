import requests

url = 'http://127.0.0.1:5000/api/process-subtitles'
files = {'file': open('sample_subtitles.srt', 'rb')}
data = {
    'target_language': 'te',
    'gemini_api_key': 'AIzaSyDn-5X28XVsUgjNL7XaK_rGPsnotLF2IF8'
}

response = requests.post(url, files=files, data=data)

if response.status_code == 200:
    print("Success!")
    print(response.json())
else:
    print(f"Error {response.status_code}: {response.text}")
