from collections import deque
from typing import Optional, Dict, List
import json
import os
from datetime import datetime

class TweetBuffer:
    def __init__(self, max_size: int):
        self.max_size = max_size
        self.buffer = deque(maxlen=max_size)
        self.state_file = "tweet_buffer_state.json"
        self.last_tweet_ids = {}  # Track last tweet ID per user
        self.load_state()
        
    def save_state(self) -> None:
        """Save buffer state and last tweet IDs to file."""
        state = {
            'buffer': list(self.buffer),
            'last_tweet_ids': self.last_tweet_ids,
            'last_updated': datetime.now().isoformat()
        }
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
            
    def load_state(self) -> None:
        """Load buffer state from file if it exists."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    # Restore buffer
                    self.buffer = deque(state['buffer'], maxlen=self.max_size)
                    # Restore last tweet IDs
                    self.last_tweet_ids = state['last_tweet_ids']
            except Exception as e:
                print(f"Error loading buffer state: {str(e)}")
                # Start fresh if state file is corrupted
                self.buffer = deque(maxlen=self.max_size)
                self.last_tweet_ids = {}
        
    def add_tweet(self, tweet: Dict) -> None:
        """Add a tweet to the buffer and update state."""
        # Only add if we haven't seen this tweet before
        tweet_id = tweet.get('id')
        if tweet_id:
            username = tweet['username']
            if username not in self.last_tweet_ids or tweet_id > self.last_tweet_ids[username]:
                self.buffer.append(tweet)
                self.last_tweet_ids[username] = tweet_id
                self.save_state()
        
    def get_next_tweet(self) -> Optional[Dict]:
        """Get the next tweet from the buffer."""
        if len(self.buffer) > 0:
            tweet = self.buffer.popleft()
            self.save_state()  # Save state after removing tweet
            return tweet
        return None
        
    def add_tweets(self, tweets: List[Dict]) -> None:
        """Add multiple tweets to the buffer."""
        for tweet in tweets:
            self.add_tweet(tweet)
            
    def is_empty(self) -> bool:
        """Check if buffer is empty."""
        return len(self.buffer) == 0
        
    def get_buffer_size(self) -> int:
        """Get current number of tweets in buffer."""
        return len(self.buffer)
        
    def get_last_tweet_id(self, username: str) -> Optional[str]:
        """Get the last seen tweet ID for a user."""
        return self.last_tweet_ids.get(username)
