## **HOMEWORK_CHECK_STATUS_BOT/ Бот в телеграм для проверки статуса домашнего задания Яндекс.Практикум**

Что умеет бот:

 - раз в 10 минут опрашивать API сервиса Практикум.Домашка и проверять статус отправленной на ревью домашней работы;
 - при обновлении статуса анализировать ответ API и отправлять вам соответствующее уведомление в Telegram;
 - логировать свою работу и сообщать о важных проблемах сообщением в
   Telegram.

## Запуск проекта
Клонируем проект:

    git clone
Создаем и активируем виртуальное окружение, устанавливаем зависимости:

    python -m venv venv
    source venv/Scripts/activate
    pip install -r requirements.txt
Создайте файл .env и укажите в нем ваши значения токенов и айди вашего чата.
Бот готов к запуску!