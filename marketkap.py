import requests
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

# Database setup
Base = declarative_base()
engine = create_engine("postgresql://user:password@localhost:5432/memecoins")
Session = sessionmaker(bind=engine)

class MarketData(Base):
    __tablename__ = "market_data"
    id = Column(Integer, primary_key=True)
    coin = Column(String)
    ticker = Column(String)
    contract_address = Column(String)
    market_cap = Column(Float)
    ath_market_cap = Column(Float)
    ath_timestamp = Column(DateTime)
    timestamp = Column(DateTime)

def fetch_market_data(coins, contract_map):
    """
    Fetch market cap and ATH data for Solana meme coins.
    Args:
        coins (list): List of coin tickers
        contract_map (dict): Mapping of tickers to Solana contract addresses
    Returns:
        dict: Market cap, ATH, and percentage changes
    """
    session = Session()
    results = {}
    base_url = "https://api.coingecko.com/api/v3"

    for coin in coins:
        contract = contract_map.get(coin)
        if not contract:
            logging.warning(f"No contract address for {coin}")
            continue
        try:
            # Fetch market data (simplified; use contract address for Solana coins)
            response = requests.get(f"{base_url}/coins/solana/contract/{contract}")
            if response.status_code != 200:
                logging.error(f"API error for {coin}: {response.status_code}")
                continue
            data = response.json()

            market_cap = data["market_data"]["market_cap"]["usd"]
            ath_market_cap = data["market_data"]["ath"]["usd"]
            ath_date = data["market_data"]["ath_date"]["usd"]
            timestamp = datetime.utcnow()

            # Calculate percentage change from ATH
            ath_change = ((market_cap - ath_market_cap) / ath_market_cap) * 100

            # Store in database
            market_entry = MarketData(
                coin=coin,
                ticker=coin,
                contract_address=contract,
                market_cap=market_cap,
                ath_market_cap=ath_market_cap,
                ath_timestamp=datetime.fromisoformat(ath_date.replace("Z", "+00:00")),
                timestamp=timestamp
            )
            session.add(market_entry)
            session.commit()

            results[coin] = {
                "market_cap": market_cap,
                "ath_market_cap": ath_market_cap,
                "ath_change": ath_change,
                "timestamp": timestamp
            }

        except Exception as e:
            logging.error(f"Error fetching market data for {coin}: {e}")
            session.rollback()

    return results

# Example usage
coins = ["$DOGE", "$SHIB", "$BONK"]
contract_map = {"$DOGE": "solana_contract_1", "$SHIB": "solana_contract_2", "$BONK": "solana_contract_3"}
market_data = fetch_market_data(coins, contract_map)
print(market_data)