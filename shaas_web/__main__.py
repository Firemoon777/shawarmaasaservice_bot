import uvicorn

from shaas_web.factory import create_app

app = create_app()

uvicorn.run(app, host="127.0.0.1")