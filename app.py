from flask import Flask, jsonify, request  # type: ignore
from flask_cors import CORS # type: ignore
from googleapiclient.discovery import build
import re
import emoji
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt # type: ignore
import io
import base64

app = Flask(__name__)
CORS(app)

API_KEY = 'AIzaSyCpjIdSNvjvsfW8kferxS2-ov93DtpD3PU'
youtube = build('youtube', 'v3', developerKey=API_KEY)

@app.route('/api/comments/<path:video_url>', methods=['GET'])
def get_comments(video_url):
    if not video_url:
        return jsonify({"error": "No video URL provided"}), 400
    
    video_id = video_url[-11:]
    if len(video_id) != 11:
        return jsonify({"error": "Invalid video URL format"}), 400
    
    try:
        video_response = youtube.videos().list(
            part='snippet',
            id=video_id
        ).execute()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    video_snippet = video_response['items'][0]['snippet']
    uploader_channel_id = video_snippet['channelId']
    video_title = video_snippet['title']
    
    comments = []
    nextPageToken = None
    while len(comments) < 600:
        request = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=100,
            pageToken=nextPageToken
        )
        response = request.execute()
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            if comment['authorChannelId']['value'] != uploader_channel_id:
                comments.append(comment['textDisplay'])
        nextPageToken = response.get('nextPageToken')
        if not nextPageToken:
            break
    
    hyperlink_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    threshold_ratio = 0.65
    relevant_comments = []
    
    for comment_text in comments:
        comment_text = comment_text.lower().strip()
        emojis = emoji.emoji_count(comment_text)
        text_characters = len(re.sub(r'\s', '', comment_text))
        if (any(char.isalnum() for char in comment_text)) and not hyperlink_pattern.search(comment_text):
            if emojis == 0 or (text_characters / (text_characters + emojis)) > threshold_ratio:
                relevant_comments.append(comment_text)
    
    sentiment_object = SentimentIntensityAnalyzer()
    polarity = []
    positive_comments = []
    negative_comments = []
    neutral_comments = []
    
    for items in relevant_comments:
        sentiment_dict = sentiment_object.polarity_scores(items)
        polarity.append(sentiment_dict['compound'])
        if sentiment_dict['compound'] > 0.05:
            positive_comments.append(items)
        elif sentiment_dict['compound'] < -0.05:
            negative_comments.append(items)
        else:
            neutral_comments.append(items)
    
    avg_polarity = sum(polarity)/len(polarity) if polarity else 0
    positive_count = len(positive_comments)
    negative_count = len(negative_comments)
    neutral_count = len(neutral_comments)
    
    labels = ['Positive', 'Negative', 'Neutral']
    comment_counts = [positive_count, negative_count, neutral_count]
    
    fig, ax = plt.subplots()
    ax.bar(labels, comment_counts, color=['blue', 'red', 'grey'])
    ax.set_xlabel('Sentiment')
    ax.set_ylabel('Comment Count')
    ax.set_title('Sentiment Analysis of Comments')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()

    response_data = {
        'title': video_title,
        'average_polarity': avg_polarity,
        'positive_comments_count': positive_count,
        'negative_comments_count': negative_count,
        'neutral_comments_count': neutral_count,
        'chart': img_str
    }
    
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)

