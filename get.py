import requests
from bs4 import BeautifulSoup
import json
import re

# Function to get the HTML content of a URL
def get_html(url):
    response = requests.get(url)
    response.raise_for_status()  # Raises an HTTPError for bad responses
    return response.text

# Function to extract video details from the HTML
def extract_video_details(html):
    soup = BeautifulSoup(html, 'html.parser')
    videos = []
    
    video_cells = soup.find_all('div', class_='video_cell')
    for cell in video_cells:
        video = {}
        video['url'] = 'https://video.sibnet.ru' + cell.find('span', itemprop='url')['content']
        video['thumbnail'] = cell.find('span', itemprop='contentUrl')['content']
        video['name'] = cell.find('span', itemprop='name').text
        
        # Extract video ID from thumbnail URL and construct a new video URL
        thumbnail_url = video['thumbnail']
        match = re.search(r'video_(\d+)_', thumbnail_url)
        if match:
            video_id = match.group(1)
            video['new_video_url'] = f'https://video.sibnet.ru/shell.php?videoid={video_id}'
        
        videos.append(video)
    
    return videos

# Function to iterate through multiple pages of video listings
def fetch_videos_from_pages(base_url, start_page, end_page):
    all_videos = []
    for page in range(start_page, end_page + 1):
        full_url = f"{base_url}?page={page}" if page > 1 else base_url  # Append page query only if it's not the first page
        html = get_html(full_url)
        video_details = extract_video_details(html)
        if not video_details:  # No more videos found, stop fetching more pages
            break
        all_videos.extend(video_details)
    return all_videos

# Main function to run the script
def main():
    base_url = 'https://video.sibnet.ru/alb678251-JJK/'  # Adjusted to your example
    videos = fetch_videos_from_pages(base_url, 1, 1)  # Example: Fetch from page 1 to 5
    
    # Output to JSON
    with open('videos.json', 'w', encoding='utf-8') as f:
        json.dump(videos, f, ensure_ascii=False, indent=4)
    
    print('Data saved to videos.json')

if __name__ == '__main__':
    main()
