from asgiref.wsgi import AsgiToWsgi
from app.main import app  # FastAPI ASGI app
application = AsgiToWsgi(app)