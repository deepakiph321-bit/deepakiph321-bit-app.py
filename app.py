import streamlit as st
import yt_dlp
import pandas as pd
from datetime import datetime
import time

# Page Configuration
st.set_page_config(page_title="Cloud Audit Pro (100 Limit)", layout="wide")

def format_duration(seconds):
    if not seconds or seconds == 'N/A': return "00-00-00"
    try: return time.strftime('%H-%M-%S', time.gmtime(float(seconds)))
    except: return "00-00-00"

def format_date(info):
    raw_date = info.get('upload_date')
    if not raw_date: return "00-00-0000 00-00-00"
    try: return datetime.strptime(raw_date, '%Y%m%d').strftime('%d-%m-%Y 00-00-00')
    except: return f"{raw_date} 00-00-00"

def extract_data(url):
    """Main extraction function with multiple fallbacks"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'referer': 'https://www.google.com/',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Views & Subs mapping
            views = info.get('view_count') or info.get('playback_count') or 'N/A'
            subs = info.get('channel_follower_count') or info.get('subscriber_count') or info.get('follower_count') or 'N/A'
            
            # URL & Name logic
            c_url = info.get('uploader_url') or info.get('channel_url')
            if not c_url and 'vk' in url:
                u_id = str(info.get('uploader_id', '')).replace('-', '')
                c_url = f"https://vk.com/public{u_id}" if u_id else 'N/A'
            
            return {
                "VideoURL": url,
                "Video Title": info.get('title', 'N/A'),
                "Views": views,
                "Duration": format_duration(info.get('duration')),
                "Likes": info.get('like_count', 'N/A'),
                "CommentCount": info.get('comment_count', 'N/A'),
                "PostUploadDate": format_date(info),
                "Channel/Profile URL": c_url or 'N/A',
                "Channel/ProfileName": info.get('uploader') or info.get('channel') or 'N/A',
                "Subscriber/Followers": subs,
                "Username": info.get('uploader_id', 'N/A')
            }
    except Exception as e:
        return {"VideoURL": url, "Video Title": f"Error: {str(e)[:50]}...", "Views": "Blocked/Error"}

# --- UI LAYOUT ---
st.title("🛡️ Cloud Audit Tool (100 URLs Bulk)")
st.info("Note: Ek saath 100 links tak process kar sakte hain. Har link ke beech 1.5s ka gap rakha gaya hai safety ke liye.")

tab1, tab2 = st.tabs(["Manual Link Check", "Bulk Process (Max 100)"])

with tab1:
    url_input = st.text_input("Enter Video URL:")
    if st.button("Check Single"):
        if url_input:
            data = extract_data(url_input)
            st.dataframe(pd.DataFrame([data]))
        else:
            st.warning("Please enter a URL")

with tab2:
    st.write("Excel ya CSV file upload karein jisme 'url' naam ka column ho.")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    
    if uploaded_file:
        df_in = pd.read_csv(uploaded_file)
        # Limit check
        if len(df_in) > 100:
            st.error("Limit exceeded! Please upload a file with maximum 100 URLs.")
        else:
            if st.button("Start Bulk Extraction"):
                results = []
                bar = st.progress(0)
                status_text = st.empty()
                
                for i, url in enumerate(df_in['url']):
                    status_text.text(f"Processing ({i+1}/{len(df_in)}): {url[:50]}...")
                    results.append(extract_data(url))
                    bar.progress((i + 1) / len(df_in))
                    time.sleep(1.5) # Anti-ban delay
                
                final_df = pd.DataFrame(results)
                st.success("Extraction Complete!")
                st.dataframe(final_df)
                
                # Download
                csv = final_df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Audit Report", csv, "bulk_report.csv", "text/csv")
