import os
import requests
import json

# --- 設定區 ---
GENSHIN_UID = "1015537" # 原神官方帳號 UID
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
MEMORY_FILE = "genshin_memory.json"

def get_genshin_posts():
    """透過 API 抓取 HoYoLAB 上的貼文"""
    api_url = f"https://bbs-api-os.hoyolab.com/community/post/wapi/userPost?uid={GENSHIN_UID}"
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
posts = get_genshin_posts()
if posts:
    latest_post = posts[0]
    post_id = latest_post["post"]["post_id"]
    title = latest_post["post"]["subject"]
    # 優先抓封面圖，沒封面就抓第一張圖
    img_url = latest_post["post"]["cover"] or (latest_post["image_list"][0]["url"] if latest_post["image_list"] else "")
    link = f"https://www.hoyolab.com/article/{post_id}"

    # 3. 比對 ID，如果是新貼文
    if memory.get("last_id") != post_id:
        print(f"發現原神新貼文: {title}")
        
        payload = {
            "embeds": [{
                "title": "🍀 《原神》HoYoLAB 最新情報",
                "description": f"「旅行者，派蒙給你帶新消息來了！派蒙要吃甜甜花釀雞啦！🤤」\n\n**{title}**",
                "url": link,
                "color": 65490, # 原神翠綠色
                "image": {"url": img_url},
                "footer": {"text": "提瓦特情報站 · 派蒙待命中"}
            }]
        }
        
        requests.post(WEBHOOK_URL, json=payload)
        
        # 更新紀錄
        memory["last_id"] = post_id
        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f)
