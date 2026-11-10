"""Dust & Debt authored M4A soundtrack mapping.

The recordings belong to the game creator. Keep the original filenames intact.
A track is available only when its original M4A is present on disk.
No generated audio silently stands in for a missing recording.

Each state has an ordered list of eligible tracks, with one guaranteed primary
and optional alternatives for variety when the actual M4A files are installed.
"""

SOUNDTRACK_PLAYLISTS={
    "title":(
        "Forsaken to This Land.m4a",
    ),
    "wilderness":(
        "Whistling the Frontier.m4a",
        "Dust on Our Sleeves.m4a",
        "Mournful Frontier Ballad.m4a",
    ),
    "town":(
        "The Good.m4a",
        "Sol de Harmonica.m4a",
        "Mm-Hmm.m4a",
    ),
    "night":(
        "Rainy Night Blues.m4a",
        "Why Me.m4a",
        "Mournful Hymn.m4a",
    ),
    "interior":(
        "Sol de Harmonica.m4a",
        "Mournful Hymn.m4a",
    ),
    "combat":(
        "Blood Money Spends.m4a",
    ),
}

# Untitled.m4a is intentionally not assigned to a scene until it is identified.
UNASSIGNED_TRACKS=("Untitled.m4a",)
SOURCE_FILES=tuple(dict.fromkeys(
    title for tracks in SOUNDTRACK_PLAYLISTS.values() for title in tracks
)) + UNASSIGNED_TRACKS

def tracks_for(state,folder):
    """Return the existing sound recordings, in score order."""
    import os
    if state not in SOUNDTRACK_PLAYLISTS:return ()
    return tuple(os.path.join(folder,title) for title in SOUNDTRACK_PLAYLISTS[state]
                 if os.path.isfile(os.path.join(folder,title)))

def missing_tracks(folder):
    import os
    return tuple(title for title in SOURCE_FILES
                 if not os.path.isfile(os.path.join(folder,title)))

def installed_count(folder):
    return len(SOURCE_FILES)-len(missing_tracks(folder))
