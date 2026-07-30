import logging
import sys
from pathlib import Path

# Configure application logging
log_dir = Path(__file__).resolve().parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

logger = logging.getLogger("resume_analyzer")
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_format = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
)
console_handler.setFormatter(console_format)

# File handler
file_handler = logging.FileHandler(log_dir / "app.log")
file_handler.setLevel(logging.INFO)
file_format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
)
file_handler.setFormatter(file_format)

if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
