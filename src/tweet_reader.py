import csv
import random
from typing import Dict, Optional
from datetime import datetime

class TweetReader:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self._last_read_rows = []  # Store last read rows for writing back
        
    def _read_tweets(self) -> list:
        """Read all tweets from CSV file and pair German/English versions."""
        tweets = []
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self._last_read_rows = list(reader)
            
        # Pair German and English tweets
        i = 0
        while i < len(self._last_read_rows):
            # Convert printed string to boolean
            self._last_read_rows[i]['printed'] = self._last_read_rows[i]['printed'].lower() == 'true'
            
            if i + 1 < len(self._last_read_rows) and self._last_read_rows[i]['username'] == self._last_read_rows[i+1]['username'] and self._last_read_rows[i]['date'] == self._last_read_rows[i+1]['date']:
                # Found a pair - German and English versions
                self._last_read_rows[i]['english_content'] = self._last_read_rows[i+1]['content']
                tweets.append(self._last_read_rows[i])
                i += 2  # Skip the next row as it's the English version
            else:
                # No pair found, just add the current row
                self._last_read_rows[i]['english_content'] = ''
                tweets.append(self._last_read_rows[i])
                i += 1
                
        return tweets
        
    def _write_tweets(self, tweets: list) -> None:
        """Write tweets back to CSV file."""
        # Create a lookup of username+date -> printed status
        tweet_status = {}
        for tweet in tweets:
            key = (tweet['username'], tweet['date'])
            tweet_status[key] = tweet['printed']
        
        # Update the printed status in the last read rows
        for row in self._last_read_rows:
            key = (row['username'], row['date'])
            if key in tweet_status:
                row['printed'] = str(tweet_status[key]).upper()
        
        # Write back to file
        fieldnames = ['username', 'content', 'date', 'printed']
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self._last_read_rows)
            
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
        
        # Format tweet for printer with both German and English content
        return {
            'username': tweet['username'],
            'title': tweet['content'],
            'content': tweet.get('english_content', ''),
            'hashtags': [],
            'date': tweet['date']
        }
