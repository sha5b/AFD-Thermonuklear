import csv
from src.tweet_reader import TweetReader

def test_tweet_reader():
    reader = TweetReader('tweets.csv')
    tweet = reader.get_random_unprinted_tweet()
    
    if tweet:
        print("Tweet retrieved successfully:")
        print(f"Username: {tweet['username']}")
        print(f"Title: {tweet['title']}")
        print(f"Content: {tweet['content']}")
        print(f"Date: {tweet['date']}")
        print(f"Hashtags: {tweet['hashtags']}")
    else:
        print("No tweet retrieved")

if __name__ == "__main__":
    test_tweet_reader()
