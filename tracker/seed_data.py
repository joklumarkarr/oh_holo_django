# The source of truth for "which talents exist". Edit this list and redeploy —
# the seed command below is safe to run every deploy; it won't duplicate rows
# or clobber live-status fields that get updated separately at runtime.

TALENTS = [
    # slug,      name,       icon,              alt_icon,           noise,              youtube_channel_id,         twitch_username
    ("mumei",    "Mumei",    "mumeiload.png",   "smolmei.jpg",      "hi-1.mp3",         "UC3n5uGu18FoCy23ggWWp8tA", ""),
    ("fauna",    "Fauna",    "fauuuuuna.png",   "smolna.png",       "konfauna.mp3",     "UCO_aKKYxn4tvrqPjcTzZ6EQ", ""),
    ("bae",      "Bae",      "baeconfused.png", "smolbae.jpg",      "wazzup.mp3",       "UCgmPnx-EEeOrZSg5Tiw7ZRQ", ""),
    ("kronii",   "Kronii",   "kroniiwink.png",  "smolnii.jpg",      "kroniichiwa.mp3",  "UCmbs8T6MWqUHP1tIQvSgKrg", ""),
    ("liz",      "Liz",      "lizfreak.png",    "woahliz.png",       "ohohohoho.mp3",   "UCW5uhrG1eCBYditmhL0Ykjw", "elizabethrosebloodflame"),
    ("nerissa",  "Nerissa",  "rissavibe.png",   "rissastare.jpg",   "",                 "UC_sFNM0z0MWm9A6WlKPuMMg", "nerissaravencroft"),
    ("gura",     "Gura",     "guraspin.png",    "guradum.jpg",      "a.mp3",            "UCoSrY_IQQVpmIRZ9Xf-y93g", "gawrgura"),
    ("ina",      "Ina",      "tomorrow.png",    "inaeat.png",       "wah.mp3",          "UCMwGHR0BTZuLsmjY_NT5Pwg", ""),
    ("kiara",    "Kiara",    "kiarapeek.png",   "kiarawink.png",    "",                 "UCHsx4Hqa-1ORjQTh9TYDhww", ""),
    ("minto",    "Minto",    "mintwink.png",    "mintload.png",     "",                 "UCcHHkJ98eSfa5aj0mdTwwLQ", ""),
    ("raora",    "Raora",    "",                "",                 "",                 "UCl69AEx4MdqMZH7Jtsm7Tig", "raora"),
    ("kaela",    "Kaela",    "",                "",                 "",                 "UCZLZ8Jjx_RN2CXloOmgTHVg", ""),
    ("gigi",     "Gigi",     "",                "",                 "",                 "UCDHABijvPBnJm7F-KlNME3w", "gigimurin"),
    ("shiorin",  "Shiorin",  "shiozoom.png",    "shiogrin.png",     "",                 "UCgnfPPb9JI3e9A4cXHnWbyg", "shiorinovella"),
    ("doki",     "Doki",     "dokihuh.png",     "dokilean.png",     "",                 "UComInW10MkHJs-_vi4rHQCQ", "dokibird"),
    ("doob",     "Doob",     "",                "",                 "",                 "UC6T7TJZbW6nO-qsc5coo8Pg", "dooby3d"),
    ("irys",     "IRyS",     "",                "",                 "",                 "UC8rcEBzJSleTkf_-agPM20g", ""),
]