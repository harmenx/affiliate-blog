import os
import sys
import datetime
import requests
import re

from openai import OpenAI

def generate_review_content(product_name, poe_api_key):
    prompt = f"""
Write an affiliate review for the product: {product_name}.

The review should have the following structure:
- Product Name: {product_name}
- Rating: [e.g., 4.5/5]
- A brief introduction to the product.
- Key Features:
  - Feature 1: Description
  - Feature 2: Description
  - Feature 3: Description
- Pros:
  - Pro 1
  - Pro 2
- Cons:
  - Con 1
  - Con 2
- Conclusion: A summary of the review and a recommendation.
- Affiliate Link: [YOUR_AFFILIATE_LINK_HERE]
- Image: [PRODUCT_IMAGE_URL_HERE]
"""

    client = OpenAI(
        api_key=os.getenv("POE_API_KEY"),
        base_url="https://api.poe.com"
    )
    
    completion = client.chat.completions.create(
        model="gpt-4", 
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
    )

    return completion.choices[0].message.content

def create_jekyll_review_post(product_name, content):
    # Extract details from the generated content
    rating_match = re.search(r"Rating: \[?([\d.]+\/\d)\]?", content)
    affiliate_link_match = re.search(r"Affiliate Link: (.*)", content)
    image_match = re.search(r"Image: (.*)", content)

    rating = rating_match.group(1) if rating_match else "N/A"
    affiliate_link = affiliate_link_match.group(1).strip() if affiliate_link_match else ""
    image_url = image_match.group(1).strip() if image_match else ""

    title = f"Review: {product_name}"
    seo_description = f"An in-depth review of {product_name}, including features, pros, cons, and our rating."
    categories = ["Product Reviews"]
    tags = [product_name.replace(" ", "-").lower(), "review"]

    # Generate filename
    today = datetime.datetime.now()
    filename_date = today.strftime("%Y-%m-%d")
    filename_title = product_name.lower().replace(" ", "-").replace(":", "").replace(",", "").replace("'", "")
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
product_name: \"{product_name}\"
rating: \"{rating}\"
affiliate_link: \"{affiliate_link}\"
image: \"{image_url}\"
---

"""
    # Remove the extracted lines from the content
    content_without_details = re.sub(r"Rating: \[?[\d.]+\/\d\]?\n", "", content)
    content_without_details = re.sub(r"Affiliate Link: .*\n", "", content_without_details)
    content_without_details = re.sub(r"Image: .*\n", "", content_without_details)

    return filename, front_matter + content_without_details

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_post.py \"Product Name\"")
        sys.exit(1)

    product_name = sys.argv[1]
    poe_api_key = os.getenv("POE_API_KEY")

    if not poe_api_key:
        print("Error: POE_API_KEY environment variable not set.")
        sys.exit(1)

    print(f"Generating review for product: {product_name}")
    try:
        generated_content = generate_review_content(product_name, poe_api_key)
        filename, full_content = create_jekyll_review_post(product_name, generated_content)

        posts_dir = "_posts"
        os.makedirs(posts_dir, exist_ok=True)
        filepath = os.path.join(posts_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(full_content)
        print(f"Successfully created review post: {filepath}")
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Poe API: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
