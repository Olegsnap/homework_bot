class StatusError(Exception):
    '''Неверный статус работы в ответе API'''


class EndpointStatusError(Exception):
    """Возникла проблема с удаленным сервером."""
