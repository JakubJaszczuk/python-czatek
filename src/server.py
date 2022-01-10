from aiohttp import web, BasicAuth, WSMsgType
from aiohttp.web import Response, Request, WebSocketResponse
import proto.data_pb2 as proto
import database as db
import asyncio
from entity import UserEntity
from security import check_password, generate_token
from collections import deque
from datetime import datetime, timedelta
from typing import Optional


class Session:

    def __init__(self):
        self.token: bytes = None
        self.user: UserEntity = None
        self.expiration = datetime.now() + timedelta(minutes=15)

    def is_expired(self):
        t = datetime.now()
        return t > self.expiration


class Message:

    def __init__(self):
        self.timestamp = None
        self.user = None
        self.message = None


class Channel:

    def __init__(self, name: str):
        self.name = name
        self.sessions: set[Session] = set()
        self.history: deque[Message] = deque(maxlen=20)

    def receive(self, msg):
        self.history.push(msg)

    def send(self, msg):
        pass

    def has_clients(self):
        return self.sessions


class ServerApp:

    def __init__(self, port=12345):
        self.persistent = db.Database()
        self.port = port
        self.sessions: set[Session] = {}
        self.channels: set[Channel] = {}

        app = web.Application()
        app.add_routes([
            web.post('/register', self.register),
            web.get('/login', self.login),
            web.get('/msg', self.message),
        ])
        self.app = app

    def run(self):
        web.run_app(self.app, port=self.port)
        # self.cleanup_task = asyncio.create_task(self.cleanup())

    async def cleanup(self):
        while True:
            await asyncio.sleep(60)
            self.channels = {ch for ch in self.channels if ch.has_clients()}
            self.sessions = {s for s in self.sessions if s.is_expired()}

    async def register(self, req: Request):
        if not req.can_read_body:
            return Response(status=400)
        data = await req.read()
        user_proto = proto.User.FromString(data)
        user = UserEntity.from_proto(user_proto)
        is_success = self.persistent.create_user(user)
        if is_success:
            return Response(status=201)
        else:
            return Response(status=400)

    async def login(self, req: Request):
        try:
            auth = BasicAuth.decode(req.headers.get('Authorization'))
        except ValueError:
            return Response(status=400)
        user = self.persistent.get_user_by_name(auth.login)
        if user is None:
            return Response(status=400)
        if not check_password(auth.password, user.password, user.salt):
            return Response(status=401)
        token = generate_token()
        print(token)
        token = proto.Token(data=token)
        print(token)
        return Response(status=200, body=token.SerializeToString())

    @staticmethod
    def get_token(request: Request) -> Optional[str]:
        token: str = request.headers.get('Authorization')
        if token is None:
            token = request.query.get('access_token')
        else:
            bearer, token = token.split(' ')
            if bearer.lower() != 'bearer':
                raise Exception('Incorrect auth method')
        return token

    async def message(self, req: Request):
        token = self.get_token(req)
        ws = web.WebSocketResponse()
        await ws.prepare(req)
        async for msg in ws:
            if msg.type == WSMsgType.BINARY:
                message = proto.Message.FromString(msg.data)
                self.channels[message.channel]
            else:
                print(req.query)
                print(req.headers)
                print(msg.data)
            await ws.send_str('Server Ping')

        print('websocket connection closed')
        return ws


def main():
    s = ServerApp()
    s.run()


if __name__ == '__main__':
    main()
    #asyncio.run(main())
