import os
import logging
from dotenv import load_dotenv

load_dotenv()

from backend import create_app

app = create_app()

logger = logging.getLogger("soclab")

if __name__ == '__main__':
    from backend.config import Config
    logger.info(f"SOC Lab on {Config.HOST}:{Config.PORT} (debug={Config.DEBUG})")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
