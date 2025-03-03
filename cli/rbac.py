import json
import requests
import typer
from cli.helpers import authenticate
from cli.views.shared import message_show_view


def authorize(ctx: typer.Context):
    object_action = f"{ctx.command.name}:{ctx.invoked_subcommand}"
    token = authenticate()
    authorized = requests.post(
        "http://localhost:5000/authorizations",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        data=json.dumps({"target": object_action}),
    )
    if not authorized.ok:
        message_show_view({"Error": "You are not authorized"})
        raise typer.Exit()


# def authorize(object_action=None):
#     def decorator_authorize(func):
#         @functools.wraps(func)
#         def wrapper(*args, **kwargs):
#             if object_action is not None:
#                 token = authenticate()
#                 authorized = requests.post(
#                     "http://localhost:5000/authorizations",
#                     headers={
#                         "Authorization": f"Bearer {token}",
#                         "Content-Type": "application/json",
#                     },
#                     data=json.dumps({"target": object_action}),
#                 )
#                 if not authorized.ok:
#                     message_show_view({"Error": "You are not authorized"})
#                     raise typer.Exit()
#             return func(*args, **kwargs)
#
#         return wrapper
#
#     return decorator_authorize
