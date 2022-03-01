from aiohttp import web, BasicAuth, WSMsgType
from aiohttp.web import Response, Request
import proto.data_pb2 as proto
import database as db
from entity import UserEntity
from security import check_password, generate_token
from collections import deque
from datetime import datetime, timedelta
from weakref import WeakSet


class Session:

    def __init__(self, token: bytes, user: UserEntity):
        self.token: bytes = token
        self.user: UserEntity = user
        self.expiration = datetime.now() + timedelta(minutes=15)
        self.ws_session = None

    def is_expired(self):
        t = datetime.now()
        return t > self.expiration

    def username(self) -> str:
        return self.user.name


class Channel:

    def __init__(self, name: str):
        self.name: str = name
        self.sessions: WeakSet[Session] = WeakSet()
        self.history: deque[proto.Message] = deque(maxlen=20)

    def join_channel(self, session: Session):
        self.sessions.add(session)

    def exit_channel(self, session: Session):
        self.sessions.remove(session)

    def receive_message(self, session: Session, msg: proto.Message):
        if self.check_session(session):
            self.history.append(msg)

    async def receive_message_and_send(self, session: Session, msg: proto.Message):
        if self.check_session(session):
            self.history.append(msg)
            await self.send_to_all(msg)

    async def send_to_all(self, msg):
        for session in self.sessions:
            await session.ws_session.send_bytes(msg.SerializeToString())

    def has_clients(self):
        return self.sessions

    def check_session(self, session: Session):
        return session in self.sessions


class ServerApp:

    def __init__(self, port=12345):
        self.persistent = db.Database()
        self.port = port
        self.sessions: dict[str, Session] = {}
        self.channels: dict[str, Channel] = {}

        app = web.Application()
        app.add_routes([
            web.post('/register', self.register),
            web.get('/login', self.login),
            web.get('/msg', self.ws_connection),
        ])
        self.app = app

    def run(self):
        main_channel = Channel('main')
        self.channels.add(main_channel)
        web.run_app(self.app, port=self.port)

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
        self.sessions[token] = Session(token, user)
        return Response(status=200, body=token)

    async def ws_connection(self, req: Request):
        token = self.get_token(req)
        is_token_valid = self.validate_token(token)
        if not is_token_valid:
            return Response(status=401)
        ws = web.WebSocketResponse()
        session = self.sessions[token]
        session.ws_session = ws
        await ws.prepare(req)
        async for msg in ws:
            msg.username = session.username()
            if msg.type == WSMsgType.BINARY:
                message = proto.Message.FromString(msg.data)
                self.dispatch_message(session, message)
        return ws

    @staticmethod
    def get_token(request: Request) -> bytes:
        token: bytes = request.headers.get('Authorization')
        if token is None:
            token = request.query.get('access_token')
        else:
            bearer, token = token.split(b' ')
            if bearer.lower() != 'bearer':
                raise Exception('Incorrect auth method')
        return token

    def validate_token(self, token: bytes) -> bool:
        return token in self.sessions

    async def dispatch_message(self, session: Session, msg: proto.Message):
        channel = self.channels[msg.channel]
        if msg.type == proto.Message.Command.JOIN:
            channel.join_channel(session)
        elif msg.type == proto.Message.Command.EXIT:
            channel.exit_channel(session)
        elif msg.type == proto.Message.Command.MSG:
            await channel.receive_message_and_send(session, msg)


def main():
    s = ServerApp()
    s.run()


if __name__ == '__main__':
    main()
