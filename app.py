from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

@app.route('/get_captions', methods=['POST'])
def get_captions():
    data = request.json
    video_url = data.get('video_url')
    proxy = data.get('proxy', None)

    if not video_url:
        return jsonify({"error": "video_url is required"}), 400
    
    if not proxy:
        return jsonify({"error": "proxy is required"}), 400

    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'subtitlesformat': 'json',
        'outtmpl': '/tmp/subtitles.json',
        'proxy': proxy,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # result = ydl.extract_info(video_url, download=False)
            # subtitles = result.get('subtitles', {})
            ydl.download([video_url])
            if os.path.exists('/tmp/subtitles.json'):
                with open('/tmp/subtitles.json', 'r') as f:
                    subtitles = f.read()
                os.remove('/tmp/subtitles.json')
                return subtitles
            else:
                return jsonify({"error": "No subtitles found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
