import streamlit as st
import yt_dlp
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Pro Audit Extractor", layout="wide")
st.title("📊 Multi-Platform Metadata Pro")

video_url = st.text_input("Enter Video URL:", placeholder="Paste link here...")

if st.button("Extract Data"):
    if video_url:
        with st.spinner('Accessing Platform Data...'):
            try:
                # Optimized Options for bypass and data extraction
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': False,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=False)
                    
                    # --- SMART MAPPING FOR ALL PLATFORMS ---
                    
                    # 1. Views (Targeting OK.ru & VK specifically)
                    views = info.get('view_count') or info.get('playback_count') or info.get('repost_count') or 'N/A'
                    
                    # 2. Channel/Profile URL (Handling Facebook/VK)
                    p_url = info.get('uploader_url') or info.get('channel_url') or info.get('webpage_url_basename')
                    if p_url and not p_url.startswith('http'):
                        # Agar sirf ID mili ho toh base URL lagana
                        if 'facebook.com' in video_url: p_url = f"https://facebook.com/{info.get('uploader_id')}"
                        elif 'vk.com' in video_url: p_url = f"https://vk.com/{info.get('uploader_id')}"
                    
                    # 3. Subscribers/Followers
                    subs = (info.get('channel_follower_count') or 
                            info.get('subscriber_count') or 
                            info.get('follower_count') or 
                            info.get('user_follower_count') or 'N/A')
                    
                    # 4. Channel Name
                    c_name = info.get('uploader') or info.get('channel') or info.get('author') or 'N/A'

                    # Data Table
                    res = {
                        "Field": ["Video Title", "Views", "Duration", "Likes", "Comments", "Upload Date", "Channel Name", "Channel URL", "Subscribers", "User ID"],
                        "Value": [
                            info.get('title', 'N/A'),
                            views,
                            f"{info.get('duration', 0)} sec",
                            info.get('like_count', 'N/A'),
                            info.get('comment_count', 'N/A'),
                            info.get('upload_date', 'N/A'),
                            c_name,
                            p_url if p_url else 'N/A',
                            subs,
                            info.get('uploader_id', 'N/A')
                        ]
                    }

                    df = pd.DataFrame(res)
                    st.success("Platform responded successfully!")
                    st.table(df)
                    
                    # Download CSV
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Download CSV", csv, f"audit_{info.get('id')}.csv", "text/csv")

            except Exception as e:
                st.error(f"Platform Error: {str(e)}")
                st.info("Tip: Bilibili/Instagram ke liye VPN ya Local machine par running script better hoti hai cloud ke muqable.")
    else:
        st.warning("Please paste a URL.")
