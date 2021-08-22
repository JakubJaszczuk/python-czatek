import aiohttp
import asyncio
from proto.message_pb2 import User


async def main():
    async with aiohttp.ClientSession() as session:
        u = User(name='Test', password='123')
        s = u.SerializeToString()
        print(s)
        async with session.post('http://127.0.0.1:2137/register', data=s) as resp:
            print(resp.status)


if __name__ == "__main__":
    asyncio.run(main())
