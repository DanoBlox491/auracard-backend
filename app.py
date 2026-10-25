from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import datetime
import os
import urllib.parse

app = Flask(__name__)
CORS(app) 

# --- YOUTUBE API KEY ---
YT_API_KEY = os.environ.get("yt api key") 

@app.route('/')
def home():
    return "AuraCard Python Backend is Running!"


# =========================================================
#  🐷👑 SECRET EASTER EGG: TECHNOBLADE
# =========================================================
def is_technoblade(name):
    if not name:
        return False
    return str(name).strip().lstrip('@').lower() == "technoblade"


def make_technoblade_card(platform):
    base = {
        "success": True,
        "username": "Technoblade",
        "display_name": "Technoblade",
        "title": "NEVER DIES LEGEND",
        "description": "Technoblade never dies. 20,000 IQ. Potato King. Undefeated in the colosseum. One of us.",
        "aura_level": 9999,
        "avatar_url": "https://mc-heads.net/avatar/Technoblade/300"
    }
    if platform == "youtube":
        base["subs"] = 9999999
        base["views"] = 999999999
        base["aura_display"] = "∞"
    else:
        base["blocks_mined"] = "999,999,999"
        base["mobs_killed"] = "999,999,999"
        base["diamonds_found"] = "99,999,999"
        base["playtime"] = "99,999 Hours"
        base["aura_streak"] = "9999x Win Streak"
    return base


# --- ROBLOX ---
@app.route('/api/roblox_stats', methods=['POST'])
def get_roblox_stats():
    data = request.json
    username = data.get('username')
    manual_game = data.get('most_played_game', 'Rivals')
    
    try:
        manual_wins = int(float(data.get('games_won', 0) or 0))
    except (ValueError, TypeError):
        manual_wins = 0

    if not username: return jsonify({"error": "No username provided"}), 400

    try:
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

        if manual_wins > 0:
            games_won = manual_wins
            games_played = int(games_won / 0.65)
            aura_level = int((games_won / 10) + (years_old * 5)) + 10
        else:
            hash_val = sum(ord(c) for c in username)
            games_played = int((years_old * 150) + (hash_val % 200) + 50)
            games_won = int(games_played * 0.65)
            aura_level = int((games_won / 10) + (years_old * 5)) + 10

        if aura_level > 999: aura_level = 999
        aura_streak = f"{(games_won % 45) + 5}x Win Streak"

        if aura_level >= 100: title = "Roblox God"
        elif aura_level >= 50: title = "Roblox Legend"
        elif aura_level >= 20: title = "Roblox Pro"
        else: title = "Roblox Player"

        return jsonify({
            "success": True, "username": username, "display_name": display_name,
            "years_old": years_old, "friends": friends_count, "games_played": games_played,
            "games_won": games_won, "aura_level": aura_level, "aura_streak": aura_streak, 
            "most_played_game": manual_game, "title": title, "avatar_url": avatar_url, 
            "description": profile_data.get("description", "No bio set.")
        })
    except Exception as e: return jsonify({"error": str(e)}), 500


# --- MINECRAFT BEDROCK ---
@app.route('/api/bedrock_stats', methods=['POST'])
def get_bedrock_stats():
    data = request.json
    gamertag = data.get('username')
    if not gamertag: return jsonify({"error": "No gamertag provided"}), 400

    if is_technoblade(gamertag):
        return jsonify(make_technoblade_card("bedrock"))

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

    if not found_custom_skin: avatar_url = "https://mc-heads.net/body/MHF_Steve" 

    hash_val = sum(ord(c) for c in gamertag)
    aura_level = (hash_val % 80) + 10
    aura_streak = f"{(hash_val % 45) + 5}x Win Streak"
    
    # 🧱 REAL MINECRAFT STATS (Fake Algorithm)
    blocks_mined = (hash_val * 1337) % 2000000
    mobs_killed = (hash_val * 67) % 50000
    diamonds_found = (hash_val * 12) % 5000
    playtime = (hash_val % 800) + 100

    title = "Bedrock Legend" if aura_level > 70 else "Bedrock Pro" if aura_level > 40 else "Bedrock Player"

    return jsonify({
        "success": True, "username": gamertag, "display_name": gamertag,
        "aura_level": aura_level, "aura_streak": aura_streak, "title": title,
        "blocks_mined": f"{blocks_mined:,}", "mobs_killed": f"{mobs_killed:,}", 
        "diamonds_found": f"{diamonds_found:,}", "playtime": f"{playtime} Hours",
        "avatar_url": avatar_url, "description": "The Ultimate Bedrock Legend."
    })


# --- MINECRAFT JAVA ---
@app.route('/api/java_skin', methods=['POST'])
def get_java_skin():
    data = request.json
    username = data.get('username')
    if not username: return jsonify({"error": "No username provided"}), 400

    if is_technoblade(username):
        return jsonify(make_technoblade_card("java"))

    try:
        uuid_res = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
        if uuid_res.status_code != 200: return jsonify({"error": "Player not found"}), 404
        
        player_uuid = uuid_res.json().get("id")
        hash_val = sum(ord(c) for c in username)
        aura_level = (hash_val % 80) + 10
        aura_streak = f"{(hash_val % 45) + 5}x Win Streak"
        
        # 🧱 REAL MINECRAFT STATS (Fake Algorithm)
        blocks_mined = (hash_val * 1337) % 2000000
        mobs_killed = (hash_val * 67) % 50000
        diamonds_found = (hash_val * 12) % 5000
        playtime = (hash_val % 800) + 100

        title = "Java Legend" if aura_level > 70 else "Java Pro" if aura_level > 40 else "Java Player"

        return jsonify({
            "success": True, "username": username, "display_name": username,
            "aura_level": aura_level, "aura_streak": aura_streak, "title": title,
            "blocks_mined": f"{blocks_mined:,}", "mobs_killed": f"{mobs_killed:,}", 
            "diamonds_found": f"{diamonds_found:,}", "playtime": f"{playtime} Hours",
            "avatar_url": f"https://crafatar.com/renders/body/{player_uuid}?scale=6&overlay",
            "description": "The Ultimate Java Legend."
        })
    except Exception as e: return jsonify({"error": str(e)}), 500


# --- YOUTUBE ---
@app.route('/api/yt_stats', methods=['POST'])
def get_yt_stats():
    data = request.json
    raw = data.get('username') or ''
    if not raw: return jsonify({"error": "No handle provided"}), 400

    if is_technoblade(raw):
        return jsonify(make_technoblade_card("youtube"))

    handle = raw.replace('@', '').strip()
    
    try:
        res = requests.get(f"https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&forHandle={handle}&key={YT_API_KEY}")
        data = res.json()
        
        if "error" in data:
            err_msg = data["error"].get("message", "Unknown Google API Error")
            return jsonify({"error": f"YouTube API Error: {err_msg}"}), 500

        items = data.get("items", [])

        if not items:
            res = requests.get(f"https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&forUsername={handle}&key={YT_API_KEY}")
            data = res.json()
            items = data.get("items", [])

        if not items:
            search_res = requests.get(f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q={handle}&key={YT_API_KEY}&maxResults=1")
            search_data = search_res.json()
            search_items = search_data.get("items", [])
            if search_items:
                channel_id = search_items[0]["snippet"]["channelId"]
                res = requests.get(f"https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id={channel_id}&key={YT_API_KEY}")
                data = res.json()
                items = data.get("items", [])

        if not items: 
            return jsonify({"error": "YouTube channel not found. Try their exact @handle!"}), 404

        channel = items[0]
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
