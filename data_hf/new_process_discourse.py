import os
import json
import re
from datetime import datetime, timezone
from bs4 import BeautifulSoup

folder_path = r'C:\Users\ulaga\VSCODE101\my_project\TDS-Project1-Data\discourse_json'
output_file = r'C:\Users\ulaga\VSCODE101\my_project\TDS-Project1-Data\processed_discourse.jsonl'

start_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
end_date = datetime(2025, 4, 14, 23, 59, 59, tzinfo=timezone.utc)

def clean_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)
    text = re.sub(r'\s+', ' ', text)
    return text

with open(output_file, 'w', encoding='utf-8') as out_f:
    total_posts = 0
    included_posts = 0
    for filename in os.listdir(folder_path):
        if not filename.endswith('.json'):
            continue
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        posts = data.get('post_stream', {}).get('posts', [])

        for post in posts:
            total_posts += 1
            created_at_str = post.get('created_at')
            if not created_at_str:
                continue

            try:
                created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
            except Exception as e:
                print(f"Skipping post due to date parse error: {created_at_str} -> {e}")
                continue

            if not (start_date <= created_at <= end_date):
                continue

            cooked_html = post.get('cooked', '')
            if not cooked_html.strip():
                continue

            cleaned_text = clean_html(cooked_html)

            topic_id = post.get('topic_id')
            post_number = post.get('post_number')
            topic_slug = post.get('topic_slug')

            url_info = {
                'topic_id': topic_id,
                'post_number': post_number,
                'topic_slug': topic_slug,
            }

            out_obj = {
                'created_at': created_at_str,
                'text': cleaned_text,
                'url_info': url_info,
            }

            out_f.write(json.dumps(out_obj, ensure_ascii=False) + '\n')
            included_posts += 1

    print(f"Processed {total_posts} posts total.")
    print(f"Included {included_posts} posts within date range and content.")
