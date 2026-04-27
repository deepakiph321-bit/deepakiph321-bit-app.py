import streamlit as st
import yt_dlp
import pandas as pd
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="Video Audit Extractor", layout="wide")

st.title("📊 Multi-Platform Video Metadata Extractor")
st.markdown("Supported domains: **VK, OK.ru, Dailymotion, Bilibili, Archive.org, Vimeo, etc.**")

# Input for URL
video_url = st.text_input("Enter Video URL:", placeholder="https://www.bilibili.tv/video/...")

if st.button("Extract Data"):
    if video_url:
        with st.spinner('Fetching details... Please wait.'):
            try:
                # yt-dlp Configuration
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': False,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=False)
                    
                    # --- ADVANCED DATA EXTRACTION (WITH FALLBACKS) ---
                    
                    # Views extraction
                    views = info.get('view_count') or info.get('concurrent_view_count') or 'N/A'
                    
                    # Profile URL extraction
                    profile_url = info.get('channel_url') or info.get('uploader_url') or info.get('user_url') or 'N/A'
                    
                    # Subscribers extraction
                    subs = info.get('channel_follower_count') or info.get('subscriber_count') or info.get('follower_count') or 'N/A'
                    
                    # Channel Name extraction
                    channel_name = info.get('uploader') or info.get('channel') or info.get('creator') or 'N/A'

                    # Upload Date Formatting
                    raw_date = info.get('upload_date', 'N/A')
                    formatted_date = raw_date
                    if raw_date != 'N/A' and len(raw_date) == 8: # Convert YYYYMMDD to YYYY-MM-DD
                        formatted_date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"

                    # Data Structure
                    data = {
                        "Field": [
                            "Video Title", "Views", "Duration (sec)", "Likes", 
                            "Comment Count", "Post Upload Date", "Channel/Profile Name", 
                            "Channel/Profile URL", "Subscribers", "User Name"
                        ],
                        "Value": [
                            info.get('title', 'N/A'),
                            views,
                            info.get('duration', 'N/A'),
                            info.get('like_count', 'N/A'),
                            info.get('comment_count', 'N/A'),
                            formatted_date,
                            channel_name,
                            profile_url,
                            subs,
                            info.get('uploader_id', 'N/A')
                        ]
                    }

                    # Show data in a table
                    df = pd.DataFrame(data)
                    st.success("Data Extracted Successfully!")
                    st.table(df)

                    # Create CSV for download
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Data as CSV",
                        data=csv,
                        file_name=f"audit_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime='text/csv',
                    )

            except Exception as e:
                st.error(f"Error: Data fetch nahi ho paya. Platform ne block kiya hoga ya URL galat hai. \n\nDetails: {str(e)}")
    else:
        st.warning("Please paste a URL first.")
