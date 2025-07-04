#!/usr/bin/env python3
"""
remove_dangling_images.py

pip install docker
chmod +x remove_dangling_images.py
./remove_dangling_images.py --force
"""
import docker
import sys
import logging
import argparse

COLOR_RESET = "\033[0m"
COLOR_DEBUG = "\033[94m"
COLOR_INFO = "\033[92m"
COLOR_WARNING = "\033[93m"
COLOR_ERROR = "\033[91m"

def get_emoji_for_level(levelno):
    if levelno == logging.DEBUG:
        return "🐛"
    elif levelno == logging.INFO:
        return "✅"
    elif levelno == logging.WARNING:
        return "⚠️"
    elif levelno == logging.ERROR:
        return "❌"
    else:
        return "ℹ️"

class ColorFormatter(logging.Formatter):
    """Logging Formatter to add level-specific emoji prefix and color."""
    def format(self, record):
        emoji = get_emoji_for_level(record.levelno)
        if record.levelno == logging.DEBUG:
            color = COLOR_DEBUG
        elif record.levelno == logging.INFO:
            color = COLOR_INFO
        elif record.levelno == logging.WARNING:
            color = COLOR_WARNING
        elif record.levelno == logging.ERROR:
            color = COLOR_ERROR
        else:
            color = COLOR_RESET

        message = super().format(record)
        return f"{color}{emoji} {message}{COLOR_RESET}"

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(ColorFormatter('%(levelname)s: %(message)s'))

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.handlers.clear()
logger.addHandler(handler)


def main(dry_run=True):
    logger.info("Starting remove_dangling_images.py (dry_run=%s)", dry_run)

    try:
        client = docker.from_env()
        logger.debug("Connected to Docker daemon: %s", client.api.base_url)
    except Exception:
        logger.error("Failed to connect to Docker daemon", exc_info=True)
        sys.exit(1)

    try:
        dangling = client.images.list(filters={'dangling': True})
        logger.info("Found %d dangling image(s)", len(dangling))
    except Exception:
        logger.error("Error listing dangling images", exc_info=True)
        sys.exit(1)

    if not dangling:
        logger.info("Nothing to delete, exiting.")
        return

    for img in dangling:
        short_id = img.id.split(':', 1)[1][:12]
        logger.info("Image: %s", short_id)

    if dry_run:
        logger.warning("DRY RUN — no images removed. Use --force to delete.")
        return

    for img in dangling:
        short_id = img.id.split(':', 1)[1][:12]
        try:
            logger.info("Removing image %s...", short_id)
            client.images.remove(image=img.id)
            logger.info("Removed %s successfully", short_id)
        except docker.errors.APIError as e:
            logger.error("Failed to remove %s: %s", short_id, e.explanation)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Remove dangling Docker images (<none>:<none>) with colorful emoji logging"
    )
    parser.add_argument(
        '-f', '--force',
        action='store_true',
        help="actually delete images (runs dry-run if omitted)"
    )
    args = parser.parse_args()
    main(dry_run=not args.force)
