import logging.config


def setup_logging(loglevel):
    cfg = {
        "version": 1,
        "formatters": {
            "json": {
                "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            }
        },
        "handlers": {
            "console": {"class": "logging.StreamHandler", "formatter": "json"}
        },
        "root": {"level": getattr(logging, loglevel), "handlers": ["console"]},
    }
    logging.config.dictConfig(cfg)
