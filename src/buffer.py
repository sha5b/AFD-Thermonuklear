from collections import deque
from typing import Optional

class TweetBuffer:
    def __init__(self, max_size: int):
        self.buffer = deque(maxlen=max_size)
        
    def add_tweet(self, tweet: str) -> None:
        """Add a tweet to the buffer."""
        self.buffer.append(tweet)
        
    def get_next_tweet(self) -> Optional[str]:
        """Get the next tweet from the buffer."""
        if len(self.buffer) > 0:
            return self.buffer.popleft()
        return None
        
    def add_tweets(self, tweets: list) -> None:
        """Add multiple tweets to the buffer."""
        for tweet in tweets:
            self.add_tweet(tweet)
            
    def is_empty(self) -> bool:
        """Check if buffer is empty."""
        return len(self.buffer) == 0
        
    def get_buffer_size(self) -> int:
        """Get current number of tweets in buffer."""
        return len(self.buffer)
