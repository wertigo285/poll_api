# API для системы опросов пользователей

Описание решаемой задачи в файле [TASK.MD](https://github.com/wertigo285/poll_api/blob/main/TASK.MD)

## Запуск
#### Запуск образа docker

Для запуска приложения в контейнере с именем 'poll_api' необходимо выполнить команды:
```
docker pull skhortyuk/poll_api 
docker run -it -p 8000:8000 --name poll_api skhortyuk/poll_api
```
При первом запуске необходимо создать и применить миграции, а так же создать супер-пользователя для возможности использования административного функционала.
```
docker exec -it poll_api python manage.py makemigrations
docker exec -it poll_api python manage.py migrate
docker exec -it poll_api python manage.py collectstatic
docker exec -it poll_api python manage.py createsuperuser
```
#### Запуск локально

Необходимо получить файлы репозитория
```
git clone https://github.com/wertigo285/poll_api.git
```
В папке репозитория создать виртуальное окружение и выполнить команды:
```
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser
```
Для запуска проекта выполнить команду:
```
python manage.py runserver
```

#### Адрес
После запуска приложение будет доступно по адресу http://127.0.0.1:8000/

## Опиание методов

#### Краткое описание энд-поинтов

###### Функционал для администратора системы:

*Методы доступны после аутентификации.*
* **/admin/polls/** - Просмотр списка/создание опросов
* **/admin/polls/{poll_id}** - Просмотр/редактирование/удаление опроса
* **/admin/polls/{poll_id}/questions/** - Просмотр/создание вопросов опроса {poll_id}
* **/admin/polls/{poll_id}/questions/{question_id}** - Просмотр/редактирование/удаление вопроса {question_id} опроса {poll_id}

###### Функционал для пользователей системы:
* **/polls/** - Просмотр списка активных опросов
* **/polls/{poll_id}** - Просмотр активного ороса
* **/polls/{poll_id}/submissions** - Просмотр активного ороса/отправка ответа опроса {poll_id}
* **/users/{user_id}/submissions** - Просмотр списка отправленнных ответов на опросы пользователя {user_id}

#### Полное описание API
Полное описание методов и моделей API доступно по адресу https://app.swaggerhub.com/apis/wertigo285/poll_api/v1 

После запуска приложения интерактивная документация так же доступна по адресу http://127.0.0.1:8000/swagger