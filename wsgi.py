import sys
import logging
from flashlearn import create_app

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/")
app = create_app()

if __name__ == "__main__":
    app.run()
