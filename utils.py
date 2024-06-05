import aiohttp
import logging
import re

YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3"

def extract_video_id(youtube_url):
    pattern = r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/live\/([a-zA-Z0-9_-]{11})"
    match = re.match(pattern, youtube_url)
    if match:
        return match.group(1)
    return youtube_url

async def fetch_live_chat_id(token, video_id):
    url = f"{YOUTUBE_API_URL}/videos?part=liveStreamingDetails&id={video_id}"
    headers = {"Authorization": f"Bearer {token}"}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                logging.error(f"Failed to fetch live chat ID: {response.status}, {await response.text()}")
                return None
            response_json = await response.json()

    items = response_json.get("items", [])
    if not items:
        logging.warning("No live broadcasts found for this video ID.")
        return None

    live_streaming_details = items[0].get("liveStreamingDetails", {})
    live_chat_id = live_streaming_details.get("activeLiveChatId")
    if not live_chat_id:
        logging.warning("No active chat found in live streaming details.")
    return live_chat_id

async def fetch_chat_messages(token, live_chat_id, page_token=None):
    url = f"{YOUTUBE_API_URL}/liveChat/messages?liveChatId={live_chat_id}&part=snippet,authorDetails&maxResults=200"
    if page_token:
        url += f"&pageToken={page_token}"

    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                logging.error(f"Failed to fetch chat messages: {response.status}, {await response.text()}")
                return [], None
            response_json = await response.json()

    return response_json.get("items", []), response_json.get("nextPageToken")

async def post_message_to_youtube(token, live_chat_id, message):
    url = f"{YOUTUBE_API_URL}/liveChat/messages?part=snippet"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    body = {
        "snippet": {
            "liveChatId": live_chat_id,
            "type": "textMessageEvent",
            "textMessageDetails": {"messageText": message}
        }
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=body) as response:
            if response.status == 200:
                logging.info('Message sent to YouTube')
            else:
                logging.error(f"Failed to send message to YouTube: {response.status}, {await response.text()}")
