class PageNotAvailableError(Exception):
    def __init__(self, *message):
        super().__init__(*message)


class WrongRobotsFormatError(Exception):
    def __init__(self, *message):
        super().__init__(*message)
