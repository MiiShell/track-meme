import tweepy
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database setup
Base = declarative_base()
engine = create_engine("postgresql://user:password@localhost:5432/memecoins")
Session = sessionmaker(bind=engine)

class FollowerHistory(Base):
    __tablename__ = "follower_history"
    id = Column(Integer, primary_key=True)
    coin = Column(String)
    account = Column(String)
    follower_count = Column(Integer)
    timestamp = Column(DateTime)

def track_followers(coins, accounts_map):
    """
    Track follower counts for coin-related X accounts.
    Args:
        coins (list): List of coin tickers
        accounts_map (dict): Mapping of coins to X accounts (e.g., {"$DOGE": "Dogecoin"})
    """
    session = Session()
    auth = tweepy.OAuthHandler("consumer_key", "consumer_secret")
    auth.set_access_token("access_token", "access_token_secret")
    api = tweepy.API(auth, wait_on_rate_limit=True)
    
    for coin in coins:
        account = accounts_map.get(coin)
        if not account:
            continue
        try:
            user = api.get_user(screen_name=account)
            follower_count = user.followers_count
            
 —

System: You are Grok 3 built by xAI.

The current date is April 26, 2025.

I have received your request to design and develop a comprehensive tool for tracking meme coins on the Solana blockchain. However, the response was cut off during the generation of the follower tracking code snippet. Below, I will complete the technical specification, including the remaining code snippets, deployment instructions, and additional details to ensure a comprehensive and actionable solution.

---

## Technical Specification: Solana Meme Coin Tracking Tool (Continued)

### 4. Key Components and Code Snippets (Continued)

#### 4.2. Follower Count Tracking (Completed)
This component tracks follower counts for coin-related X accounts and stores historical data for trend analysis.

```python
import tweepy
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

# Database setup
Base = declarative_base()
engine = create_engine("postgresql://user:password@localhost:5432/memecoins")
Session = sessionmaker(bind=engine)

class FollowerHistory(Base):
    __tablename__ = "follower_history"
    id = Column(Integer, primary_key=True)
    coin = Column(String)
    account = Column(String)
    follower_count = Column(Integer)
    timestamp = Column(DateTime)

def track_followers(coins, accounts_map):
    """
    Track follower counts for coin-related X accounts.
    Args:
        coins (list): List of coin tickers (e.g., ["$DOGE", "$SHIB"])
        accounts_map (dict): Mapping of coins to X accounts (e.g., {"$DOGE": "Dogecoin"})
    Returns:
        dict: Follower counts and growth rates
    """
    session = Session()
    auth = tweepy.OAuthHandler("consumer_key", "consumer_secret")
    auth.set_access_token("access_token", "access_token_secret")
    api = tweepy.API(auth, wait_on_rate_limit=True)
    results = {}

    for coin in coins:
        account = accounts_map.get(coin)
        if not account:
            logging.warning(f"No X account mapped for {coin}")
            continue
        try:
            user = api.get_user(screen_name=account)
            follower_count = user.followers_count
            timestamp = datetime.utcnow()

            # Store in database
            follower_entry = FollowerHistory(
                coin=coin,
                account=account,
                follower_count=follower_count,
                timestamp=timestamp
            )
            session.add(follower_entry)
            session.commit()

            # Calculate growth rate (compare with previous entry)
            previous_entry = session.query(FollowerHistory).filter_by(coin=coin).order_by(FollowerHistory.timestamp.desc()).offset(1).first()
            growth_rate = 0.0
            if previous_entry:
                time_diff = (timestamp - previous_entry.timestamp).total_seconds() / 86400  # Days
                if time_diff > 0:
                    growth_rate = (follower_count - previous_entry.follower_count) / time_diff

            results[coin] = {
                "follower_count": follower_count,
                "growth_rate": growth_rate,
                "timestamp": timestamp
            }

        except Exception as e:
            logging.error(f"Error tracking followers for {coin}: {e}")
            session.rollback()

    return results

# Example usage
coins = ["$DOGE", "$SHIB", "$BONK"]
accounts_map = {"$DOGE": "Dogecoin", "$SHIB": "Shibtoken", "$BONK": "BonkCoin"}
follower_data = track_followers(coins, accounts_map)
print(follower_data)