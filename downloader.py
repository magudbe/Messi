import yt_dlp
import os
import uuid


DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_video(url: str):
    """
    Downloads video from TikTok / Instagram / Facebook
    returns file path if success, else None
    """

    file_id = str(uuid.uuid4())
    output_path = os.path.join(DOWNLOAD_DIR, f"{file_id}.mp4")

    ydl_opts = {
        "outtmpl": output_path,
        "format": "mp4/best",
        "quiet": True,
        "noplaylist": True,
        "merge_output_format": "mp4"
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if os.path.exists(output_path):
            return output_path
        return None

    except Exception as e:
        print("Download error:", e)
        return None


def is_supported_link(url: str) -> bool:
    """
    Checks if link is supported
    """
    supported = [
        "tiktok.com",
        "instagram.com",
        "facebook.com",
        "fb.watch"
    ]

    return any(domain in url for domain in supported)
