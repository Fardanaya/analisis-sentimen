import json
import pandas as pd
import re
import sys
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
def simple_tokenize(text):
    return [word.strip() for word in re.split(r'\s+|[\.,!?;\n]', text.lower()) if word.strip()]

# Load sentiment dictionary from positive.tsv and negative.tsv
def load_sentiment_dict():
    sentiment_dict = {}

    # Load positive words
    with open('positive.tsv', 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                word = parts[0].lower().strip()
                try:
                    score = float(parts[1])
                    sentiment_dict[word] = score
                except ValueError:
                    continue  # Skip if not a number

    # Load negative words
    with open('negative.tsv', 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                word = parts[0].lower().strip()
                try:
                    score = float(parts[1])
                    sentiment_dict[word] = score
                except ValueError:
                    continue  # Skip if not a number

    return sentiment_dict

# Load comments from JSON
def load_youtube_comments(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    comments = []
    for item in data:
        for comment_data in item['comments']:
            comments.append(comment_data['comment'])

    return comments, data

def load_tweet_comments(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    comments = []
    for tweet in data:
        comments.append(tweet['text'])

    return comments, data

# Preprocessing: Tokenize, stem, and clean
def preprocess_text(text, stemmer):
    # Remove special characters and numbers
    text = re.sub(r'[^\w\s]', '', text.lower())

    # Tokenize
    tokens = simple_tokenize(text)

    # Stemming
    stemmed_tokens = [stemmer.stem(token) for token in tokens]

    return stemmed_tokens

# Analyze sentiment for each token using custom dictionary scores
def analyze_sentiment(tokens, sentiment_dict):
    total_score = 0.0
    positive_score = 0.0
    negative_score = 0.0
    found_tokens = 0

    sentiment_details = []

    for token in tokens:
        score = sentiment_dict.get(token.lower(), 0.0)  # Default to 0.0 for neutral
        if score != 0.0:
            found_tokens += 1

        total_score += score

        if score > 0:
            positive_score += score
            sentiment_details.append({'token': token, 'score': score, 'sentiment': 'positive'})
        elif score < 0:
            negative_score += abs(score)  # Store absolute value for negative
            sentiment_details.append({'token': token, 'score': score, 'sentiment': 'negative'})
        else:
            sentiment_details.append({'token': token, 'score': score, 'sentiment': 'neutral'})

    return total_score, positive_score, negative_score, sentiment_details, found_tokens

# Determine overall sentiment based on total score
def overall_sentiment(total_score):
    if total_score > 0.1:
        return 'positive'
    elif total_score < -0.1:
        return 'negative'
    else:
        return 'neutral'

# Main function
def main():
    if len(sys.argv) < 2:
        print("Usage: python sentiment_analysis.py <source>")
        print("Sources: youtube, twitter")
        sys.exit(1)

    source = sys.argv[1].lower()

    # Initialize stemmer
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()

    # Load sentiment dictionary
    sentiment_dict = load_sentiment_dict()

    # Load comments based on source
    if source == 'youtube':
        print("Loading YouTube comments...")
        comments, data = load_youtube_comments('youtube_sound_horeg_comments.json')
        source_name = "YouTube"
    elif source == 'twitter':
        print("Loading Twitter comments...")
        comments, data = load_tweet_comments('hasil_tweet_sound_horeg.json')
        source_name = "Twitter"
    else:
        print("Invalid source. Use 'youtube' or 'twitter'")
        sys.exit(1)

    # Process each comment
    results = []
    for comment in comments:
        tokens = preprocess_text(comment, stemmer)
        total_score, positive_score, negative_score, sentiment_details, found_tokens = analyze_sentiment(tokens, sentiment_dict)
        overall = overall_sentiment(total_score)

        result = {
            'comment': comment,
            'tokens': tokens,
            'total_score': total_score,
            'positive_score': positive_score,
            'negative_score': negative_score,
            'sentiment_details': sentiment_details,
            'found_sentiment_tokens': found_tokens,
            'overall_sentiment': overall
        }
        results.append(result)

    # Save to JSON
    with open('sentiment_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    # Count overall sentiment distribution
    sentiment_count = {
        'positive': sum(1 for r in results if r['overall_sentiment'] == 'positive'),
        'negative': sum(1 for r in results if r['overall_sentiment'] == 'negative'),
        'neutral': sum(1 for r in results if r['overall_sentiment'] == 'neutral')
    }

    # Summary statistics
    total_comments = len(results)
    total_found_tokens = sum(r['found_sentiment_tokens'] for r in results)

    summary = {
        'total_comments': total_comments,
        'avg_sentiment_score': sum(r['total_score'] for r in results) / total_comments if total_comments > 0 else 0.0,
        'total_sentiment_tokens_found': total_found_tokens,
        'overall_ratio': {
            'positive': sentiment_count['positive'] / total_comments if total_comments > 0 else 0.0,
            'negative': sentiment_count['negative'] / total_comments if total_comments > 0 else 0.0,
            'neutral': sentiment_count['neutral'] / total_comments if total_comments > 0 else 0.0
        }
    }

    # Save summary to CSV as well
    summary_df = pd.DataFrame([summary])
    summary_df.to_csv('sentiment_summary.csv', index=False)

    # Save comment-level results to CSV
    results_csv = []
    for result in results:
        for detail in result['sentiment_details']:
            results_csv.append({
                'comment': result['comment'],
                'token': detail['token'],
                'score': detail['score'],
                'sentiment': detail['sentiment']
            })

    results_df = pd.DataFrame(results_csv)
    results_df.to_csv('sentiment_results.csv', index=False)

    # Save detailed Excel format with tokens as comma-separated
    excel_data = []

    if source == 'youtube':
        for i, comment_data in enumerate(data):
            video_title = comment_data.get('video_title', f'Video {i+1}')
            for comment_obj in comment_data['comments']:
                comment = comment_obj['comment']
                tokens = preprocess_text(comment, stemmer)
                total_score, positive_score, negative_score, sentiment_details, found_tokens = analyze_sentiment(tokens, sentiment_dict)
                overall = overall_sentiment(total_score)

                # Get all tokens as comma-separated string
                all_tokens = ', '.join([f"{detail['token']}({detail['score']:.2f})" for detail in sentiment_details])
                # Get sentiment summary per comment
                excel_data.append({
                    'source': source_name,
                    'video_title': video_title,
                    'comment': comment,
                    'tokens': all_tokens,
                    'total_score': total_score,
                    'positive_score': positive_score,
                    'negative_score': negative_score,
                    'sentiment_tokens_found': found_tokens,
                    'overall_sentiment': overall
                })
    elif source == 'twitter':
        for i, tweet_data in enumerate(data):
            comment = tweet_data['text']
            tokens = preprocess_text(comment, stemmer)
            total_score, positive_score, negative_score, sentiment_details, found_tokens = analyze_sentiment(tokens, sentiment_dict)
            overall = overall_sentiment(total_score)

            # Get all tokens as comma-separated string
            all_tokens = ', '.join([f"{detail['token']}({detail['score']:.2f})" for detail in sentiment_details])
            # Get sentiment summary per comment
            username = tweet_data.get('user', {}).get('username', 'Unknown')
            excel_data.append({
                'source': source_name,
                'video_title': f'Tweet by {username}',
                'comment': comment,
                'tokens': all_tokens,
                'total_score': total_score,
                'positive_score': positive_score,
                'negative_score': negative_score,
                'sentiment_tokens_found': found_tokens,
                'overall_sentiment': overall
            })

    excel_df = pd.DataFrame(excel_data)
    try:
        excel_df.to_excel(f'sentiment_analysis_{source}.xlsx', index=False)
    except PermissionError:
        print(f"Warning: Could not save Excel file 'sentiment_analysis_{source}.xlsx'. File may be open in another application.")

    # Updated Summary DataFrame with custom dictionary scores
    summary_df = {
        'Metric': ['Total Comments', 'Avg Sentiment Score', 'Total Sentiment Tokens Found', 'Positive Ratio', 'Negative Ratio', 'Neutral Ratio'],
        'Value': [
            summary['total_comments'],
            f"{summary['avg_sentiment_score']:.2f}",
            summary['total_sentiment_tokens_found'],
            f"{summary['overall_ratio']['positive']:.2f}",
            f"{summary['overall_ratio']['negative']:.2f}",
            f"{summary['overall_ratio']['neutral']:.2f}"
        ]
    }
    summary_df = pd.DataFrame(summary_df)
    summary_df.to_csv('sentiment_summary.csv', index=False)

    print("Analysis Complete using custom sentiment dictionary!")
    print(f"Total Comments: {summary['total_comments']}")
    print(f"Overall Sentiment Distribution:")
    print(f"  Positive: {sentiment_count['positive']}")
    print(f"  Negative: {sentiment_count['negative']}")
    print(f"  Neutral: {sentiment_count['neutral']}")
    print(f"Average Sentiment Score: {summary['avg_sentiment_score']:.2f}")
    print(f"Total Sentiment Tokens Found: {summary['total_sentiment_tokens_found']}")
    print(f"Positive Ratio: {summary['overall_ratio']['positive']:.2f}")
    print(f"Negative Ratio: {summary['overall_ratio']['negative']:.2f}")
    print(f"Neutral Ratio: {summary['overall_ratio']['neutral']:.2f}")

if __name__ == "__main__":
    main()
