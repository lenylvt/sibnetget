import requests
from bs4 import BeautifulSoup
import json
import re

# Function to get the HTML content of a URL
def get_html(url):
    print(f"Fetching URL: {url}")
    response = requests.get(url)
    response.raise_for_status()  # Raises an HTTPError for bad responses
    return response.text

# Function to extract video details from the HTML
def extract_video_details(html, start_with_name):
    soup = BeautifulSoup(html, 'html.parser')
    videos = []
    
    video_cells = soup.find_all('div', class_='video_cell')
    print(f"Found {len(video_cells)} video cells")
    
    for cell in video_cells:
        video = {}
        
        # Ensure the span with itemprop='url' exists
        url_span = cell.find('span', itemprop='url')
        if url_span is not None:
            video['url'] = 'https://video.sibnet.ru' + url_span['content']
        else:
            print("URL span not found, skipping cell")
            continue
        
        # Ensure the span with itemprop='contentUrl' exists
        content_url_span = cell.find('span', itemprop='contentUrl')
        if content_url_span is not None:
            video['thumbnail'] = content_url_span['content']
        else:
            print("Content URL span not found, skipping cell")
            continue
        
        # Ensure the span with itemprop='name' exists
        name_span = cell.find('span', itemprop='name')
        if name_span is not None:
            video['name'] = name_span.text
        else:
            print("Name span not found, skipping cell")
            continue
        
        # Only include videos with titles starting with the specified string
        if not video['name'].startswith(start_with_name):
            print(f"Skipping video with title: {video['name']}")
            continue
        
        # Extract video ID from thumbnail URL and construct a new video URL
        thumbnail_url = video['thumbnail']
        match = re.search(r'video_(\d+)_', thumbnail_url)
        if match:
            video_id = match.group(1)
            video['new_video_url'] = f'https://video.sibnet.ru/shell.php?videoid={video_id}'

        video['episodeNumber'] = None
        
        videos.append(video)
        print(f"Added video: {video['name']}")
    
    return videos

# Function to iterate through multiple pages of video listings
def fetch_videos_from_pages(base_url, start_with_name, start_page, end_page):
    all_videos = []
    for page in range(start_page, end_page + 1):
        print(f"Processing page {page}")
        full_url = f"{base_url}?page={page}" if page > 1 else base_url  # Append page query only if it's not the first page
        html = get_html(full_url)
        video_details = extract_video_details(html, start_with_name)
        all_videos.extend(video_details)
        print(f"Total videos so far: {len(all_videos)}")
    return all_videos

# Main function to run the script
def main():

    # CONFIGURATION

    # Sibnet playlist URL
    base_url = ''

    # Find videos title starting with
    start_with_name = ""

    # Start and end page
    from_page = 1
    to_page = 1

    # END CONFIGURATION

    print("Starting video extraction process...")
    videos = fetch_videos_from_pages(base_url, start_with_name, from_page, to_page)
    
    # Output to JSON
    with open('videos.json', 'w', encoding='utf-8') as f:
        json.dump(videos, f, ensure_ascii=False, indent=4)
    
    print('Data saved to videos.json')

if __name__ == '__main__':
    main()
