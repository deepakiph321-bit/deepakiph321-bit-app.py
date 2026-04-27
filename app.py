import streamlit as st
import yt_dlp
import pandas as pd
from datetime import datetime
import time

# Page Config
st.set_page_config(page_title="Horizontal Video Auditor", layout="wide")

def format_duration(seconds):
    """Seconds to HH-MM-SS"""
    if not seconds or seconds == 'N/A': return "00-00-00"
    try: return time.strftime('%H-%M-%S', time.gmtime(float(seconds)))
    except: return "00-00-00"

def format_date(info):
    """YYYYMMDD to DD-MM-YYYY HH-MM-SS"""
    raw_date = info.get('upload_date')
    if not raw_date: return "00-00-0000 00-00-00"
    try:
        return datetime.strptime(raw_date, '%Y%m%d').strftime('%d-%m-%Y 00-00-00')
    except: return f"{raw_date} 00-00-00"

st.title("🛡️ Anti-Piracy Data Dashboard (Horizontal)")
st.markdown("Supports: **VK, OK.ru, Dailymotion, Bilibili, Instagram, TikTok, Archive.org, etc.**")

# Input URL
video_url = st.text_input("Enter Video URL:", placeholder="Paste link here...")

if st.button("Extract Metadata"):
    if video_url:
        with st.spinner('Extracting horizontal data...'):
            try:
                # Headers to mimic browser and handle VK/Bilibili better
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                    'referer': 'https://www.google.com/',
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=False)
                    
                    # --- DATA EXTRACTION ---
                    title = info.get('title', 'N/A')
                    views = info.get('view_count') or info.get('playback_count') or 'N/A'
                    duration = format_duration(info.get('duration'))
                    likes = info.get('like_count', 'N/A')
                    comments = info.get('comment_count', 'N/A')
                    upload_date = format_date(info)
                    
                    # Channel Logic
                    channel_url = info.get('uploader_url') or info.get('channel_url') or 'N/A'
                    channel_name = info.get('uploader') or info.get('channel') or 'N/A'
                    subs = (info.get('channel_follower_count') or 
                            info.get('subscriber_count') or 
                            info.get('follower_count') or 'N/A')
                    username = info.get('uploader_id') or info.get('uploader') or 'N/A'

                    # --- CREATING HORIZONTAL DATA ---
                    row_data = {
                        "VideoURL": video_url,
                        "Video Title": title,
                        "Views": f"{views:,}" if isinstance(views, int) else views,
                        "Duration": duration,
                        "Likes": likes,
                        "CommentCount": comments,
                        "PostUploadDate": upload_date,
                        "Channel/Profile URL": channel_url,
                        "Channel/ProfileName": channel_name,
                        "Subscriber/Followers": f"{subs:,}" if isinstance(subs, int) else subs,
                        "Username": username
                    }

                    # Display in Table (Horizontal)
                    df = pd.DataFrame([row_data]) # Wrapping in list [] makes it horizontal
                    
                    st.success("Extraction Complete!")
                    st.dataframe(df) # Horizontal view with scroll
                    
                    # Download CSV
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Download Excel/CSV", csv, f"audit_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")

            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Reminder: Bilibili aur Instagram aksar Cloud (Streamlit) IPs ko block kar dete hain. Is case mein 'Local PC' par setup karein.")
    else:
        st.warning("Please paste a URL.")
