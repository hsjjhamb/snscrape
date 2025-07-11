# Extract Specific Twitter Thread & Visualize

This script extracts all replies, nested replies, quoted tweets, and images from a **specific tweet** (not from a whole profile).  
It also finds all quote tweets of this post by the same author, and includes their nested threads.

## Usage

```bash
python extract_specific_thread.py --tweet_url https://twitter.com/username/status/1234567890 --save_images
```
or
```bash
python extract_specific_thread.py --tweet_id 1234567890 --save_images
```

- `--tweet_url` : URL of the main tweet you want to extract the thread from.
- `--tweet_id`  : Tweet ID if you don't have the URL.
- `--save_images` : Download images to a folder named `<tweet_id>_images`.

## Output

- `<tweet_id>_thread.json` : full structured thread, replies, quotes, images
- `<tweet_id>_mindmap.md` : Mermaid mindmap for visual/manual verification
- `<tweet_id>_images/` : all images, if you use `--save_images`

## Free Tools Used

- [snscrape](https://github.com/JustAnotherArchivist/snscrape) (Python, free)
- [Mermaid](https://mermaid-js.github.io/) (visualization, free)
- Python standard libraries

## Visual Mindmap Example

Open `<tweet_id>_mindmap.md` in Obsidian, Notion, or GitHub to explore the thread visually.

```