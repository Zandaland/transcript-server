# transcript_server.py
"""
Flask server for YouTube transcript extraction. Deployable on Render.com.
"""
from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

app = Flask(__name__)

@app.route('/')
def home():
    return 'YouTube Transcript API Server is running.'

@app.route('/transcript', methods=['GET'])
def get_transcript():
    video_id = request.args.get('video_id')
    if not video_id:
        return jsonify({'error': 'Missing video_id'}), 400
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id)
        lines = [entry.text for entry in transcript]
        return jsonify({'transcript': lines})
    except TranscriptsDisabled:
        return jsonify({'error': 'Transcripts are disabled for this video.'}), 404
    except NoTranscriptFound:
        return jsonify({'error': 'No transcript found for this video.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
