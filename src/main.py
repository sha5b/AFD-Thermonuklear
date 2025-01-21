import yaml
import keyboard
import time
from colorama import init, Fore
from typing import Dict

from .twitter import TwitterClient
from .buffer import TweetBuffer
from .printer import M08FPrinter

def load_config() -> Dict:
    """Load configuration from YAML file."""
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

def main():
    # Initialize colorama for colored output
    init()
    
    print(f"{Fore.GREEN}Loading configuration...{Fore.RESET}")
    config = load_config()
    
    # Initialize components
    twitter_client = TwitterClient(config)
    tweet_buffer = TweetBuffer(config['printer']['buffer_size'])
    printer = M08FPrinter(config)
    
    print(f"{Fore.GREEN}Starting Twitter Printer...{Fore.RESET}")
    print(f"{Fore.YELLOW}Press ESC to exit{Fore.RESET}")
    
    try:
        while not keyboard.is_pressed('esc'):
            # Refill buffer if needed
            if tweet_buffer.is_empty():
                print(f"{Fore.BLUE}Fetching new tweets...{Fore.RESET}")
                tweets = twitter_client.fetch_all_accounts()
                tweet_buffer.add_tweets(tweets)
                # Add delay before next fetch attempt if buffer is still empty
                if tweet_buffer.is_empty():
                    print(f"{Fore.YELLOW}No new tweets found. Waiting 5 minutes before next attempt...{Fore.RESET}")
                    time.sleep(300)  # Wait 5 minutes
            
            # Get and print next tweet
            tweet = tweet_buffer.get_next_tweet()
            if tweet:
                print(f"{Fore.WHITE}Printing tweet from @{tweet['username']}: {tweet['title'][:50]}...{Fore.RESET}")
                printer.print_text(tweet)
            
            time.sleep(0.1)  # Small delay to prevent CPU overuse
            
    except KeyboardInterrupt:
        print(f"{Fore.RED}Interrupted by user{Fore.RESET}")
    finally:
        printer.close()
        print(f"{Fore.GREEN}Printer connection closed{Fore.RESET}")

if __name__ == '__main__':
    main()
