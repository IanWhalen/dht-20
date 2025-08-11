import asyncio
from viam.module.module import Module
try:
    from models.dht_20 import Dht20
except ModuleNotFoundError:
    # when running as local module with run.sh
    from .models.dht_20 import Dht20


if __name__ == '__main__':
    asyncio.run(Module.run_from_registry())
