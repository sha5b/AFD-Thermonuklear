import csv
from src.tweet_reader import TweetReader

# Test the pairing logic
def test_pairing():
    reader = TweetReader('tweets.csv')
    tweets = reader._read_tweets()
    
    print(f"Total paired tweets: {len(tweets)}")
    
    # Show first few tweets
    for i, tweet in enumerate(tweets[:5]):
        print(f"\nTweet {i+1}:")
        print(f"  Username: {tweet['username']}")
        print(f"  German: {tweet['content'][:50]}...")
        print(f"  English: {tweet.get('english_content', '')[:50]}...")
        print(f"  Printed: {tweet['printed']}")
        
    # Check for tweets without English content
    no_english = [t for t in tweets if not t.get('english_content', '').strip()]
    print(f"\nTweets without English content: {len(no_english)}")

if __name__ == "__main__":
    test_pairing()
