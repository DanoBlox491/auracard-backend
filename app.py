from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import datetime
import os

app = Flask(__name__)
CORS(app) 

@app.route('/')
def home():
    return "AuraCard Python Backend is Running!"

@app.route('/api/roblox_stats', methods=['POST'])
def get_roblox_stats():
    data = request.json
    username = data.get('username')
    
    if not username:
        return jsonify({"error": "No username provided"}), 400

    try:
        # 1. Get User ID
        url = "https://users.roblox.com/v1/usernames/users"
        payload = {"usernames": [username], "excludeBannedUsers": True}
        res = requests.post(url, json=payload)
        user_data = res.json()
        
        if not user_data["data"]:
            return jsonify({"error": "Invalid or cracked username"}), 404
            
        user_id = user_data["data"][0]["id"]
        display_name = user_data["data"][0]["displayName"]

        # 2. Get Profile Data
        profile_url = f"https://users.roblox.com/v1/users/{user_id}"
        profile_res = requests.get(profile_url)
        profile_data = profile_res.json()
        
        # 3. Calculate Account Age
        created_date_str = profile_data.get("created", "")[:10] 
        created_date = datetime.datetime.strptime(created_date_str, "%Y-%m-%d")
        today = datetime.datetime.now()
        days_old = (today - created_date).days
        years_old = round(days_old / 365.25, 1)

        # 4. Get Followers Count
        followers_url = f"https://friends.roblox.com/v1/users/{user_id}/followers/count"
        followers_res = requests.get(followers_url)
        followers_count = followers_res.json().get("count", 0)

        # 5. Get Friends Count
        friends_url = f"https://friends.roblox.com/v1/users/{user_id}/friends/count"
        friends_res = requests.get(friends_url)
        friends_count = friends_res.json().get("count", 0)

        # 6. GET ROBLOX FULL BODY AVATAR IMAGE
        avatar_url = ""
        try:
            thumb_url = f"https://thumbnails.roblox.com/v1/users/avatar?userIds={user_id}&size=720x720&format=Png&isCircular=false"
            thumb_res = requests.get(thumb_url)
            thumb_data = thumb_res.json()
            if thumb_data["data"]:
                avatar_url = thumb_data["data"][0]["imageUrl"]
        except:
            pass

        # 7. THE ALGORITHM (Games Played & Won)
        hash_val = sum(ord(c) for c in username)
        games_played = int((years_old * 150) + (hash_val % 200) + 50)
        win_rate = 0.4 + ((hash_val % 20) / 100.0) 
        games_won = int(games_played * win_rate)

        # 8. Real Aura Score
        aura_score = int((years_old * 1000) + (followers_count * 5) + (friends_count * 10))
        
        if years_old >= 8:
            title = "OG Legend"
        elif aura_score >= 5000:
            title = "Roblox God"
        elif aura_score >= 2000:
            title = "Roblox Pro"
        else:
            title = "Roblox Player"

        return jsonify({
            "success": True,
            "username": username,
            "display_name": display_name,
            "years_old": years_old,
            "followers": followers_count,
            "friends": friends_count,
            "games_played": games_played,
            "games_won": games_won,
            "aura_score": aura_score,
            "title": title,
            "avatar_url": avatar_url,
            "description": profile_data.get("description", "No bio set.")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)