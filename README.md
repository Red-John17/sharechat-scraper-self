# Web Scraping Project - ShareChat Data Collector

## Introduction

This Python script is designed to scrape and collect data from ShareChat, focusing on posts, authors, likes, and followers. It utilizes Selenium WebDriver for browser automation to interact with the ShareChat web pages.

## Requirements

- Python 3.x
- Selenium
- WebDriver Manager
- pandas
- tqdm
- os
- json
- Docker (optional for containerized execution)

Ensure you have the above Python packages installed. You can install them using the `requirements.txt` file located in the project directory.

## Installation

1. **Clone the Repository**: Clone this repository to your local machine or download the source code.

2. **Install Dependencies**: Navigate to the directory where `requirements.txt` is located and run:

   ```
   pip install -r requirements.txt
   ```

3. **Docker (Optional)**: If you prefer using Docker, ensure Docker is installed on your system and use Docker Compose:
   ```
   docker compose up
   ```

## Usage

1. **Set Environment Variables**: The script sets the `DISPLAY` environment variable for the Selenium WebDriver. Ensure this is compatible with your system settings.

2. **Run the Script**: Execute the script using Python:

   ```
   python sharechat_scraper.py
   ```

3. **Data Collection**: The script navigates through ShareChat, collecting data about posts including author details, number of views, likes, and follower information.

## Features

- Navigates through ShareChat's trending Hindi page.
- Collects data from different post types (image, video, gif).
- Extracts detailed information about each post and its author.
- Retrieves like counts and detailed follower lists for users.
- Stores the collected data in a JSONL file for easy processing.

## Output

The script outputs a file named as specified in the `outputName` variable in the `constants.py` file. The output is in JSONL format, with each line representing data from a single post.

## Note

- The script is dependent on the structure of the ShareChat website. Changes to the site may require updates to the script.

## Output Structure

```py
curData = {
   "post_ph": post_ph,
   "author_name": author_name,
   "author_url": author_link,
   "author_id": authorID,
   "number_of_views": number_of_views,
   "years_before": years_before,
   "post_caption": pcText,
   "likes": likeCount,
   "comments": comments,
   "like_users": justLikes,
   "all_users": users,
   "followers": followers,
   "tag": tag_url
}
```

Each line in the `output.jsonl` file contains a JSON object with the above structure.
