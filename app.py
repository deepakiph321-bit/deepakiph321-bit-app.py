import streamlit as st
import yt_dlp
import pandas as pd
from datetime import datetime
import time

# Page Config
st.set_page_config(page_title="Audit Tool - VK Pro", layout="wide")

def format_duration(seconds):
    if not seconds or seconds == 'N/A': return "00-00-00"
    try: return time.strftime('%H-%M-%S', time.gmtime(float(seconds)))
    except: return "00-00-00"

def format_date(info):
    raw_date = info.get('upload_date')
    if not raw_date: return "00-00-0000 00-00-00"
    try:
        return datetime.strptime(raw_date, '%Y%m%d').strftime('%d-%m-%Y 00-00-00')
    except: return f"{raw_date} 00-00-00"

st.title("🛡️ Video Audit Dashboard")
st.write("Handling: **VKVideo (@handles), OK.ru, Dailymotion, etc.**")

video_url = st.text_input("Paste Video URL:", placeholder="https://vk.com/...")

if st.button("Start Extraction"):
    if video_url:
        with st.spinner('Fetching metadata...'):
            try:
                # Advanced Options for VK
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=False)
                    
                    # --- VK DATA LOGIC ---
                    uploader_name = info.get('uploader') or 'N/A'
                    uploader_id = str(info.get('uploader_id', ''))
                    
                    # Channel URL Logic: Handle vs ID
                    # Hum koshish karenge ki agar handle (@) available hai toh wo lein
                    c_url = info.get('uploader_url') or info.get('channel_url')
                    
                    # Agar Handle nahi mil raha, toh VKVideo ka standard handle format try karein
                    if uploader_name != 'N/A' and (not c_url or "public" in c_url):
                        # Cleaning name for potential handle (this is a guess logic)
                        clean_name = uploader_name.lower().replace(" ", "")
                        # But standard Numerical ID is safer if handle fails
                        if not c_url: c_url = f"https://vk.com/public{uploader_id.replace('-', '')}"

                    # Views & Subs
                    views = info.get('view_count') or info.get('playback_count') or 'N/A'
                    subs = info.get('channel_follower_count') or info.get('subscriber_count') or 'N/A'

                    # Formatting results
                    res = {
                        "Field": [
                            "Video Title", "Views", "Duration (HH-MM-SS)", 
                            "Likes", "Comment Count", "Upload Date (DD-MM-YYYY HH-MM-SS)", 
                            "Channel Name", "Channel URL", "Subscribers", "User Name"
                        ],
                        "Value": [
                            info.get('title', 'N/A'),
                            f"{views:,}" if isinstance(views, int) else views,
                            format_duration(info.get('duration')),
                            info.get('like_count', 'N/S'),
                            info.get('comment_count', 'N/A'),
                            format_date(info),
                            uploader_name,
                            c_url,
                            f"{subs:,}" if isinstance(subs, int) else subs,
                            uploader_id
                        ]
                    }

                    df = pd.DataFrame(res)
                    st.success("Target Extracted!")
                    st.table(df)
                    
                    # Download CSV
                    st.download_button("📥 Download Report", df.to_csv(index=False).encode('utf-8'), "audit_report.csv")

            except Exception as e:
                st.error(f"Cloud Restriction: {str(e)}")
                st.info("Tip: VK aur Bilibili aksar Streamlit ko block karte hain. Local machine setup se 100% result milenge.")
    else:
        st.warning("Please paste a URL.")
