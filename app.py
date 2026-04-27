import streamlit as st
import yt_dlp
import pandas as pd
from datetime import datetime
import time

# Page Configuration
st.set_page_config(page_title="Bulk Video Auditor", layout="wide")

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
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'referer': 'https://www.google.com/',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url.strip(), download=False)
            
            views = info.get('view_count') or info.get('playback_count') or 'N/A'
            subs = info.get('channel_follower_count') or info.get('subscriber_count') or info.get('follower_count') or 'N/A'
            
            c_url = info.get('uploader_url') or info.get('channel_url')
            if not c_url and 'vk' in url:
                u_id = str(info.get('uploader_id', '')).replace('-', '')
                c_url = f"https://vk.com/public{u_id}" if u_id else 'N/A'
            
            return {
                "VideoURL": url.strip(),
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
        return {"VideoURL": url.strip(), "Video Title": f"Error/Blocked", "Views": "N/A"}

# --- UI LAYOUT ---
st.title("🛡️ Anti-Piracy Bulk Extractor")
st.markdown("Niche box mein links paste karein (Max 100). Har line par ek link hona chahiye.")

# Text Area for pasting links
urls_text = st.text_area("Paste URLs here (one per line):", height=300, placeholder="https://vk.com/video...\nhttps://ok.ru/video...")

if st.button("Start Bulk Extraction"):
    # Split text into list and remove empty lines
    url_list = [u.strip() for u in urls_text.split('\n') if u.strip()]
    
    if not url_list:
        st.warning("Please paste some URLs first.")
    elif len(url_list) > 100:
        st.error(f"Limit exceeded! You pasted {len(url_list)} links. Please keep it under 100.")
    else:
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Process links
        for i, url in enumerate(url_list):
            status_text.text(f"Processing ({i+1}/{len(url_list)}): {url[:60]}...")
            data = extract_data(url)
            results.append(data)
            
            # Update progress
            progress_bar.progress((i + 1) / len(url_list))
            
            # Anti-ban delay (1.5s gap)
            time.sleep(1.5)
            
        # Create DataFrame
        final_df = pd.DataFrame(results)
        
        st.success(f"Successfully processed {len(url_list)} links!")
        
        # Display horizontal table
        st.dataframe(final_df)
        
        # Download Button
        csv = final_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Audit Report (CSV)",
            data=csv,
            file_name=f"bulk_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime='text/csv'
        )
