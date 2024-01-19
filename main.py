import streamlit as st
import pandas as pd
from langchain.document_loaders import YoutubeLoader
from langchain.chains.summarize import load_summarize_chain
from langchain import OpenAI
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import googleapiclient.discovery
import googleapiclient.errors
import PIL
# Path to your banner image (can be a local path or a URL)
banner_image = PIL.Image.open("C:\\Users\\rames\\OneDrive\\Desktop\\Logo\\Website.jpg")  # Replace with your image path

# Display the banner image
st.image(banner_image,width=None, use_column_width='always')

def get_videos(api_key, term, date_string):
    try:
        # Create a YouTube client
        youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey=api_key)

        # Search for videos
        search_request = youtube.search().list(
            part='snippet',
            q=term,
            order='viewCount',
            type='video',
            publishedAfter=date_string,
            maxResults=50
        )
        search_response = search_request.execute()

        # Extract video IDs
        video_ids = [item['id']['videoId'] for item in search_response['items']]

        # Get statistics for each video in a single request
        videos_request = youtube.videos().list(
            part="snippet,statistics",
            id=','.join(video_ids)
        )
        videos_response = videos_request.execute()

        # Process and return video data
        videos = []
        for item in videos_response['items']:
            video = {
                'title': item['snippet']['title'],
                'published_at': item['snippet']['publishedAt'],
                'description': item['snippet']['description'],
                'channel_title': item['snippet']['channelTitle'],
                'video_id': item['id'],
                'view_count': int(item['statistics']['viewCount']),
                'url': f'https://www.youtube.com/watch?v={item["id"]}'
            }
            videos.append(video)

        return videos

    except googleapiclient.errors.HttpError as e:
        print(f"HTTP error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return []



def get_transcript(video_url):
    """
    Retrieves the transcript of a YouTube video.

    Args:
    video_url (str): The URL of the YouTube video.

    Returns:
    dict: A dictionary containing the transcript and video information, or
    None if the transcript could not be retrieved.
    """
    # Validate the video URL (basic validation assuming it's a YouTube URL)
    if not video_url.startswith("https://www.youtube.com/watch"):
        print("Invalid YouTube URL.")
        return None

    try:
        loader = YoutubeLoader.from_youtube_url(video_url, add_video_info=True)
        return loader.load()
    except Exception as e:
        print(f"An error occurred while fetching the transcript: {e}")
        return None
        

def fetch_videos(api_key, search_term, date_string):
    try:
        return get_videos(api_key, search_term, date_string)
    except Exception as e:
        st.error(f"Error fetching videos: {e}")
        return []

def fetch_transcript(url):
    try:
        return get_transcript(url)
    except Exception as e:
        st.error(f"Error fetching transcript: {e}")
        return None

def display_top_videos(videos):
    df = pd.DataFrame(videos)
    df = df.sort_values('view_count', ascending=False).head(3)  # Top 3 videos
    st.subheader('Top 3 Videos')
    st.table(df[['title', 'url', 'view_count']])
    return df

def main():
    st.title('QuickVid Summarizer: YouTube Content at a Glance')
    st.markdown("## Please input your API keys")
    date_string = (datetime.now() - timedelta(days=5)).isoformat("T") + "Z"

    youtube_api_key = st.text_input("Insert your YouTube API key here", type="password")
    openai_api_key = st.text_input("Insert your OpenAI API key here", type="password")

    if st.button('Submit'):
        st.session_state['api_keys'] = {'youtube': youtube_api_key, 'openai': openai_api_key}

    if 'api_keys' in st.session_state:
        search_term = st.text_input('Enter search term', 'AI news')

        if st.button('Search'):
            with st.spinner('Fetching Videos...'):
                st.session_state['videos'] = fetch_videos(st.session_state['api_keys']['youtube'], search_term, date_string)

        if st.session_state.get('videos'):
            df = display_top_videos(st.session_state['videos'])
            selected_video_url = st.selectbox("Select a video for transcript:", df['url'])

            if st.button('Get Transcript'):
                with st.spinner('Fetching Transcript...'):
                    transcript = fetch_transcript(selected_video_url)
                    if transcript:
                        st.session_state['transcript'] = transcript

        if st.session_state.get('transcript'):
            llm = OpenAI(openai_api_key=st.session_state['api_keys']['openai'], temperature=0.5)
            chain = load_summarize_chain(llm, chain_type="map_reduce")
            summary = chain.run(st.session_state['transcript'])
            st.subheader('Summary')
            st.write(summary)

if __name__ == "__main__":
    main()