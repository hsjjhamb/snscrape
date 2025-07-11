import snscrape.modules.twitter as sntwitter
import json
import os
import re

def extract_images(tweet):
    images = []
    if hasattr(tweet, 'media') and tweet.media:
        for m in tweet.media:
            if hasattr(m, 'fullUrl'):
                images.append(m.fullUrl)
            elif hasattr(m, 'url'):
                images.append(m.url)
    return images

def get_thread(tweet, depth=0):
    thread = {
        'id': tweet.id,
        'content': tweet.content,
        'author': tweet.user.username,
        'images': extract_images(tweet),
        'quoted': [],
        'replies': []
    }
    # Get replies to this tweet, recursively
    for reply in sntwitter.TwitterSearchScraper(f'to:{tweet.user.username} conversation_id:{tweet.id}').get_items():
        if reply.inReplyToTweetId == tweet.id:
            thread['replies'].append(get_thread(reply, depth+1))
    # If this tweet quotes another, include it
    if hasattr(tweet, 'quotedTweet') and tweet.quotedTweet:
        thread['quoted'].append(get_thread(tweet.quotedTweet, depth+1))
    return thread

def find_author_quotes(main_tweet_id, author):
    # Find all quote tweets by the author quoting the main tweet
    quoted_threads = []
    search_query = f'from:{author} url:"twitter.com/{author}/status/{main_tweet_id}"'
    for tweet in sntwitter.TwitterSearchScraper(search_query).get_items():
        quoted_threads.append(get_thread(tweet))
    return quoted_threads

def main(tweet_url=None, tweet_id=None, save_images=False):
    # Extract tweet ID from URL
    if tweet_url:
        m = re.search(r'twitter\.com/([^/]+)/status/(\d+)', tweet_url)
        if not m:
            print("Could not parse tweet URL!")
            return
        author = m.group(1)
        tweet_id = m.group(2)
    elif tweet_id:
        # Try to get author from tweet object
        tweet = next(sntwitter.TwitterTweetScraper(tweet_id).get_items())
        author = tweet.user.username
    else:
        print("Provide either --tweet_url or --tweet_id")
        return

    # Get main tweet object
    main_tweet = next(sntwitter.TwitterTweetScraper(tweet_id).get_items())
    main_thread = get_thread(main_tweet)
    # Find all quote tweets of the main post by the author
    author_quotes = find_author_quotes(tweet_id, author)
    main_thread['author_quotes'] = author_quotes

    # Save JSON output
    with open(f"{tweet_id}_thread.json", "w", encoding="utf-8") as f:
        json.dump(main_thread, f, indent=2, ensure_ascii=False)
    print(f"Saved thread to {tweet_id}_thread.json")

    # Optionally save images
    if save_images:
        os.makedirs(f"{tweet_id}_images", exist_ok=True)
        save_images_from_thread(main_thread, f"{tweet_id}_images")

    # Generate mindmap
    with open(f"{tweet_id}_mindmap.md", "w", encoding="utf-8") as f:
        f.write(generate_mermaid_mindmap(main_thread, author))
    print(f"Saved mindmap to {tweet_id}_mindmap.md")

def save_images_from_thread(thread, img_dir):
    import requests
    for idx, img_url in enumerate(thread.get('images', [])):
        try:
            ext = os.path.splitext(img_url)[1][:5]
            filename = f"{thread['id']}_{idx}{ext}"
            path = os.path.join(img_dir, filename)
            r = requests.get(img_url, timeout=10)
            if r.status_code == 200:
                with open(path, "wb") as f:
                    f.write(r.content)
        except Exception as e:
            print(f"Error downloading {img_url}: {e}")
    for qt in thread.get('quoted', []):
        save_images_from_thread(qt, img_dir)
    for reply in thread.get('replies', []):
        save_images_from_thread(reply, img_dir)
    for qt in thread.get('author_quotes', []):
        save_images_from_thread(qt, img_dir)

def generate_mermaid_mindmap(thread, author):
    def thread_to_mermaid(thread, indent=2):
        img_info = f" ({len(thread['images'])} imgs)" if thread['images'] else ""
        label = f"{thread['id']}: {thread['content'][:40].replace('\n',' ')}{img_info}"
        result = " " * indent + f"{label}\n"
        for qt in thread.get("quoted", []):
            result += " " * (indent+2) + f"Quoted:\n" + thread_to_mermaid(qt, indent+4)
        for reply in thread.get("replies", []):
            result += " " * (indent+2) + f"Reply:\n" + thread_to_mermaid(reply, indent+4)
        return result
    mermaid = "```mermaid\nmindmap\n"
    mermaid += f"  root\n    {author}\n"
    mermaid += thread_to_mermaid(thread, indent=6)
    # Visualize the author's quote tweets as separate branches
    if 'author_quotes' in thread and thread['author_quotes']:
        mermaid += "      Author_Quotes\n"
        for qt in thread['author_quotes']:
            mermaid += thread_to_mermaid(qt, indent=8)
    mermaid += "```\n"
    return mermaid

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--tweet_url", type=str, help="Main tweet URL")
    parser.add_argument("--tweet_id", type=str, help="Main tweet ID (if URL not provided)")
    parser.add_argument("--save_images", action="store_true", help="Download images to local folder")
    args = parser.parse_args()
    main(tweet_url=args.tweet_url, tweet_id=args.tweet_id, save_images=args.save_images)
