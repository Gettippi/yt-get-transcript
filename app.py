from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import GenericProxyConfig
import requests

app = Flask(__name__)

@app.route('/transcript', methods=['GET'])
def get_transcript():
    video_id = request.args.get('video_id')
    proxy = request.args.get('proxy')  # Get the proxy from the request

    if not video_id:
        return jsonify({'error': 'video_id is required'}), 400

    if not proxy:
        return jsonify({'error': 'proxy is required'}), 400

    try:
        # Use the custom session with youtube-transcript-api
        yt_transcript = YouTubeTranscriptApi(
            proxy_config=GenericProxyConfig(
                http_url=f"http://{proxy}",
                https_url=f"https://{proxy}",
            )
        )

        transcript = yt_transcript.get_transcript(video_id)
        return jsonify(transcript)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
