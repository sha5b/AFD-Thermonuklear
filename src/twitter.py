import tweepy
from typing import List, Dict
import os
from dotenv import load_dotenv

class TwitterClient:
    def __init__(self, config: Dict):
        load_dotenv()
        
        # Initialize Twitter API v2 client
        self.client = tweepy.Client(
            bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
            consumer_key=os.getenv('TWITTER_API_KEY'),
            consumer_secret=os.getenv('TWITTER_API_SECRET'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        )
        self.config = config
        
    def fetch_tweets(self, username: str, count: int) -> List[str]:
        """Fetch tweets from a specific user using Twitter API v2."""
        try:
            # First get the user ID from username
            user = self.client.get_user(username=username)
            if not user.data:
                print(f"User {username} not found")
                return []
                
            # Then get their tweets
            tweets = self.client.get_users_tweets(
                id=user.data.id,
                max_results=min(count, 100),  # API v2 max is 100 per request
                tweet_fields=['text']
            )
            
            if not tweets.data:
                return []
                
            return [tweet.text for tweet in tweets.data]
        except tweepy.errors.TweepyException as e:
            print(f"Error fetching tweets for {username}: {str(e)}")
            return []
            
    def fetch_all_accounts(self) -> List[str]:
        """Fetch tweets from all configured accounts."""
        all_tweets = []
        for account in self.config['twitter']['accounts']:
            username = account['username']
            tweets = self.fetch_tweets(
                username,
                self.config['twitter']['fetch_count']
            )
            all_tweets.extend(tweets)
        return all_tweets
