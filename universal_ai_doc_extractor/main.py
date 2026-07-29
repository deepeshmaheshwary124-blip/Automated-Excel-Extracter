"""Entry point for the Universal AI Document Extractor application."""

import sys
import signal
import logging

from app import Application


logger = logging.getLogger(__name__)


def main() -> None:
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = Application()

    try:
        app.initialize()
        exit_code = app.run()
        sys.exit(exit_code)
    except Exception as e:
        logger.critical("Fatal error: %s", e, exc_info=True)
        sys.exit(1)
    finally:
        app.shutdown()


if __name__ == "__main__":
    main()
