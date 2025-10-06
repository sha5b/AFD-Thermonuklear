from src.tweet_reader import TweetReader

# Test getting a random unprinted tweet
def test_get_tweet():
    reader = TweetReader('tweets.csv')
    tweet = reader.get_random_unprinted_tweet()
    
    if tweet:
        print("Successfully got a tweet:")
        print(f"  Username: {tweet['username']}")
        print(f"  Title: {tweet['title']}")
        print(f"  Content: {tweet['content']}")
        print(f"  Hashtags: {tweet['hashtags']}")
    else:
        print("No tweet returned")

if __name__ == "__main__":
    test_get_tweet()
