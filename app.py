from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import requests

app = Flask(__name__)

@app.route('/transcript', methods=['GET'])
def get_transcript():
    video_id = request.args.get('video_id')
    proxy = request.args.get('proxy')  # Get the proxy from the request

    if not video_id:
        return jsonify({'error': 'video_id is required'}), 400

    # Prepare the proxy configuration
    proxies = None
    if proxy:
        proxies = {
            'http': proxy,
            'https': proxy,
        }

    try:
        # Create a custom session with the proxy
        session = requests.Session()
        if proxies:
            session.proxies.update(proxies)

        # Use the custom session with youtube-transcript-api
        transcript = YouTubeTranscriptApi.get_transcript(video_id, http_client=session)
        return jsonify(transcript)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
