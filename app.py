import streamlit as st
import yt_dlp
import pandas as pd
from datetime import datetime
import time

# Page Config
st.set_page_config(page_title="Video Audit Tool Pro", layout="wide")

def format_duration_custom(seconds):
    """Seconds ko HH-MM-SS mein badalne ke liye"""
    if not seconds or seconds == 'N/A':
        return "00-00-00"
    try:
        # Convert seconds to HH-MM-SS with dashes
        return time.strftime('%H-%M-%S', time.gmtime(float(seconds)))
    except:
        return "00-00-00"

def format_date_custom(info):
    """Platform se date lekar DD-MM-YYYY HH-MM-SS mein badalne ke liye"""
    # yt-dlp usually provides 'upload_date' as YYYYMMDD
    raw_date = info.get('upload_date')
    if not raw_date or raw_date == 'N/A':
        return "00-00-0000 00-00-00"
    try:
        date_obj = datetime.strptime(raw_date, '%Y%m%d')
        return date_obj.strftime('%d-%m-%Y 00-00-00')
    except:
        return f"{raw_date} 00-00-00"

st.title("🛡️ Anti-Piracy Video Data Extractor")
st.write("Specialized for: **VKVideo, OK.ru, Dailymotion, Bilibili, and Social Media.**")

video_url = st.text_input("Paste Video URL:", placeholder="https://vkvideo.ru/video-...")

if st.button("Extract & Format Data"):
    if video_url:
        with st.spinner('Fetching metadata...'):
            try:
                # Headers to reduce blocking
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                    'referer': 'https://www.google.com/',
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=False)
                    
                    # --- ROBUST EXTRACTION LOGIC ---
                    
                    # 1. Views (Trying all possible keys for VK/OK.ru)
                    views = info.get('view_count') or info.get('playback_count') or 'N/A'
                    
                    # 2. Subscribers / Followers
                    subs = (info.get('channel_follower_count') or 
                            info.get('subscriber_count') or 
                            info.get('follower_count') or 'N/A')
                    
                    # 3. Channel URL
                    c_url = info.get('uploader_url') or info.get('channel_url') or 'N/A'
                    
                    # 4. Formatted Fields
                    duration_final = format_duration_custom(info.get('duration'))
                    date_final = format_date_custom(info)

                    # --- FINAL DATA STRUCTURE ---
                    res_data = {
                        "Field": [
                            "Video Title", 
                            "Views", 
                            "Duration (HH-MM-SS)", 
                            "Likes", 
                            "Comment Count", 
                            "Upload Date (DD-MM-YYYY HH-MM-SS)", 
                            "Channel Name", 
                            "Channel URL", 
                            "Subscribers", 
                            "User Name"
                        ],
                        "Value": [
                            info.get('title', 'N/A'),
                            views,
                            duration_final,
                            info.get('like_count', 'N/A'),
                            info.get('comment_count', 'N/A'),
                            date_final,
                            info.get('uploader', 'N/A'),
                            c_url,
                            subs,
                            info.get('uploader_id', 'N/A')
                        ]
                    }

                    df = pd.DataFrame(res_data)
                    st.success("Data Extracted Successfully!")
                    st.table(df)
                    
                    # Download CSV
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Audit CSV",
                        data=csv,
                        file_name=f"audit_report_{datetime.now().strftime('%d_%m_%Y')}.csv",
                        mime='text/csv',
                    )

            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Instagram/Bilibili Note: Agar 'URL Blocked' aa raha hai, toh Streamlit server block ho chuka hai. Local PC setup is recommended.")
    else:
        st.warning("Please paste a URL first.")
