import yaml
import keyboard
import time
from colorama import init, Fore
from typing import Dict

from printer import M08FPrinter
from tweet_reader import TweetReader

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
    tweet_reader = TweetReader('tweets.csv')
    printer = M08FPrinter(config)
    
    print(f"{Fore.GREEN}Starting Tweet Printer...{Fore.RESET}")
    
    # Print startup message
    print(f"{Fore.BLUE}Printing startup message...{Fore.RESET}")
    if not printer.print_startup_message():
        print(f"{Fore.RED}Failed to print startup message. Please check connection and try again.{Fore.RESET}")
        return
    
    print(f"{Fore.GREEN}Printer initialization successful!{Fore.RESET}")
    print(f"{Fore.YELLOW}Press ESC to exit{Fore.RESET}")
    
    try:
        while not keyboard.is_pressed('esc'):
            # Get random unprinted tweet
            tweet = tweet_reader.get_random_unprinted_tweet()
            
            if tweet:
                print(f"{Fore.WHITE}Printing tweet from @{tweet['username']}:{Fore.RESET}")
                print(f"{Fore.CYAN}Title: {tweet['title'][:50]}...{Fore.RESET}")
                if tweet['hashtags']:
                    print(f"{Fore.BLUE}Tags: {' '.join(tweet['hashtags'])}{Fore.RESET}")
                
                try:
                    if not printer.print_text(tweet):
                        print(f"{Fore.RED}Failed to print tweet. Check printer connection.{Fore.RESET}")
                        time.sleep(5)  # Wait before retrying
                except Exception as e:
                    print(f"{Fore.RED}Printer error: {str(e)}{Fore.RESET}")
                    time.sleep(5)  # Wait before retrying
            else:
                print(f"{Fore.YELLOW}No unprinted tweets found. Waiting 10 seconds...{Fore.RESET}")
                time.sleep(10)  # Wait before checking again
            
            time.sleep(0.1)  # Small delay to prevent CPU overuse
            
    except KeyboardInterrupt:
        print(f"{Fore.RED}Interrupted by user{Fore.RESET}")
    except Exception as e:
        print(f"{Fore.RED}Unexpected error: {str(e)}{Fore.RESET}")
    finally:
        printer.close()
        print(f"{Fore.GREEN}Printer connection closed{Fore.RESET}")

if __name__ == '__main__':
    main()
