class BaseBotException(Exception):
    response = "Произошла неизвестная ошибка"


class ForbiddenError(BaseBotException):
    response = "Данное действие доступно только администраторам"


class NotGroupError(BaseBotException):
    response = "Данное действие доступно только в группах"


class NoMenuInGroupError(BaseBotException):
    response = "В группе нет меню. Необходимо создать хотя бы одно меню для этого действия."


class NoItemsInMenuError(BaseBotException):
    response = "В меню нет опций для опроса"


class IncorrectInputDataError(BaseBotException):
    response = "Введены некорретные данные. Попробуйте ещё раз."


class AlreadyRunningError(BaseBotException):
    response = "Дождитесь завершения события или закройте его вручную."


