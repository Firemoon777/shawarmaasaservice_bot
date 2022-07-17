from telegram.ext import Application

app = None


def get_bot():
    return app


def make_bot(settings):
    global app
    app = Application.builder().token(settings.token).build()