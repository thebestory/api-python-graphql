"""
The Bestory Project
"""

import asyncpg
from graphql.execution.executors.asyncio import AsyncioExecutor
from sanic import Sanic
from sanic_graphql import GraphQLView

import tbs.db_connection
import tbs.lib.session
from tbs import config
from tbs.graphql.schema import schema
from tbs.lib import exceptions


# Application instance

app = Sanic()
loop = None


# Listeners and middleware lists

before_start_listeners = [
    tbs.db_connection.before_start_listener
]
"""List of listeners, that will be iterated, and each listener will
be invoked before server start."""

after_start_listeners = [
    # tbs.db_connection.after_start_listener
]
"""List of listeners, that will be iterated, and each listener will
be invoked after server start."""

before_stop_listeners = []
"""List of listeners, that will be iterated, and each listener will
be invoked before server stop."""

after_stop_listeners = [
    tbs.db_connection.after_stop_listener
]
"""List of listeners, that will be iterated, and each listener will
be invoked after server stop."""

request_middleware = [
    tbs.lib.session.request_middleware
]
"""Functions which will be executed before each request to the
server."""

response_middleware = []
"""Functions which will be executed after each request to the
server."""


# Save our loop for the future tasks
@app.listener("before_server_start")
async def get_loop(app, loop_):
    loop = loop_


# We do not create a loop manually, so we need to add our GraphQL
# routes via listener
@app.listener("before_server_start")
async def add_graphql_routes(app, loop):
    app.add_route(
        GraphQLView.as_view(schema=schema,
                            pretty=config.graphql.PRETTY,
                            graphiql=config.graphql.GRAPHIQL,
                            executor=AsyncioExecutor(loop=loop)),
        "/graphql")
    app.add_route(
        GraphQLView.as_view(schema=schema,
                            batch=True,
                            pretty=config.graphql.PRETTY,
                            graphiql=config.graphql.GRAPHIQL,
                            executor=AsyncioExecutor(loop=loop)),
        "/graphql/batch")


# Helpers for registering listeners and
# middleware before server starts

def add_listeners():
    def add(listeners: list, type: str):
        for listener in listeners:
            app.listener(type)(listener)

    add(before_start_listeners, "before_server_start")
    add(after_start_listeners, "after_server_start")
    add(before_stop_listeners, "before_server_stop")
    add(after_stop_listeners, "after_server_stop")

    return True

def add_middleware():
    def add(middleware: list, type: str):
        for mw in middleware:
            app.middleware(type)(mw)

    add(request_middleware, "request")
    add(response_middleware, "response")

    return True


# Runs the server with configurated settings

run = lambda: (add_listeners() and 
               add_middleware() and 
               app.go_fast(host=config.app.HOST,
                           port=config.app.PORT,
                           debug=config.app.DEBUG,
                           workers=config.app.WORKERS))
