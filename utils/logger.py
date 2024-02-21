"""Logging utils"""
import logging


class NexusLogger(logging.Logger):
    """Logging class"""

    def __init__(self):
        super().__init__(name="Nexus", level=logging.DEBUG)
        formatter = logging.Formatter(
            "[%(asctime)s %(levelname)s] - %(module)s.%(funcName)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.addHandler(console_handler)


logger = NexusLogger()
