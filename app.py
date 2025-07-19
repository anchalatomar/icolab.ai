from flask import Flask, request, jsonify
from openai import OpenAI
import instaloader
import re
from collections import Counter

app = Flask(__name__)
client = OpenAI(api_key="sk-...")  # Replace with your real OpenAI API key

def extract_username(instagram_url):
    match = re.search(r"instagram\.com/([^/?#]+)", instagram_url)
    return match.group(1) if match else None

@app.route("/analyze", methods=["POST"])
def analyze_profile():
    data = request.json
    profile_url = data.get("profile_url")

    if not profile_url:
        return jsonify({"error": "No profile_url provided"}), 400

    username = extract_username(profile_url)
    if not username:
        return jsonify({"error": "Invalid Instagram URL"}), 400

    try:
        loader = instaloader.Instaloader()
        profile = instaloader.Profile.from_username(loader.context, username)

        # Basic profile data
        profile_data = {
            "username": profile.username,
            "full_name": profile.full_name,
            "biography": profile.biography,
            "followers": profile.followers,
            "followees": profile.followees,
            "posts": profile.mediacount,
            "external_url": profile.external_url,
            "is_verified": profile.is_verified,
            "is_private": profile.is_private,
            "profile_pic_url": str(profile.profile_pic_url)
        }

        # Post data
        posts = profile.get_posts()
        post_count = 0
        total_likes = 0
        total_comments = 0
        all_hashtags = []
        mentions = []

        for post in posts:
            if post_count >= 5:
                break
            total_likes += post.likes
            total_comments += post.comments
            all_hashtags.extend(post.caption_hashtags)
            mentions.extend(post.mentions)
            post_count += 1

        avg_likes = total_likes // post_count if post_count > 0 else 0
        avg_comments = total_comments // post_count if post_count > 0 else 0
        top_hashtags = [tag for tag, _ in Counter(all_hashtags).most_common(5)]

        print("📊 Profile:", profile_data)
        print("👍 Avg Likes:", avg_likes)
        print("💬 Avg Comments:", avg_comments)
        print("🏷️ Top Hashtags:", top_hashtags)

        # Estimated metrics
        estimated_engagement_rate = "2.5%"
        estimated_impressions = int(profile_data["followers"] * 0.6)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a creator monetization strategist. Based on the Instagram profile and post data, create a report that includes:\n\n"
                    "1. **Profile Summary** (username, followers, posts, engagement rate, avg likes/comments, and impressions)\n"
                    "2. **Top Hashtags** with 1-line insights on what they reveal about the content or community\n"
                    "3. **Monetization Suggestions** — 3 specific ideas with:\n"
                    "- Name of the product/service\n"
                    "- 🎯 Target audience\n"
                    "- 💰 Suggested price (USD, EUR, INR)\n\n"
                    "Use markdown-style formatting and emojis for clarity. Keep it sharp, relevant, and insight-driven."
                )
            },
            {
                "role": "user",
                "content": f"""
Username: {profile_data['username']}
Full Name: {profile_data['full_name']}
Bio: {profile_data['biography']}
Followers: {profile_data['followers']}
Following: {profile_data['followees']}
Posts: {profile_data['posts']}
Profile URL: {profile_data['external_url']}
Verified: {profile_data['is_verified']}
Private: {profile_data['is_private']}
Profile Pic: {profile_data['profile_pic_url']}

Average Likes: {avg_likes}
Average Comments: {avg_comments}
Estimated Engagement Rate: {estimated_engagement_rate}
Estimated Impressions: {estimated_impressions}
Top Hashtags: {', '.join(top_hashtags)}
Mentions: {', '.join(mentions)}
"""
            }
        ]

        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7
        )

        result = response.choices[0].message.content
        print("🧠 GPT Response:", result)
        return jsonify({ "result": result })

    except Exception as e:
        print("🔥 Error:", str(e))
        return jsonify({ "error": str(e) }), 500

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)

