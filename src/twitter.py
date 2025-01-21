import tweepy
from typing import List, Dict
import os
import time
from dotenv import load_dotenv
from colorama import Fore

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
                tweet_fields=['text', 'entities', 'context_annotations']
            )
            
            if not tweets.data:
                return []
            
            formatted_tweets = []
            for tweet in tweets.data:
                # Get hashtags if available
                hashtags = []
                if hasattr(tweet, 'entities') and 'hashtags' in tweet.entities:
                    hashtags = [f"#{tag['tag']}" for tag in tweet.entities['hashtags']]
                
                # Split text into title and content (first line as title)
                text_parts = tweet.text.split('\n', 1)
                title = text_parts[0]
                content = text_parts[1] if len(text_parts) > 1 else ""
                
                formatted_tweets.append({
                    'username': username,
                    'title': title,
                    'content': content,
                    'hashtags': hashtags
                })
                
            return formatted_tweets
        except tweepy.errors.TweepyException as e:
            print(f"Error fetching tweets for {username}: {str(e)}")
            return []
            
    def fetch_all_accounts(self) -> List[str]:
        """Fetch tweets from all configured accounts."""
        all_tweets = []
        for account in self.config['twitter']['accounts']:
            username = account['username']
            try:
                tweets = self.fetch_tweets(
                    username,
                    self.config['twitter']['fetch_count']
                )
                all_tweets.extend(tweets)
                # Add delay between requests to avoid rate limiting
                time.sleep(2)  # 2 second delay between requests
            except tweepy.errors.TooManyRequests:
                print(f"{Fore.YELLOW}Rate limit reached. Waiting 15 minutes...{Fore.RESET}")
                time.sleep(900)  # Wait 15 minutes
                continue
            except Exception as e:
                print(f"{Fore.RED}Error fetching tweets for {username}: {str(e)}{Fore.RESET}")
                continue
        return all_tweets
