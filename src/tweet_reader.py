import csv
import random
from typing import Dict, Optional
from datetime import datetime

class TweetReader:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        
    def _read_tweets(self) -> list:
        """Read all tweets from CSV file."""
        tweets = []
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert printed string to boolean
                row['printed'] = row['printed'].lower() == 'true'
                tweets.append(row)
        return tweets
        
    def _write_tweets(self, tweets: list) -> None:
        """Write tweets back to CSV file."""
        fieldnames = ['username', 'title', 'content', 'tags', 'date', 'printed']
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(tweets)
            
    def get_random_unprinted_tweet(self) -> Optional[Dict]:
        """Get a random unprinted tweet and mark it as printed."""
        tweets = self._read_tweets()
        
        # Filter unprinted tweets
        unprinted = [t for t in tweets if not t['printed']]
        if not unprinted:
            # Reset all tweets to unprinted
            for t in tweets:
                t['printed'] = False
            self._write_tweets(tweets)
            # Now get an unprinted tweet
            unprinted = tweets
            
        # Select random tweet
        tweet = random.choice(unprinted)
        
        # Mark as printed
        for t in tweets:
            if (t['username'] == tweet['username'] and 
                t['date'] == tweet['date']):
                t['printed'] = True
                break
                
        # Write back to file
        self._write_tweets(tweets)
        
        # Format tweet for printer
        return {
            'username': tweet['username'],
            'title': tweet['title'],
            'content': tweet['content'],
            'hashtags': tweet['tags'].split(),
            'date': tweet['date']
        }
