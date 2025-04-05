import logging


def get_logger(name, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers if function is called multiple times
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            f"supadef_cli | {name} | %(message)s"))
        logger.addHandler(handler)

    return logger
