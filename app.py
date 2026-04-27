import streamlit as st
import yt_dlp
import pandas as pd
from datetime import datetime
import time

# Page Config
st.set_page_config(page_title="Pro Audit Tool - Ok.ru Fix", layout="wide")

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

st.title("🛡️ Anti-Piracy Dashboard (Horizontal)")
st.markdown("Special Fix for: **Ok.ru, VK, Bilibili, and Dailymotion**")

video_url = st.text_input("Enter Video URL:", placeholder="Paste link here...")

if st.button("Extract Metadata"):
    if video_url:
        with st.spinner('Scanning Platform... Please wait.'):
            try:
                # Advanced Options specifically for Russian & Chinese platforms
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                    'referer': 'https://ok.ru/',
                    'extract_flat': False,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=False)
                    
                    # --- OK.RU & VK SPECIFIC MAPPING ---
                    # Views fallback
                    views = info.get('view_count') or info.get('playback_count') or info.get('repost_count') or 'N/A'
                    
                    # Channel Name fallback
                    c_name = info.get('uploader') or info.get('channel') or info.get('creator') or 'N/A'
                    
                    # Channel URL fallback (Building manually for OK.ru if missing)
                    c_url = info.get('uploader_url') or info.get('channel_url')
                    if not c_url or c_url == 'N/A':
                        u_id = info.get('uploader_id')
                        if u_id and 'ok.ru' in video_url:
                            c_url = f"https://ok.ru/profile/{u_id}" if u_id.isdigit() else f"https://ok.ru/{u_id}"

                    # Subscribers/Followers fallback
                    subs = (info.get('channel_follower_count') or 
                            info.get('subscriber_count') or 
                            info.get('follower_count') or 'N/A')

                    # --- ROW DATA (HORIZONTAL) ---
                    row_data = {
                        "VideoURL": video_url,
                        "Video Title": info.get('title', 'N/A'),
                        "Views": f"{views:,}" if isinstance(views, int) else views,
                        "Duration": format_duration(info.get('duration')),
                        "Likes": info.get('like_count', 'N/A'),
                        "CommentCount": info.get('comment_count', 'N/A'),
                        "PostUploadDate": format_date(info),
                        "Channel/Profile URL": c_url or 'N/A',
                        "Channel/ProfileName": c_name,
                        "Subscriber/Followers": f"{subs:,}" if isinstance(subs, int) else subs,
                        "Username": info.get('uploader_id') or 'N/A'
                    }

                    df = pd.DataFrame([row_data])
                    st.success("Target Extracted Successfully!")
                    st.dataframe(df) # Horizontal view
                    
                    # CSV Download
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Download Row as CSV", csv, "audit_row.csv", "text/csv")

            except Exception as e:
                st.error(f"Platform Blocked: {str(e)}")
                st.info("Tip: Agar Ok.ru ya Bilibili 'N/A' dikhaye, toh iska matlab Cloud IP ban hai. Local PC setup is highly recommended.")
    else:
        st.warning("Please paste a URL.")
