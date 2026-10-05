"""Thin wrapper around the Holodex API (https://docs.holodex.net).
Kept separate from the management command so the parsing logic can be
unit-tested without a real network call, and so later chapters (the
scheduler) can reuse these same functions.
"""
import requests
from django.conf import settings

BASE_URL = "https://holodex.net/api/v2"


def _get(path, params=None):
    if not settings.HOLODEX_API_KEY:
        raise RuntimeError("HOLODEX_API_KEY is not set")
    response = requests.get(
        f"{BASE_URL}{path}",
        params=params or {},
        headers={"X-APIKEY": settings.HOLODEX_API_KEY},
        timeout=15,
    )
    response.raise_for_status()
    return response.json()

def fetch_live_status(channel_ids):
    """One batched call for a fixed set of channels (the /users/live endpoint).
    Returns {channel_id: [video_dict, ...]} — a channel can have 0, 1, or
    rarely 2+ entries (e.g. live now AND something scheduled later today)."""
    data = _get("/users/live", params={"channels": ",".join(channel_ids)})
    by_channel = {}
    for video in data:
        channel = video.get("channel") or {}
        channel_id = channel.get("id")
        by_channel.setdefault(channel_id, []).append(video)
    return by_channel

def fetch_channel_stats(channel_id):
    """subscriber_count / view_count / photo for one channel."""
    return _get(f"/channels/{channel_id}")


def fetch_last_past_video(channel_id):
    """Most recent completed stream for one channel, or None if there isn't one."""
    results = _get("/videos", params={
        "channel_id": channel_id, "status": "past", "type": "stream", "limit": 1,
    })
    return results[0] if results else None