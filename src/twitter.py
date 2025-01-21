import tweepy
from typing import List, Dict, Set, Optional
import os
import time
import json
from datetime import datetime, timedelta
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
            access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
            wait_on_rate_limit=True  # Auto-wait when rate limited
        )
        self.config = config
        
    def fetch_tweets(self, username: str, count: int, since_id: Optional[str] = None) -> List[Dict]:
        """Fetch tweets from a specific user using Twitter API v2."""
        try:
            # First get the user ID from username
            user = self.client.get_user(username=username)
            if not user.data:
                print(f"User {username} not found")
                return []
            
            # Then get their tweets with pagination
            all_tweets = []
            pagination_token = None
            remaining_count = count
            
            while remaining_count > 0:
                # Fetch tweets
                tweets = self.client.get_users_tweets(
                    id=user.data.id,
                    max_results=min(remaining_count, 10),  # Reduced to minimize rate limiting
                    since_id=since_id,  # Only get tweets newer than this ID
                    pagination_token=pagination_token,
                    tweet_fields=['text', 'entities', 'context_annotations', 'id']
                )
                
                if not tweets.data:
                    break
                    
                # Process tweets
                for tweet in tweets.data:
                    # Get hashtags if available
                    hashtags = []
                    if hasattr(tweet, 'entities') and 'hashtags' in tweet.entities:
                        hashtags = [f"#{tag['tag']}" for tag in tweet.entities['hashtags']]
                    
                    # Split text into title and content (first line as title)
                    text_parts = tweet.text.split('\n', 1)
                    title = text_parts[0]
                    content = text_parts[1] if len(text_parts) > 1 else ""
                    
                    all_tweets.append({
                        'username': username,
                        'title': title,
                        'content': content,
                        'hashtags': hashtags,
                        'id': tweet.id
                    })
                
                # Update remaining count
                remaining_count -= len(tweets.data)
                
                # Check if there are more pages
                if not tweets.meta or 'next_token' not in tweets.meta:
                    break
                    
                pagination_token = tweets.meta['next_token']
                time.sleep(1)  # Small delay between pages
            
            return all_tweets
            
        except tweepy.errors.TooManyRequests:
            print(f"{Fore.YELLOW}Rate limit reached for {username}, will retry later{Fore.RESET}")
            return []
        except tweepy.errors.TweepyException as e:
            print(f"{Fore.RED}Error fetching tweets for {username}: {str(e)}{Fore.RESET}")
            return []
            
    def fetch_all_accounts(self, last_tweet_ids: Dict[str, str]) -> List[Dict]:
        """Fetch tweets from all configured accounts."""
        all_tweets = []
        for account in self.config['twitter']['accounts']:
            username = account['username']
            since_id = last_tweet_ids.get(username)
            tweets = self.fetch_tweets(
                username,
                self.config['twitter']['fetch_count'],
                since_id=since_id
            )
            all_tweets.extend(tweets)
            # Small delay between accounts
            time.sleep(1)
        return all_tweets
