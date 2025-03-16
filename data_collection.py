import os
import json
import pandas as pd
import logging
import time
import random
from datetime import datetime
from notification import EmailNotifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data_collection.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TunisianDataCollector:
    def __init__(self, output_dir="data"):
        """
        Initialize the data collector
        
        Args:
            output_dir: Directory to save collected data
        """
        self.output_dir = output_dir
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        self.notifier = EmailNotifier()
        
    def collect_twitter_data(self, api_key, api_secret, access_token, access_token_secret, 
                             query_terms=None, max_tweets=10000, days_to_run=7):
        """
        Collect Tunisian dialect data from Twitter
        
        Args:
            api_key: Twitter API key
            api_secret: Twitter API secret
            access_token: Twitter access token
            access_token_secret: Twitter access token secret
            query_terms: List of search terms (defaults to Tunisian-specific terms)
            max_tweets: Maximum number of tweets to collect
            days_to_run: Number of days to run the collection
        """
        try:
            import tweepy
        except ImportError:
            logger.info("Tweepy not found. Installing...")
            import subprocess
            subprocess.check_call(["pip", "install", "tweepy"])
            import tweepy
            
        if query_terms is None:
            query_terms = [
                "تونس", "تونسي", "تونسية", "تونسيين", "تونسيات",
                "tunis", "tunisie", "tunisian", "tounsi", "tounsia",
                "3asslema", "ahla", "labess", "chneya", "barcha",
                "شنية", "برشا", "لاباس", "أهلا", "عسلامة"
            ]
            
        # Authenticate with Twitter
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        
        # Initialize data storage
        all_tweets = []
        tweets_per_day = max_tweets // days_to_run
        
        start_time = datetime.now()
        end_time = start_time + pd.Timedelta(days=days_to_run)
        
        logger.info(f"Starting Twitter data collection for {days_to_run} days")
        self.notifier.send_notification(
            "Data Collection Started", 
            f"Twitter data collection has started and will run for {days_to_run} days."
        )
        
        day_count = 1
        while datetime.now() < end_time and len(all_tweets) < max_tweets:
            daily_tweets = []
            
            # Randomly select query terms to avoid repetition
            daily_terms = random.sample(query_terms, min(5, len(query_terms)))
            
            for term in daily_terms:
                try:
                    # Search for tweets
                    tweets = tweepy.Cursor(
                        api.search_tweets,
                        q=f"{term} -filter:retweets",
                        lang="ar",
                        tweet_mode="extended",
                        count=100
                    ).items(tweets_per_day // len(daily_terms))
                    
                    for tweet in tweets:
                        if hasattr(tweet, "full_text"):
                            text = tweet.full_text
                        else:
                            text = tweet.text
                            
                        # Clean the text
                        text = text.replace('\n', ' ').strip()
                        
                        # Store the tweet
                        daily_tweets.append({
                            "text": text,
                            "created_at": tweet.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                            "query_term": term
                        })
                        
                        if len(daily_tweets) >= tweets_per_day:
                            break
                            
                except Exception as e:
                    logger.error(f"Error collecting tweets for term '{term}': {str(e)}")
                    
                # Sleep to avoid rate limits
                time.sleep(5)
                
            # Save daily tweets
            all_tweets.extend(daily_tweets)
            
            # Save to CSV
            df = pd.DataFrame(daily_tweets)
            daily_file = os.path.join(self.output_dir, f"twitter_data_day_{day_count}.csv")
            df.to_csv(daily_file, index=False)
            
            logger.info(f"Day {day_count}: Collected {len(daily_tweets)} tweets. Total: {len(all_tweets)}")
            
            # Send notification
            if day_count % 1 == 0:  # Send notification every day
                self.notifier.send_notification(
                    f"Data Collection Update - Day {day_count}", 
                    f"Collected {len(daily_tweets)} tweets today.\n"
                    f"Total tweets collected: {len(all_tweets)}\n"
                    f"Progress: {len(all_tweets)}/{max_tweets} ({len(all_tweets)/max_tweets*100:.1f}%)"
                )
                
            # Sleep until next day
            day_count += 1
            time.sleep(60 * 60)  # Sleep for an hour before continuing
            
        # Save all tweets
        df = pd.DataFrame(all_tweets)
        all_file = os.path.join(self.output_dir, "twitter_data_all.csv")
        df.to_csv(all_file, index=False)
        
        logger.info(f"Twitter data collection completed. Total tweets: {len(all_tweets)}")
        self.notifier.send_notification(
            "Data Collection Complete", 
            f"Twitter data collection has completed.\n"
            f"Total tweets collected: {len(all_tweets)}"
        )
        
        return all_file
        
    def collect_web_data(self, urls=None, days_to_run=7):
        """
        Collect Tunisian dialect data from websites
        
        Args:
            urls: List of URLs to scrape (defaults to Tunisian news sites)
            days_to_run: Number of days to run the collection
        """
        try:
            import requests
            from bs4 import BeautifulSoup
        except ImportError:
            logger.info("Required packages not found. Installing...")
            import subprocess
            subprocess.check_call(["pip", "install", "requests", "beautifulsoup4"])
            import requests
            from bs4 import BeautifulSoup
            
        if urls is None:
            urls = [
                "https://www.mosaiquefm.net/",
                "https://www.tunisienumerique.com/",
                "https://www.businessnews.com.tn/",
                "https://www.tekiano.com/",
                "https://www.tuniscope.com/",
                "https://www.kapitalis.com/",
                "https://www.realites.com.tn/",
                "https://www.webdo.tn/",
                "https://www.tunisie-tribune.com/"
            ]
            
        # Initialize data storage
        all_articles = []
        articles_per_day = 100  # Target articles per day
        
        start_time = datetime.now()
        end_time = start_time + pd.Timedelta(days=days_to_run)
        
        logger.info(f"Starting web data collection for {days_to_run} days")
        self.notifier.send_notification(
            "Web Data Collection Started", 
            f"Web scraping has started and will run for {days_to_run} days."
        )
        
        day_count = 1
        while datetime.now() < end_time:
            daily_articles = []
            
            # Randomly select URLs to avoid repetition
            daily_urls = random.sample(urls, min(3, len(urls)))
            
            for url in daily_urls:
                try:
                    # Get the webpage
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                    response = requests.get(url, headers=headers, timeout=30)
                    response.raise_for_status()
                    
                    # Parse the HTML
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find all links that might be articles
                    article_links = []
                    for a in soup.find_all('a', href=True):
                        href = a['href']
                        if href.startswith('http'):
                            article_links.append(href)
                        elif href.startswith('/'):
                            article_links.append(url.rstrip('/') + href)
                            
                    # Randomly sample some article links
                    if article_links:
                        sample_size = min(10, len(article_links))
                        sampled_links = random.sample(article_links, sample_size)
                        
                        for link in sampled_links:
                            try:
                                # Get the article
                                article_response = requests.get(link, headers=headers, timeout=30)
                                article_response.raise_for_status()
                                
                                # Parse the article
                                article_soup = BeautifulSoup(article_response.text, 'html.parser')
                                
                                # Extract text from paragraphs
                                paragraphs = article_soup.find_all('p')
                                article_text = ' '.join([p.get_text().strip() for p in paragraphs])
                                
                                # Clean the text
                                article_text = article_text.replace('\n', ' ').strip()
                                
                                # Only keep articles with substantial text
                                if len(article_text) > 100:
                                    daily_articles.append({
                                        "text": article_text,
                                        "url": link,
                                        "source": url,
                                        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    })
                                    
                                    if len(daily_articles) >= articles_per_day:
                                        break
                                        
                            except Exception as e:
                                logger.error(f"Error processing article {link}: {str(e)}")
                                
                            # Sleep between article requests
                            time.sleep(random.uniform(2, 5))
                            
                except Exception as e:
                    logger.error(f"Error processing website {url}: {str(e)}")
                    
                # Sleep between website requests
                time.sleep(random.uniform(10, 20))
                
                if len(daily_articles) >= articles_per_day:
                    break
                    
            # Save daily articles
            all_articles.extend(daily_articles)
            
            # Save to CSV
            df = pd.DataFrame(daily_articles)
            daily_file = os.path.join(self.output_dir, f"web_data_day_{day_count}.csv")
            df.to_csv(daily_file, index=False)
            
            logger.info(f"Day {day_count}: Collected {len(daily_articles)} articles. Total: {len(all_articles)}")
            
            # Send notification
            if day_count % 1 == 0:  # Send notification every day
                self.notifier.send_notification(
                    f"Web Data Collection Update - Day {day_count}", 
                    f"Collected {len(daily_articles)} articles today.\n"
                    f"Total articles collected: {len(all_articles)}"
                )
                
            # Sleep until next day
            day_count += 1
            time.sleep(60 * 60 * 4)  # Sleep for 4 hours before continuing
            
        # Save all articles
        df = pd.DataFrame(all_articles)
        all_file = os.path.join(self.output_dir, "web_data_all.csv")
        df.to_csv(all_file, index=False)
        
        logger.info(f"Web data collection completed. Total articles: {len(all_articles)}")
        self.notifier.send_notification(
            "Web Data Collection Complete", 
            f"Web data collection has completed.\n"
            f"Total articles collected: {len(all_articles)}"
        )
        
        return all_file
    
    def collect_youtube_comments(self, api_key, query_terms=None, max_comments=10000, days_to_run=7):
        """
        Collect Tunisian dialect data from YouTube comments
        
        Args:
            api_key: YouTube API key
            query_terms: List of search terms (defaults to Tunisian-specific terms)
            max_comments: Maximum number of comments to collect
            days_to_run: Number of days to run the collection
        """
        try:
            from googleapiclient.discovery import build
        except ImportError:
            logger.info("Google API client not found. Installing...")
            import subprocess
            subprocess.check_call(["pip", "install", "google-api-python-client"])
            from googleapiclient.discovery import build
            
        if query_terms is None:
            query_terms = [
                "تونس", "تونسي", "tunisie", "tunisian", 
                "كلام تونسي", "دارجة تونسية", "tunisian dialect",
                "أغاني تونسية", "tunisian music", "tunisian food"
            ]
            
        # Initialize YouTube API
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # Initialize data storage
        all_comments = []
        comments_per_day = max_comments // days_to_run
        
        start_time = datetime.now()
        end_time = start_time + pd.Timedelta(days=days_to_run)
        
        logger.info(f"Starting YouTube comments collection for {days_to_run} days")
        self.notifier.send_notification(
            "YouTube Data Collection Started", 
            f"YouTube comments collection has started and will run for {days_to_run} days."
        )
        
        day_count = 1
        while datetime.now() < end_time and len(all_comments) < max_comments:
            daily_comments = []
            
            # Randomly select query terms
            daily_terms = random.sample(query_terms, min(3, len(query_terms)))
            
            for term in daily_terms:
                try:
                    # Search for videos
                    search_response = youtube.search().list(
                        q=term,
                        part="id,snippet",
                        maxResults=10,
                        type="video",
                        relevanceLanguage="ar"
                    ).execute()
                    
                    # Get video IDs
                    video_ids = [item['id']['videoId'] for item in search_response['items']]
                    
                    for video_id in video_ids:
                        try:
                            # Get comments for the video
                            comments_response = youtube.commentThreads().list(
                                part="snippet",
                                videoId=video_id,
                                maxResults=100,
                                textFormat="plainText"
                            ).execute()
                            
                            # Extract comments
                            for item in comments_response['items']:
                                comment = item['snippet']['topLevelComment']['snippet']
                                text = comment['textDisplay']
                                
                                # Clean the text
                                text = text.replace('\n', ' ').strip()
                                
                                # Store the comment
                                daily_comments.append({
                                    "text": text,
                                    "video_id": video_id,
                                    "published_at": comment['publishedAt'],
                                    "query_term": term
                                })
                                
                                if len(daily_comments) >= comments_per_day:
                                    break
                                    
                        except Exception as e:
                            logger.error(f"Error collecting comments for video {video_id}: {str(e)}")
                            
                        # Sleep to avoid rate limits
                        time.sleep(random.uniform(5, 10))
                        
                        if len(daily_comments) >= comments_per_day:
                            break
                            
                except Exception as e:
                    logger.error(f"Error searching for videos with term '{term}': {str(e)}")
                    
                # Sleep between search requests
                time.sleep(random.uniform(10, 20))
                
                if len(daily_comments) >= comments_per_day:
                    break
                    
            # Save daily comments
            all_comments.extend(daily_comments)
            
            # Save to CSV
            df = pd.DataFrame(daily_comments)
            daily_file = os.path.join(self.output_dir, f"youtube_data_day_{day_count}.csv")
            df.to_csv(daily_file, index=False)
            
            logger.info(f"Day {day_count}: Collected {len(daily_comments)} comments. Total: {len(all_comments)}")
            
            # Send notification
            if day_count % 1 == 0:  # Send notification every day
                self.notifier.send_notification(
                    f"YouTube Data Collection Update - Day {day_count}", 
                    f"Collected {len(daily_comments)} comments today.\n"
                    f"Total comments collected: {len(all_comments)}\n"
                    f"Progress: {len(all_comments)}/{max_comments} ({len(all_comments)/max_comments*100:.1f}%)"
                )
                
            # Sleep until next day
            day_count += 1
            time.sleep(60 * 60 * 6)  # Sleep for 6 hours before continuing
            
        # Save all comments
        df = pd.DataFrame(all_comments)
        all_file = os.path.join(self.output_dir, "youtube_data_all.csv")
        df.to_csv(all_file, index=False)
        
        logger.info(f"YouTube data collection completed. Total comments: {len(all_comments)}")
        self.notifier.send_notification(
            "YouTube Data Collection Complete", 
            f"YouTube comments collection has completed.\n"
            f"Total comments collected: {len(all_comments)}"
        )
        
        return all_file
    
    def import_existing_corpus(self, corpus_path, corpus_type="TSAC"):
        """
        Import an existing Tunisian dialect corpus
        
        Args:
            corpus_path: Path to the corpus file
            corpus_type: Type of corpus (TSAC, MADAR, etc.)
        """
        logger.info(f"Importing existing corpus: {corpus_path} (type: {corpus_type})")
        
        if corpus_type.upper() == "TSAC":
            # TSAC corpus format: CSV with text and sentiment columns
            try:
                df = pd.read_csv(corpus_path)
                
                # Ensure there's a text column
                if "text" not in df.columns and len(df.columns) > 0:
                    # Rename the first column to text
                    df = df.rename(columns={df.columns[0]: "text"})
                    
                # Save to our format
                output_file = os.path.join(self.output_dir, "tsac_corpus.csv")
                df.to_csv(output_file, index=False)
                
                logger.info(f"Imported {len(df)} examples from TSAC corpus")
                return output_file
                
            except Exception as e:
                logger.error(f"Error importing TSAC corpus: {str(e)}")
                return None
                
        elif corpus_type.upper() == "MADAR":
            # MADAR corpus format: TSV with dialect and text columns
            try:
                df = pd.read_csv(corpus_path, sep='\t')
                
                # Filter for Tunisian dialect
                if "dialect" in df.columns:
                    df = df[df["dialect"].str.contains("TUN", case=False)]
                    
                # Ensure there's a text column
                if "text" not in df.columns and "sentence" in df.columns:
                    df = df.rename(columns={"sentence": "text"})
                    
                # Save to our format
                output_file = os.path.join(self.output_dir, "madar_corpus.csv")
                df.to_csv(output_file, index=False)
                
                logger.info(f"Imported {len(df)} examples from MADAR corpus")
                return output_file
                
            except Exception as e:
                logger.error(f"Error importing MADAR corpus: {str(e)}")
                return None
                
        else:
            # Generic format: Try to load as CSV or text file
            try:
                # Try CSV first
                try:
                    df = pd.read_csv(corpus_path)
                    
                    # Ensure there's a text column
                    if "text" not in df.columns and len(df.columns) > 0:
                        # Rename the first column to text
                        df = df.rename(columns={df.columns[0]: "text"})
                        
                except Exception:
                    # Try as plain text file
                    with open(corpus_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        
                    # Create DataFrame
                    df = pd.DataFrame({"text": [line.strip() for line in lines if line.strip()]})
                    
                # Save to our format
                output_file = os.path.join(self.output_dir, f"{corpus_type.lower()}_corpus.csv")
                df.to_csv(output_file, index=False)
                
                logger.info(f"Imported {len(df)} examples from {corpus_type} corpus")
                return output_file
                
            except Exception as e:
                logger.error(f"Error importing {corpus_type} corpus: {str(e)}")
                return None
    
    def run_collection_pipeline(self, days_to_run=7, twitter_creds=None, youtube_api_key=None):
        """
        Run a complete data collection pipeline
        
        Args:
            days_to_run: Number of days to run the collection
            twitter_creds: Dictionary with Twitter API credentials
            youtube_api_key: YouTube API key
        """
        logger.info("Starting data collection pipeline")
        self.notifier.send_notification(
            "Data Collection Pipeline Started",
            f"Starting comprehensive data collection for {days_to_run} days"
        )
        
        # Collect web data
        web_file = self.collect_web_data(days_to_run=days_to_run)
        
        # Collect Twitter data if credentials provided
        if twitter_creds:
            twitter_file = self.collect_twitter_data(
                api_key=twitter_creds.get('api_key'),
                api_secret=twitter_creds.get('api_secret'),
                access_token=twitter_creds.get('access_token'),
                access_token_secret=twitter_creds.get('access_token_secret'),
                days_to_run=days_to_run
            )
        
        # Collect YouTube data if API key provided
        if youtube_api_key:
            youtube_file = self.collect_youtube_comments(
                api_key=youtube_api_key,
                days_to_run=days_to_run
            )
        
        # Combine all data
        all_files = []
        if 'web_file' in locals():
            all_files.append(web_file)
        if 'twitter_file' in locals():
            all_files.append(twitter_file)
        if 'youtube_file' in locals():
            all_files.append(youtube_file)
        
        # Combine into a single dataset
        all_data = []
        for file in all_files:
            df = pd.read_csv(file)
            if "text" in df.columns:
                all_data.extend(df["text"].tolist())
        
        # Save combined dataset
        combined_file = os.path.join(self.output_dir, "combined_data.csv")
        pd.DataFrame({"text": all_data}).to_csv(combined_file, index=False)
        
        logger.info(f"Data collection pipeline completed. Total examples: {len(all_data)}")
        self.notifier.send_notification(
            "Data Collection Pipeline Complete",
            f"Comprehensive data collection has completed.\n"
            f"Total examples collected: {len(all_data)}"
        )
        
        return combined_file

if __name__ == "__main__":
    collector = TunisianDataCollector()
    
    # Example usage:
    # 1. Import existing corpus
    # collector.import_existing_corpus("path/to/corpus.csv", "TSAC")
    
    # 2. Collect web data
    # collector.collect_web_data(days_to_run=1)
    
    # 3. Collect Twitter data
    # twitter_creds = {
    #     'api_key': 'YOUR_API_KEY',
    #     'api_secret': 'YOUR_API_SECRET',
    #     'access_token': 'YOUR_ACCESS_TOKEN',
    #     'access_token_secret': 'YOUR_ACCESS_TOKEN_SECRET'
    # }
    # collector.collect_twitter_data(**twitter_creds, days_to_run=1)
    
    # 4. Collect YouTube data
    # collector.collect_youtube_comments('YOUR_API_KEY', days_to_run=1)
    
    # 5. Run complete pipeline
    # collector.run_collection_pipeline(
    #     days_to_run=7,
    #     twitter_creds=twitter_creds,
    #     youtube_api_key='YOUR_API_KEY'
    # )