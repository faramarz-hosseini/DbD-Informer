import os
import logging
from informer_client import InformerClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    client = InformerClient(token=os.environ.get('discord-token'))
    client.run(client.token)
