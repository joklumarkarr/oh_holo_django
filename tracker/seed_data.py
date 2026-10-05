# The source of truth for "which talents exist". Edit this list and redeploy —
# the seed command below is safe to run every deploy; it won't duplicate rows
# or clobber live-status fields that get updated separately at runtime.

TALENTS = [
    # slug,     name,      youtube_channel_id,          twitch_username
    ("mumei",   "Mumei",   "UC3n5uGu18FoCy23ggWWp8tA",  ""),
    ("fauna",   "Fauna",   "UCO_aKKYxn4tvrqPjcTzZ6EQ",  ""),
    ("bae",     "Bae",     "UCgmPnx-EEeOrZSg5Tiw7ZRQ",  ""),
    ("gura",    "Gura",    "UCoSrY_IQQVpmIRZ9Xf-y93g",  ""),
]