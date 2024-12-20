from selenium import webdriver
from bs4 import BeautifulSoup
import time
import pandas as pd

# Set up Selenium WebDriver
driver = webdriver.Chrome()

# Open the YouTube URL
driver.get("https://www.youtube.com/results?search_query=trending")

# Initialize lists to store data
video_urls = []
video_titles = []
channel_names = []
views = []
descriptions = []
video_durations = []

# Scroll and collect data
scroll_pause_time = 3
last_height = driver.execute_script("return document.documentElement.scrollHeight")
desired_count = 500

while len(video_urls) < desired_count:
    # Scroll down
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
    time.sleep(scroll_pause_time)

    # Parse the current page
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # Find video containers
    video_containers = soup.find_all('ytd-video-renderer', class_='style-scope ytd-item-section-renderer')

    for video in video_containers:
        # Extract video URL
        link_tag = video.find('a', class_='yt-simple-endpoint style-scope ytd-video-renderer')
        if link_tag:
            video_url = f"https://www.youtube.com{link_tag['href']}"

            # Avoid duplicates
            if video_url not in video_urls:
                video_urls.append(video_url)

                # Extract video title
                title = link_tag.get('title', 'No title available')
                video_titles.append(title)

                # Extract channel name
                channel_name_tag = video.find('a', class_='yt-simple-endpoint style-scope yt-formatted-string')
                channel_name = channel_name_tag.text if channel_name_tag else 'No channel name'
                channel_names.append(channel_name)

                # Extract views
                view_tag = video.find('span', class_='inline-metadata-item style-scope ytd-video-meta-block')
                view = view_tag.text if view_tag else 'No views'
                views.append(view)

                # Extract description
                description_tag = video.find('yt-formatted-string', class_='metadata-snippet-text-navigation style-scope ytd-video-renderer')
                description = description_tag.text if description_tag else 'No description available'
                descriptions.append(description)

                # Extract video duration
                duration_tag = video.find('span', class_='ytd-thumbnail-overlay-time-status-renderer')
                duration = duration_tag.text.strip() if duration_tag else 'No duration'
                video_durations.append(duration)

    # Break if no new content is loaded
    new_height = driver.execute_script("return document.documentElement.scrollHeight")
    if new_height == last_height:
        print("No new content loaded. Stopping scroll.")
        break
    last_height = new_height

    print(f"Collected {len(video_urls)} videos so far...")

# Ensure all lists are of equal length
min_length = min(len(video_urls), len(video_titles), len(channel_names), len(views), len(descriptions), len(video_durations))
video_urls = video_urls[:min_length]
video_titles = video_titles[:min_length]
channel_names = channel_names[:min_length]
views = views[:min_length]
descriptions = descriptions[:min_length]
video_durations = video_durations[:min_length]

# Create a DataFrame
data = {
    'Video URL': video_urls,
    'Title': video_titles,
    'Description': descriptions,
    'Channel Name': channel_names,
    'Views': views,
    'Duration': video_durations
}
df = pd.DataFrame(data)

# Save to CSV
output_file = "YouTube_Trending_500_Videos.csv"
df.to_csv(output_file, index=False)

print(f"Data has been saved to {output_file}")

# Close the browser
driver.quit()
