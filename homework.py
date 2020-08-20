import os
import requests
import telegram
import time
import logging

from dotenv import load_dotenv

load_dotenv()


logging.basicConfig(
    filename='.homework.log',
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.INFO,
)


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
homework_api_url = f'https://praktikum.yandex.ru/api/user_api/homework_statuses/'

try:
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
except requests.exceptions.RequestException as error:
    logging.error(error)
else:
    logging.info('Success, bot created!')


def parse_homework_status(homework):
    if homework and homework.get('homework_name') and homework.get('status') is None:
        logging.error('Not found homework')
    logging.info('Homework found')
    homework_name = homework.get('homework_name')
    logging.info('Homework name found')
    if homework.get('status') == 'rejected':
        logging.info('Homework status found')
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    if current_timestamp is None:
        current_timestamp = time.time()
    params = {'from_date': current_timestamp, 'current_date': time.time()}
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    try:
        homework_statuses = requests.get(homework_api_url, headers=headers, params=params)
    except requests.exceptions.RequestException as err:
        logging.error(err)
        return err
    else:
        logging.info('Success, YPracticum data received!')
        return homework_statuses.json()


def send_message(message):
    logging.info('Message must be sent!')
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = time.time()

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get('current_date')  # обновить timestamp
            time.sleep(300)  # опрашивать раз в 10 минут

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
