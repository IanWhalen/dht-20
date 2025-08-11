import asyncio

from viam.module.module import Module

from models.dht_20 import Dht20  # noqa: F401

if __name__ == "__main__":
    asyncio.run(Module.run_from_registry())
