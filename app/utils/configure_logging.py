import logging
import colorlog


def configure_logging(level=logging.INFO):
    handler = colorlog.StreamHandler()
    handler.setFormatter(
        colorlog.ColoredFormatter(
            fmt="%(log_color)s%(levelname)-10s[%(asctime)s.%(msecs)03d] (%(lineno)-d): %(message)s (%(name)s)",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )
    )

    logging.basicConfig(
        level=level,
        handlers=[handler],  # перезаписываем хендлеры, чтобы использовать цветной
    )

    logging.getLogger("asyncio").setLevel(logging.INFO)
    logging.getLogger("aiomysql").setLevel(logging.INFO)
    logging.getLogger("python_multipart.multipart").setLevel(logging.INFO)
