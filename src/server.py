from aiohttp import web
from aiohttp.web import Request, Response
import proto.message_pb2 as proto
import database as db
from entity import User


class ServerApp:

    def __init__(self, port=12345):
        self.persistent = db.Database()
        self.cache = db.DatabaseCache()
        self.port = port

        app = web.Application()
        app.add_routes([
            web.post('/register', self.register),
            web.post('/login', self.login),
            web.post('/msg', self.message),
        ])
        self.app = app

    def run(self):
        web.run_app(self.app, port=self.port)

    async def register(self, req: Request):
        if not req.can_read_body:
            return Response(status=400)
        data = await req.read()
        user_proto = proto.User.FromString(data)
        user = User.from_proto(user_proto)
        self.persistent.create_user(user)
        return web.Response(status=200)

    async def login(self, req: Request):
        return web.Response(status=200)

    async def message(self, req: Request):
        return web.Response(status=200)


def main():
    s = ServerApp(2137)
    s.run()


if __name__ == '__main__':
    main()
