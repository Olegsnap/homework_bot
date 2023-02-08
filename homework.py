import logging
import os
import requests
import sys
import telegram
import time
from http import HTTPStatus
from dotenv import load_dotenv
from exceptions import EndpointStatusError, StatusError


load_dotenv()


PRACTICUM_TOKEN = os.getenv('SECRET_PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('SECRET_TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('SECRET_TELEGRAM_CHAT_ID')


RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


logging.basicConfig(
    level=logging.INFO,
    filename='program.log',
    format='%(levelname)s, %(message)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s, %(levelname)s, %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def check_tokens():
    '''Проверяем что необходимые перменные доступны'''
    for token in [
        PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
    ]:
        if not token:
            logger.critical(
                'Программа остановлена. Отсуствует переменная окружения.'
            )
            raise SystemExit
    return True


def send_message(bot, message):
    '''Отправляет сообщения в чат. Чат определяется по TELEGRAM_CHAT_ID'''
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.debug(
            f'Сообщение в Telegram отправлено: {message}')
    except Exception as error:
        logger.error(
            f'Сообщение в Telegram не отправлено: {error}')


def get_api_answer(timestamp):
    '''Создает запрос к эндпоинту и возвращает объект домашней работы'''
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    finally:
        if response.status_code != HTTPStatus.OK:
            message = (
                f'Ресурс {ENDPOINT} недоступен. '
                f'Код ответа: {response.status_code}.'
            )
            logger.error(message)
            raise EndpointStatusError
    return response.json()


def check_response(response):
    '''Проверяет ответ API на соответствие требованиям'''
    if type(response) is not dict:
        error_message = 'Необрабатываемый ответ API.'
        logger.error(error_message)
        raise TypeError(error_message)
    if 'homeworks' not in response:
        error_message = 'Ошибка в ответе API, ключ homeworks не найден.'
        logger.error(error_message)
        raise KeyError(error_message)
    if type(response['homeworks']) is not list:
        error_message = 'Неверные данные.'
        logger.error(error_message)
        raise TypeError(error_message)
    if not response['homeworks']:
        logger.info('Словарь homeworks пуст.')
        return {}
    if response['homeworks'][0].get('status') not in HOMEWORK_VERDICTS:
        error_message = 'Не определен статус домашней работы!'
        logger.error(error_message)
        raise StatusError
    return response['homeworks'][0]


def parse_status(homework):
    '''Получает статус конкретной домашней работы'''
    if 'homework_name' not in homework:
        error_message = 'Ключ homework_name отсутствует.'
        logger.error(error_message)
        raise KeyError(error_message)
    if 'status' not in homework:
        error_message = 'Ключ status отсутствует.'
        logger.error(error_message)
        raise StatusError
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_VERDICTS:
        error_message = ('Не определен статус домашней работы!')
        logger.error(error_message)
        raise StatusError
    else:
        verdict = HOMEWORK_VERDICTS[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)
            if homework:
                message = parse_status(homework)
                if message:
                    send_message(bot, message)
            logger.info('Повторение запроса через 10 мин.')
            time.sleep(RETRY_PERIOD)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            logger.error(message)
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
