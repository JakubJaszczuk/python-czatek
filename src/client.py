import aiohttp
import asyncio
from proto.data_pb2 import User, Message
from datetime import datetime as dt
import logging
from typing import Final


FORMAT: Final[str] = '%(asctime)s, %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)
logger = logging.getLogger(__name__)


class Client:

    def __init__(self, host='127.0.0.1', port='12345'):
        self.session = aiohttp.ClientSession()
        self.ws_session = None
        self.host = host
        self.port = port
        self.url = f'http://{host}:{port}/'

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

    async def close(self):
        await self.session.close()

    async def ws(self):
        h = {'Authorization': str(dt.now())}
        async with self.session.ws_connect('http://127.0.0.1:2137/msg', headers=h) as ws:
            await ws.send_str('1')
            await asyncio.sleep(1)
            await ws.send_str('2')
            await asyncio.sleep(1)
            await ws.send_str('3')
            await asyncio.sleep(1)
            await ws.send_str('4')
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    print(msg.data)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break

    async def register(self, username: str, password: str):
        user = User(name=username, password=password)
        data = user.SerializeToString()
        url = f'{self.url}register'
        async with self.session.post(url, data=data) as response:
            logger.info(response.status)

    async def login(self, username: str, password: str):
        auth = aiohttp.BasicAuth(username, password)
        url = f'{self.url}login'
        async with self.session.get(url, auth=auth) as response:
            logger.info(response.status)
            data = await response.read()
            logger.info(data)

    async def send_message(self, message: str, channel='main', command='/msg'):
        pass


async def main():
    async with Client() as client:
        await client.login('qw', 'er')


if __name__ == "__main__":
    asyncio.run(main())
