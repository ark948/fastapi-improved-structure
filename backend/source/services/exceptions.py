from fastapi.responses import JSONResponse
from fastapi.requests import Request
from typing import Any, Callable





# Custom Exceptions here


class ObjectDoesNotExist(Exception):
    pass


class MultipleObjectsReturned(Exception):
    pass