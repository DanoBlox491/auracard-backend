from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import datetime
import os
import urllib.parse

app = Flask(__name__)
CORS(app) 

@app.route('/')
def home():
    return "AuraCard Python Backend is Running!"

# --- ROBLOX ---
@app.route('/api/roblox_stats', methods=['POST'])
def get_roblox_stats():
    data = request.json
    username = data.get('username')
    manual_game = data.get('most_played_game', 'Rivals')
    manual_played = int(data.get('games_played', 0))

    if not username: return jsonify({"error": "No username provided"}), 400

    try:
        # 1. Fetch REAL Roblox Data (Bio, Friends, Avatar, Age)
        url = "https://users.roblox.com/v1/usernames/users"
        payload = {"usernames": [username], "excludeBannedUsers": True}
        res = requests.post(url, json=payload)
        user_data = res.json()
        
        if not user_data["data"]: return jsonify({"error": "Invalid or cracked username"}), 404
            
        user_id = user_data["data"][0]["id"]
        display_name = user_data["data"][0]["displayName"]

        profile_data = requests.get(f"https://users.roblox.com/v1/users/{user_id}").json()
        created_date = datetime.datetime.strptime(profile_data.get("created", "")[:10], "%Y-%m-%d")
        years_old = round((datetime.datetime.now() - created_date).days / 365.25, 1)

        friends_count = requests.get(f"https://friends.roblox.com/v1/users/{user_id}/friends/count").json().get("count", 0)

        avatar_url = ""
        try:
            thumb_data = requests.get(f"https://thumbnails.roblox.com/v1/users/avatar?userIds={user_id}&size=720x720&format=Png&isCircular=false").json()
            if thumb_data["data"]: avatar_url = thumb_data["data"][0]["imageUrl"]
        except: pass

        # 2. THE AURA ALGORITHM (Based on manual Games Played)
        if manual_played > 0:
            games_won = int(manual_played * 0.65) # Assume 65% win rate for the flex
            aura_level = int((games_won / 10) + (years_old * 5)) + 10
            if aura_level > 999: aura_level = 999
            aura_streak = f"{(games_won % 45) + 5}x Win Streak"
        else:
            games_won = 0
            aura_level = int(years_old * 10) + 10
            aura_streak = "0x Win Streak"

        # 3. Title Logic
        if aura_level >= 100: title = "Roblox God"
        elif aura_level >= 50: title = "Roblox Legend"
        elif aura_level >= 20: title = "Roblox Pro"
        else: title = "Roblox Player"

        return jsonify({
            "success": True, 
            "username": username, 
            "display_name": display_name,
            "years_old": years_old, 
            "friends": friends_count, 
            "games_played": manual_played,
            "games_won": games_won,
            "aura_level": aura_level, 
            "aura_streak": aura_streak, 
            "most_played_game": manual_game,
            "title": title,
            "avatar_url": avatar_url, 
            "description": profile_data.get("description", "No bio set.")
        })
    except Exception as e: return jsonify({"error": str(e)}), 500

# --- MINECRAFT BEDROCK ---
@app.route('/api/bedrock_stats', methods=['POST'])
def get_bedrock_stats():
    data = request.json
    gamertag = data.get('username')
    if not gamertag: return jsonify({"error": "No gamertag provided"}), 400

    encoded_gamertag = urllib.parse.quote(gamertag)
    avatar_url = ""
    found_custom_skin = False

    try:
        xuid_res = requests.get(f"https://api.geysermc.org/v2/xbox/xuid/{encoded_gamertag}", timeout=5)
        if xuid_res.status_code == 200:
            xuid = xuid_res.json().get("xuid")
            if xuid:
                skin_res = requests.get(f"https://api.geysermc.org/v2/skin/{xuid}", timeout=5)
                if skin_res.status_code == 200:
                    texture_id = skin_res.json().get("texture_id")
                    if texture_id:
                        avatar_url = f"https://mc-heads.net/body/{texture_id}"
                        found_custom_skin = True
    except: pass

    if not found_custom_skin:
        avatar_url = "https://mc-heads.net/body/MHF_Steve" 

    hash_val = sum(ord(c) for c in gamertag)
    aura_level = (hash_val % 80) + 10
    aura_streak = f"{(hash_val % 45) + 5}x Win Streak"
    title = "Bedrock Legend" if aura_level > 70 else "Bedrock Pro" if aura_level > 40 else "Bedrock Player"

    return jsonify({
        "success": True, "username": gamertag, "display_name": gamertag,
        "aura_level": aura_level, "aura_streak": aura_streak, "title": title,
        "avatar_url": avatar_url, "description": "The Ultimate Bedrock Legend."
    })

# --- MINECRAFT JAVA ---
@app.route('/api/java_skin', methods=['POST'])
def get_java_skin():
    data = request.json
    username = data.get('username')
    if not username: return jsonify({"error": "No username provided"}), 400

    try:
        uuid_res = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
        if uuid_res.status_code != 200: return jsonify({"error": "Player not found"}), 404
        
        player_uuid = uuid_res.json().get("id")
        hash_val = sum(ord(c) for c in username)
        aura_level = (hash_val % 80) + 10
        aura_streak = f"{(hash_val % 45) + 5}x Win Streak"
        title = "Java Legend" if aura_level > 70 else "Java Pro" if aura_level > 40 else "Java Player"

        return jsonify({
            "success": True, "username": username, "display_name": username,
            "aura_level": aura_level, "aura_streak": aura_streak, "title": title,
            "avatar_url": f"https://crafatar.com/renders/body/{player_uuid}?scale=6&overlay",
            "description": "The Ultimate Java Legend."
        })
    except Exception as e: return jsonify({"error": str(e)}), 500

# --- YOUTUBE ---
@app.route('/api/yt_stats', methods=['POST'])
def get_yt_stats():
    data = request.json
    handle = data.get('username').replace('@', '')
    if not handle: return jsonify({"error": "No handle provided"}), 400

    YT_API_KEY = "YOUR_YOUTUBE_API_KEY" 

    try:
        res = requests.get(f"https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&forHandle={handle}&key={YT_API_KEY}")
        data = res.json()

        if not data.get("items"): return jsonify({"error": "YouTube channel not found"}), 404

        channel = data["items"][0]
        snippet = channel["snippet"]
        stats = channel["statistics"]

        subs = int(stats.get("subscriberCount", 0))
        views = int(stats.get("viewCount", 0))
        aura_level = int((subs / 100) + (views / 2000)) + 1
        if aura_level > 999: aura_level = 999

        title = "Content God" if aura_level >= 100 else "Verified Legend" if aura_level >= 50 else "Pro Creator"

        return jsonify({
            "success": True, "username": handle, "display_name": snippet["title"],
            "aura_level": aura_level, "subs": subs, "views": views, "title": title,
            "avatar_url": snippet["thumbnails"]["high"]["url"], "description": snippet.get("description", "No bio set.")[:100]
        })
    except Exception as e: return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
