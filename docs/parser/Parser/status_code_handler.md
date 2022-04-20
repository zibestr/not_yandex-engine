### def status_code_handler(self, url: str) -> Response
Делает GET запрос к url адресу. Если возвращается код 404, то возвращает 
пустой объект класса Response модуля requests, если возвращается
код 200, то возвращает обычный объект класса Response, иначе вызывает исключение
PageNotAvailableError и пишет код ошибки.