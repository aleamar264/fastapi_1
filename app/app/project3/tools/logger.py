import logging
import sys

# get logger
logger = logging.getLogger()

# create formatter
formatter = logging.Formatter(fmt="%(asctime)s - %(levelname)s - %(message)s")

# create handlers
stream_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler("logs/app.log")

# set formatter
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# add hanlders to the logger
logger.handlers = [stream_handler, file_handler]

# set level
logger.setLevel(logging.INFO)
