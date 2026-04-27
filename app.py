import streamlit as st
import yt_dlp
import pandas as pd
from datetime import datetime
import time

st.set_page_config(page_title="VK & Audit Pro Extractor", layout="wide")

def format_duration_custom(seconds):
    if not seconds or seconds == 'N/A': return "00-00-00"
    try: return time.strftime('%H-%M-%S', time.gmtime(float(seconds)))
    except: return "00-00-00"

def format_date_custom(info):
    raw_date = info.get('upload_date')
    if not raw_date: return "00-00-0000 00-00-00"
    try:
        date_obj = datetime.strptime(raw_date, '%Y%m%d')
        return date_obj.strftime('%d-%m-%Y 00-00-00')
    except: return f"{raw_date} 00-00-00"

st.title("🛡️ Advanced Video Auditor (VK/OK/Bilibili)")

video_url = st.text_input("Enter Video URL:", placeholder="https://vkvideo.ru/video-...")

if st.button("Extract Data"):
    if video_url:
        # VKVideo URL correction (Sometimes vkvideo.ru needs to be treated as vk.com)
        if "vkvideo.ru" in video_url:
            video_url = video_url.replace("vkvideo.ru", "vk.com")
            
        with st.spinner('Forcing extraction through platform firewalls...'):
            try:
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                    'add_header': ['Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'],
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=False)
                    
                    # --- VK SPECIFIC MAPPING ---
                    # Views: VK views are often in 'view_count' or 'repost_count'
                    v_count = info.get('view_count') or info.get('playback_count')
                    
                    # Subscribers: VK groups use 'follower_count'
                    subs = info.get('channel_follower_count') or info.get('uploader_count') or info.get('subscriber_count')
                    
                    # Channel URL & User Name
                    u_url = info.get('uploader_url') or info.get('channel_url')
                    u_id = info.get('uploader_id') or info.get('uploader')
                    
                    # Fallback for Channel URL if missing but ID exists
                    if not u_url and u_id:
                        if "vk.com" in video_url: u_url = f"https://vk.com/{u_id}"

                    res = {
                        "Field": ["Video Title", "Views", "Duration (HH-MM-SS)", "Likes", "Comments", "Upload Date", "Channel Name", "Channel URL", "Subscribers", "User Name"],
                        "Value": [
                            info.get('title', 'N/A'),
                            f"{v_count:,}" if isinstance(v_count, int) else v_count or 'N/A',
                            format_duration_custom(info.get('duration')),
                            info.get('like_count', 'N/A'),
                            info.get('comment_count', 'N/A'),
                            format_date_custom(info),
                            info.get('uploader', 'N/A'),
                            u_url or 'N/A',
                            f"{subs:,}" if isinstance(subs, int) else subs or 'N/A',
                            u_id or 'N/A'
                        ]
                    }

                    df = pd.DataFrame(res)
                    st.success("Extraction attempt finished!")
                    st.table(df)
                    st.download_button("📥 Download CSV", df.to_csv(index=False).encode('utf-8'), "audit.csv")

            except Exception as e:
                st.error(f"Cloud Blocked Error: {str(e)}")
                st.warning("VK/Instagram/Bilibili aksar Cloud IPs ko block karte hain. Niche wala 'Local Setup' try karein.")
