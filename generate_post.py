import os
import sys
import datetime
import requests
import re

from openai import OpenAI

def generate_post_content(topic, poe_api_key):
    prompt = f"""
Content: {topic}

The blog post should have the following structure:
- A summary of the article.
- An analysis of the article.
- A conclusion.
"""

    client = OpenAI(
        api_key=os.getenv("POE_API_KEY"),
        base_url="https://api.poe.com/v1"
    )
    
    completion = client.chat.completions.create(
        model="gpt-4", 
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024, # Increased max_tokens for potentially longer prompts with news
    )

    return completion.choices[0].message.content

def create_jekyll_post(topic, content):
    title = topic.replace("-", " ").title()
    seo_description = f"A blog post about {topic}."
    categories = ["AI Tools"]
    tags = ["AI"]

    # Generate filename
    today = datetime.datetime.now()
    filename_date = today.strftime("%Y-%m-%d")
    filename_title = title.lower().replace(" ", "-").replace(":", "").replace(",", "").replace("'", "")
    filename = f"{filename_date}-{filename_title}.md"

    # Construct front matter
    front_matter = f"""
---
layout: post
title: \"{title}\" 
date: {today.strftime("%Y-%m-%d %H:%M:%S %z")}
categories: {categories}
tags: {tags}
seo_title: \"{title}\" 
description: \"{seo_description}\" 
---

"""
    return filename, front_matter + content

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_post.py \"Your Blog Post Topic\"")
        sys.exit(1)

    blog_topic = sys.argv[1]
    poe_api_key = os.getenv("POE_API_KEY")

    if not poe_api_key:
        print("Error: POE_API_KEY environment variable not set.")
        sys.exit(1)

    print(f"Generating post for topic: {blog_topic}")
    try:
        generated_content = generate_post_content(blog_topic, poe_api_key)
        filename, full_content = create_jekyll_post(blog_topic, generated_content)

        posts_dir = "_posts"
        os.makedirs(posts_dir, exist_ok=True)
        filepath = os.path.join(posts_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(full_content)
        print(f"Successfully created post: {filepath}")
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Poe API: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
