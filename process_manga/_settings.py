# format
OUTPUT_FORMAT = 'WEBP'
OUTPUT_EXTENSION = OUTPUT_FORMAT.lower()
OUTPUT_QUALITY = 80

# Method | Speed        | Size
# -------|--------------|--------------
# 0      | ~54% faster  | ~29% larger
# 1      | ~52% faster  | ~22% larger
# 2      | ~44% faster  | ~3% larger
# 3      |  Baseline    |  Baseline
# 4      |  ~4% slower  | ~Unchanged
# 5      |  ~9% slower  | ~Unchanged
# 6      | ~20% slower  | ~Unchanged
WEBP_METHOD = 2

# size
LONG_STRIP_ASPECT_RATIO = 5 / 8
MAX_HEIGHT = 1920
MAX_WIDTH = 1200

# cropping
BLACK_THRESHOLD = 8
WHITE_THRESHOLD = 248
MAX_PAGE_ASPECT_RATIO = 1 / 5
