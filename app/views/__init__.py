from .main import handlers as mai_handlers
from .twitter import handlers as twitter_handlers


handlers = []
handlers.extend(mai_handlers)
handlers.extend(twitter_handlers)
