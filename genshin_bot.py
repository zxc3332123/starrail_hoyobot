import os
import requests
import json

# --- 設定區 ---
StarRail_UID = "172534910"
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
MEMORY_FILE = "StarRail_memory.json"

def get_starrail_posts():
    """透過 API 抓取 HoYoLAB 上的貼文"""
    api_url = f"https://bbs-api-os.hoyolab.com/community/post/wapi/userPost?uid={StarRail_UID}"
    try:
        res = requests.get(api_url)
        data = res.json()
        if data.get("retcode") == 0:
            return data["data"]["list"]
    except Exception as e:
        print(f"抓取失敗: {e}")
    return []

# 1. 讀取舊紀錄
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r") as f:
        memory = json.load(f)
else:
    memory = {"last_id": ""}

# 2. 巡邏
posts = get_starrail_posts()
if posts:
    latest_post = posts[0]
    post_id = latest_post["post"]["post_id"]
    title = latest_post["post"]["subject"]
    # 優先抓封面圖，沒封面就抓第一張圖
    img_url = latest_post["post"]["cover"] or (latest_post["image_list"][0]["url"] if latest_post["image_list"] else "")
    link = f"https://www.hoyolab.com/article/{post_id}"

    # 3. 比對 ID，如果是新貼文
    if memory.get("last_id") != post_id:
        print(f"發現崩鐵新貼文: {title}")
        
        payload = {
            "embeds": [{
                "title": "🚂 《崩壞：星穹鐵道》最新情報",
                "description": f"「開拓者，快來看看三月拍到了什麼!📸」\n\n**{title}**",
                "url": link,
                "color": 16768768, 
                "image": {"url": img_url},
                "footer": {"text": "星鐵情報站 · 三月七攝影中"}
            }]
        }
        
        requests.post(WEBHOOK_URL, json=payload)
        
        # 更新紀錄
        memory["last_id"] = post_id
        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f)
