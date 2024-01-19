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
import google.generativeai as genai

# Import Markdown display for rendering generated content
from IPython.display import Markdown

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
        st.write(f"An error occurred while fetching the transcript: {e}")
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
import textwrap

def split_text_to_multiline(text, max_line_length):
    return '\n'.join(textwrap.wrap(text, max_line_length))

def display_top_videos(videos):
    df = pd.DataFrame(videos)
    st.write(df)
    #df = df.sort_values('view_count', ascending=False)  # Top 3 videos
    #st.write(df)
    df1 = df.sort_values('view_count', ascending=False).head(3)
    st.subheader('Top 3 Videos')
    st.table(df1[['title', 'url', 'view_count']])
    return df1

def main():
    st.title('QuickVid Summarizer: YouTube Content at a Glance')
    st.sidebar.markdown("## Please input your API keys")
    date_string = (datetime.now() - timedelta(days=5)).isoformat("T") + "Z"
    # Create a list of activity options for selection
    activity = ['OpenAI', 'GeminiPro']

    # Use Streamlit's sidebar to allow users to select the model type
    choice = st.sidebar.selectbox("Select Model type", activity)

    youtube_api_key = st.sidebar.text_input("Insert your YouTube API key here", type="password")
    openai_api_key = st.sidebar.text_input("Insert your "+choice+"  API key here", type="password")




    if st.sidebar.button('Submit'):
        st.session_state['api_keys'] = {'youtube': youtube_api_key, 'openai': openai_api_key}

    if 'api_keys' in st.session_state:
        search_term = st.text_input('Enter a keyword or phrase to search for YouTube videos:', 'LLM news')

        if st.button('Search'):
            with st.spinner('Fetching Videos...'):
                st.session_state['videos'] = fetch_videos(st.session_state['api_keys']['youtube'], search_term, date_string)
                
        if st.session_state.get('videos'):
            df = display_top_videos(st.session_state['videos'])
            selected_video_url = st.selectbox("Select a video for transcript:", df['url'])

            if st.button('Get Transcript'):
                
                with st.spinner('Fetching Transcript...'):
                    
                    transcript = fetch_transcript(selected_video_url)
                    docs = list(transcript)
                    # Initialize an empty list to store extracted data
                    data = []

                    # Iterate over the list and extract data
                    for doc in docs:
                        data.append({
                            "Page Content": doc.page_content,
                            "Source": doc.metadata['source'],
                            "Title": doc.metadata['title'],
                            "Description": doc.metadata['description'],
                            "View Count": doc.metadata['view_count'],
                            "Thumbnail URL": doc.metadata['thumbnail_url'],
                            "Publish Date": doc.metadata['publish_date'],
                            "Length": doc.metadata['length'],
                            "Author": doc.metadata['author']
                        })
                    
                    # Creating DataFrame
                    
                    df = pd.DataFrame(data)
 
                    # Display DataFrame in Streamlit
                    st.write(df)
                    st.write(transcript)
                    if transcript:
                        
                        st.session_state['transcript'] = transcript

        if st.session_state.get('transcript'):
            
            if choice == 'GeminiPro':
                prompt = f"Summarize the following text: {st.session_state['transcript']}"
                genai.configure(api_key = st.session_state['api_keys']['openai'])
                # Initialize the text-based GenerativeModel with "gemini-pro"
                model = genai.GenerativeModel("gemini-pro")
                # Generate content based on the user's text prompt
                response = model.generate_content(prompt)       
                # Display the generated content as Markdown
                summary = response.text
                
            elif choice == 'OpenAI':
            
                llm = OpenAI(openai_api_key=st.session_state['api_keys']['openai'], temperature=0.5)
                chain = load_summarize_chain(llm, chain_type="map_reduce")
                summary = chain.run(st.session_state['transcript'])
            
            
            st.subheader('Summary')
            st.markdown(summary)

if __name__ == "__main__":
    main()