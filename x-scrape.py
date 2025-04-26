import tweepy
from transformers import pipeline
import spacy
from collections import defaultdict
import logging

# Initialize X API client
auth = tweepy.OAuthHandler("consumer_key", "consumer_secret")
auth.set_access_token("access_token", "access_token_secret")
api = tweepy.API(auth, wait_on_rate_limit=True)

# Initialize NLP models
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
nlp = spacy.load("en_core_web_sm")

def analyze_x_posts(coins, query_limit=100):
    """
    Scrape X posts for meme coins and analyze sentiment/trading signals.
    Args:
        coins (list): List of coin tickers (e.g., ["$DOGE", "$SHIB"])
        query_limit (int): Max posts to fetch per coin
    Returns:
        dict: Sentiment scores, mentions, and signals per coin
    """
    results = defaultdict(lambda: {"mentions": 0, "sentiment_score": 0.0, "signals": []})
    
    for coin in coins:
        try:
            query = f"{coin} Solana -filter:retweets"
            posts = api.search_tweets(q=query, count=query_limit, lang="en")
            
            for post in posts:
                text = post.text.lower()
                results[coin]["mentions"] += 1
                
                # Sentiment analysis
                sentiment = sentiment_analyzer(text)[0]
                score = sentiment["score"] if sentiment["label"] == "POSITIVE" else -sentiment["score"]
                results[coin]["sentiment_score"] += score
                
                # Detect trading signals (e.g., "buy", "sell", "pump")
                doc = nlp(text)
                signals = [token.text for token in doc if token.text in ["buy", "sell", "pump", "dump"]]
                if signals:
                    results[coin]["signals"].extend(signals)
                
                # Weight by influence (follower count, engagement)
                influence = post.user.followers_count + post.retweet_count + post.favorite_count
                results[coin]["sentiment_score"] *= (1 + influence / 10000)
        
        except Exception as e:
            logging.error(f"Error analyzing {coin}: {e}")
    
    # Normalize sentiment scores
    for coin in results:
        if results[coin]["mentions"] > 0:
            results[coin]["sentiment_score"] /= results[coin]["mentions"]
    
    return dict(results)

# Example usage
coins = ["$DOGE", "$SHIB", "$BONK"]
results = analyze_x_posts(coins)
print(results)