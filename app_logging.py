import logging

logger = logging.getLogger("test")
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(
    logging.Formatter("%(asctime)s %(message)s [%(pathname)s:%(lineno)d] \n")
)
logger.addHandler(stream_handler)

logging.basicConfig(
    format="%(asctime)s %(message)s {%(pathname)s:%(lineno)d} \n",  # Include '\n' for line break
    filename="app.log",
    encoding="utf-8",
    level=logging.DEBUG,
)
