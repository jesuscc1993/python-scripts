# Process Games

## Description

Generates CompactGUI and HowLongToBeat reports for your installed games or Steam wishlist.

## Scripts

### [generate_compact_gui_report.py](generate_compact_gui_report.py)

Matches game folders against the CompactGUI database and generates a compression report.<br>
Add a `.nocompactguiscan` file to a folder to exclude it, or `.noscan` to exclude it from every scan type.

### [generate_hltb_report.py](generate_hltb_report.py)

Matches game folders against HowLongToBeat and generates a completion time report.<br>
Add a `.nohltbscan` file to a folder to exclude it, or `.noscan` to exclude it from every scan type.

### [try_fallback_hltb_scan.py](try_fallback_hltb_scan.py)

Manually maps a game folder name to a fallback name to search HowLongToBeat with, caching the result in the local database.
