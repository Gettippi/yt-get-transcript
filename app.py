from flask import Flask, request, jsonify
import yt_dlp
import os
import requests
import re
from typing import List
import io
import webvtt


https_pattern = re.compile(
    r'https://'  # https:// at the beginning
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain name, simplified
    r'(?:[A-Z0-9-]{2,})\.[A-Z]{2,6})'  # domain name, basic
    r'(?:[/?][^\s]*)', re.IGNORECASE)  # optional path and query parameters

def find_https_urls(text: str) -> List[str]:
    return https_pattern.findall(text)



app = Flask(__name__)

@app.route('/get_captions', methods=['POST'])
def get_captions():
    data = request.json
    video_url = data.get('video_url')
    proxy = data.get('proxy')

    if not video_url:
        return jsonify({"error": "video_url is required"}), 400

    if proxy:
        proxies = {'http': proxy, 'https': proxy}
    else:
        proxies = None

    ydl_opts = {
        'cachedir': False,
        'quiet': True,
        'proxy': proxy,
        'source_address': '0.0.0.0'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            subtitles_link = next(
                (sub.get("url") for sub in info_dict.get("automatic_captions", {}).get("eng-orig", []) if sub.get("ext") == "vtt"),
                None
            )

            if not subtitles_link:
                return jsonify({"error": "No VTT subtitles found"}), 404

            captions_lang, captions_raw = extract_captions(subtitles_link, proxies)
            return jsonify({"captions": captions_lang, "captions_raw": captions_raw}), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Network error: {str(e)}"}), 500
    except yt_dlp.utils.DownloadError as e:
        return jsonify({"error": f"Download error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

def extract_captions(subtitles_link, proxies):
    vtt_urls = find_https_urls(subtitles_link)
    if not vtt_urls:
        vtt_urls = [subtitles_link]

    captions_lang = []
    captions_raw = []

    for url in vtt_urls:
        vtt_response = requests.get(url, proxies=proxies)
        vtt_response.raise_for_status()
        vtt_content = io.StringIO(vtt_response.text)

        for caption in webvtt.read_buffer(vtt_content):
            if '\n' not in caption.text:
                captions_lang.append(caption.text)
                captions_raw.append({'start': caption.start_in_seconds, 'end': caption.end_in_seconds, 'text': caption.text})

    return captions_lang, captions_raw


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
