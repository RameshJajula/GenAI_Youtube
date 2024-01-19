# QuickVid Summarizer: YouTube Content at a Glance

QuickVid Summarizer is an innovative web application designed to streamline the way users interact with YouTube content. Utilizing the power of Python and Streamlit, this tool not only fetches YouTube videos based on user-defined search terms but also provides concise, AI-generated summaries of their transcripts. It's an ideal solution for those seeking quick insights from video content without the need to watch entire videos.

## Features

- **API Integration:** Seamlessly integrates with YouTube's API to fetch videos and OpenAI's API for transcript summarization.
  
- **Search Functionality:** Allows users to search for YouTube videos using custom search terms.
  
- **Top Video Selection:** Displays the top 3 videos sorted by view count for any given search term.
  
- **Transcript Extraction:** Retrieves and displays the transcript of selected YouTube videos.
  
- **AI-Powered Summarization:** Utilizes OpenAI's advanced language models to generate brief, accurate summaries of video transcripts.
  
- **User-Friendly Interface:** Built with Streamlit, the application boasts an intuitive and interactive user interface.

  
## How It Works

- **API Key Input:** Users start by entering their YouTube and OpenAI API keys.
  
- **Video Search:** Users can search for videos using keywords.
  
- **Video Display:** The application lists the top 3 videos based on the search term.
  
- **Transcript and Summary:** For the selected video, the app fetches the transcript and displays a summarized version of the content.
  
## Use Cases

- **Educational:** Quickly gather key points from educational videos or lectures.
  
- **Research:** Efficiently collate information from various sources for research purposes.
  
- **Content Creation:** Analyze popular video content to strategize future content creation.
  
- **Accessibility:** Assist users with hearing disabilities by providing written summaries of video content.


## Installation

To set up QuickVid Summarizer on your local machine:

1. Clone the repository:

2. Navigate to the project directory:

3. Install the required dependencies:


## Usage

To run QuickVid Summarizer:

1. Start the Streamlit server:
   - streamlit run app.py
2. Open your web browser and go to `http://localhost:8501`.

## Configuration

Enter your YouTube and OpenAI API keys in the provided input fields to enable video fetching and transcript summarization.

## Contributing

Contributions are welcome!

## License

This project is licensed under the [MIT License](LICENSE.md) - see the LICENSE file for details.

## Acknowledgments

- Streamlit - For the interactive web application framework.
- OpenAI - For AI-powered text summarization capabilities.
- YouTube Data API - For video fetching and data retrieval.
