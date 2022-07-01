import uvicorn

from core.factory import create_app

app = create_app(create=True)

uvicorn.run(app, host="127.0.0.1")