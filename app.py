import streamlit as st
import yt_dlp
import pandas as pd
from datetime import datetime
import time
import re

st.set_page_config(page_title="Audit Tool - VK Fix", layout="wide")

def format_duration(seconds):
    if not seconds or seconds == 'N/A': return "00-00-00"
    return time.strftime('%H-%M-%S', time.gmtime(float(seconds)))

def format_date(info):
    raw_date = info.get('upload_date')
    if not raw_date: return "00-00-0000 00-00-00"
    try:
        return datetime.strptime(raw_date, '%Y%m%d').strftime('%d-%m-%Y 00-00-00')
    except: return f"{raw_date} 00-00-00"

st.title("🛡️ Video Metadata Extractor (VK Optimized)")

video_url = st.text_input("Paste Video URL:", placeholder="https://vkvideo.ru/video-...")

if st.button("Extract Data"):
    if video_url:
        with st.spinner('Accessing VK Servers...'):
            try:
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=False)
                    
                    # --- VK SPECIFIC LOGIC ---
                    uploader_id = str(info.get('uploader_id', ''))
                    uploader_name = info.get('uploader', 'N/A')
                    
                    # 1. Manual Channel URL Construction for VK
                    # Agar scraper @handle nahi de raha, toh numerical ID se link banayenge
                    c_url = info.get('uploader_url') or info.get('channel_url')
                    if not c_url or c_url == 'N/A':
                        if "vk" in video_url and uploader_id:
                            # VK mein negative ID ka matlab 'Club' ya 'Public' page hota hai
                            clean_id = uploader_id.replace('-', '')
                            c_url = f"https://vk.com/public{clean_id}"

                    # 2. Views & Subs
                    views = info.get('view_count') or info.get('playback_count') or 'N/A'
                    subs = info.get('channel_follower_count') or info.get('subscriber_count') or 'N/A'

                    res = {
                        "Field": [
                            "Video Title", "Views", "Duration (HH-MM-SS)", 
                            "Likes", "Comment Count", "Upload Date", 
                            "Channel Name", "Channel URL", "Subscribers", "User Name"
                        ],
                        "Value": [
                            info.get('title', 'N/A'),
                            f"{views:,}" if isinstance(views, int) else views,
                            format_duration(info.get('duration')),
                            info.get('like_count', 'N/A'),
                            info.get('comment_count', 'N/A'),
                            format_date(info),
                            uploader_name,
                            c_url,
                            f"{subs:,}" if isinstance(subs, int) else subs,
                            uploader_id
                        ]
                    }

                    df = pd.DataFrame(res)
                    st.success("Data Fetched!")
                    st.table(df)
                    st.download_button("📥 Download CSV", df.to_csv(index=False).encode('utf-8'), "vk_audit.csv")

            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("VK/Instagram aksar Streamlit ke servers ko block kar dete hain. Agar ye error baar-baar aaye, toh Local PC setup hi ekmatra solution hai.")
