"""Context:
CSV tweet storage and selection utilities.

Responsibilities:
- Read tweets from `tweets.csv`.
- Pair German/English rows where applicable.
- Mark tweets as printed and persist the updated CSV.
"""

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
        with open(self.csv_path, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            self._last_read_rows = list(reader)
            
        # Pair German and English tweets by assuming consecutive rows from same user are pairs
        i = 0
        while i < len(self._last_read_rows):
            # Convert printed string to boolean for current row
            self._last_read_rows[i]['printed'] = self._last_read_rows[i]['printed'].lower() == 'true'
            
            # Check if next row exists and can be paired
            if i + 1 < len(self._last_read_rows):
                # Convert printed string to boolean for next row
                self._last_read_rows[i+1]['printed'] = self._last_read_rows[i+1]['printed'].lower() == 'true'
                
                # Normalize usernames for comparison (accounting for extra spaces)
                username1 = self._last_read_rows[i]['username'].strip()
                username2 = self._last_read_rows[i+1]['username'].strip()
                
                # If usernames match, assume they're a pair
                if username1 == username2:
                    # Found a pair - German and English versions
                    self._last_read_rows[i]['english_content'] = self._last_read_rows[i+1]['content']
                    tweets.append(self._last_read_rows[i])
                    i += 2  # Skip the next row as it's the English version
                    continue
            
            # No pair found, just add the current row
            # Make sure we don't add empty content rows
            if self._last_read_rows[i]['content'].strip():
                self._last_read_rows[i]['english_content'] = ''
                tweets.append(self._last_read_rows[i])
            i += 1
                
        return tweets
    
    def _dates_match(self, date1: str, date2: str) -> bool:
        """Check if two dates match, accounting for various formats."""
        # Direct match
        if date1 == date2:
            return True
            
        # Remove periods and compare
        if date1.replace('.', '') == date2.replace('.', ''):
            return True
            
        # Case insensitive match
        if date1.lower() == date2.lower():
            return True
            
        # Remove spaces and compare
        if date1.replace(' ', '') == date2.replace(' ', ''):
            return True
            
        # Handle specific known mismatches
        # "10.10.2016" vs "Oktober 2016"
        if ("10.10.2016" in date1 and "oktober 2016" in date2.lower()) or \
           ("10.10.2016" in date2 and "oktober 2016" in date1.lower()):
            return True
        
        # Handle "August 2017" vs "08.2017" or similar
        if self._month_year_match(date1, date2):
            return True
            
        # "01.08.13" vs "01.08.2013" (handle 2-digit vs 4-digit years)
        if self._normalize_year_dates(date1, date2):
            return True
            
        return False
        
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
            # Write the original rows without any extra fields we added
            original_rows = []
            for row in self._last_read_rows:
                # Create a clean row with only the original fieldnames
                clean_row = {field: row.get(field, '') for field in fieldnames}
                original_rows.append(clean_row)
            writer.writerows(original_rows)
            
    def get_random_unprinted_tweet(self) -> Optional[Dict]:
        """Get a random unprinted tweet and mark it as printed."""
        tweets = self._read_tweets()
        
        # If no tweets available, return None
        if not tweets:
            return None
        
        # Filter unprinted tweets
        unprinted = [t for t in tweets if not t['printed']]
        
        # If no unprinted tweets, return None (don't reset automatically)
        if not unprinted:
            return None
            
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
