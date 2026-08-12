"""
ASReview Integration

ASReview is an open-source systematic review tool.
GitHub: https://github.com/asreview/asreview

Integration approach:
- ASReview can be installed locally (pip install asreview)
- We use ASReview's Python API for data exchange
- Export project papers to ASReview-compatible format
- Import screening results back
"""
from .adapter import ASReviewAdapter