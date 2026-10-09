# Process Media

## Description

Collection of scripts that process media (anime or manga).<br>

## Scripts

### [downsize_covers.py](downsize_covers.py)

Downsizes each folder's cover image to fit within a maximum size.

### [fetch_score.py](fetch_score.py)

Searches MyAnimeList and writes the score to a hidden metadata.json inside each folder.

### [overlay_cover_score.py](overlay_cover_score.py)

Overlays the saved score onto each folder's cover image.

- Requires running [fetch_score.py](fetch_score.py) first or manually setting the score
