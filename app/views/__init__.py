from .main import handlers as mai_handlers
from .weibo import handlers as weibo_handlers

handlers = []
handlers.extend(mai_handlers)
handlers.extend(weibo_handlers)
