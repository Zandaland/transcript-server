# transcript_server.py
"""
Flask server for YouTube transcript extraction. Deployable on Render.com.
"""
from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from youtube_transcript_api.proxies import GenericProxyConfig
import requests
import os

app = Flask(__name__)

# CORS headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/')
def home():
    return 'YouTube Transcript API Server is running.'

@app.route('/transcript', methods=['GET'])
def get_transcript():
    video_id = request.args.get('video_id')
    if not video_id:
        return jsonify({'error': 'Missing video_id'}), 400
    
    try:
        # Try with custom session, user agent, and optional proxy
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        # Optional proxy support via env var, e.g. socks5h://tor:9050 or http://user:pass@host:port
        proxy_url = os.getenv('PROXY_URL')
        if proxy_url:
            session.proxies.update({'http': proxy_url, 'https': proxy_url})

        ytt_api = YouTubeTranscriptApi(http_client=session)
        transcript = ytt_api.fetch(video_id)
        lines = [entry.text for entry in transcript]
        return jsonify({'transcript': lines})
    except TranscriptsDisabled:
        return jsonify({'error': 'Transcripts are disabled for this video.'}), 404
    except NoTranscriptFound:
        return jsonify({'error': 'No transcript found for this video.'}), 404
    except Exception as e:
        error_msg = str(e)
        if 'blocking requests from your IP' in error_msg:
            return jsonify({'error': 'YouTube is blocking requests from this server. Try using the extension\'s built-in extraction or a different video.'}), 429
        return jsonify({'error': error_msg}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
