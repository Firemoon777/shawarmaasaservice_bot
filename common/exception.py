class BaseBotException(Exception):
    response = "Произошла неизвестная ошибка"


class ForbiddenError(BaseBotException):
    response = "Данное действие доступно только администраторам"


class NotGroupError(BaseBotException):
    response = "Данное действие доступно только в группах"
