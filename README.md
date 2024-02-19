# Описание
recipe-share - это онлайн-платформа для обмена рецептами приготовления различных блюд. Пользователи могут создавать свои рецепты, просматривать рецепты других пользователей, а также добавлять их в "Избранное" или "Список покупок". Более 2000 ингридиентов с соответствующими единицами измерения уже предзагружено и доступно для выбора при создании рецепта. Присутствует также возможность добавить изображение блюда. Полезная функция "Список покупок" позволяет, добавив в корзину несколько рецептов, скачать результирующий список ингридиентов, в котором количества одинаковых ингридиентов суммируются. Удобдно для похода в магазин.

# Запуск проекта локально.
### 1. Клонировать репозиторий командой в терминале Git Bash:
```bash
git clone git@github.com:Scorcer777/foodgram-project-react.git
```
### 2. Создать файл с переменными окружения в головной директории проекта:
```bash
touch .env
```
   Скопировать в файл следующее содержимое:
```
DEBUG=False
DB_NAME=postgres
DB_ENGINE=django.db.backends.postgresql
POSTGRES_USER=postgres
POSTGRES_PASSWORD=123
DB_HOST=db
DB_PORT=5432
SECRET_KEY=django-insecure-nf&#vvppnl$l3p-fgr3_%-37@sqy@2tz6vg%s__5yi*(g-se5$
ALLOWED_HOSTS=130.193.42.123,127.0.0.1,localhost,blackwaterpark.ddns.net
DJANGO_SUPERUSER_EMAIL=fornka2006@yandex.ru
DJANGO_SUPERUSER_USERNAME=NoTiltToday
DJANGO_SUPERUSER_PASSWORD=Scorcer777
```

### 3. Установить приложение Docker Desktop со страндарстными настройками.
### 4. Собрать контейнеры. Находясь в директории с файлом docker-compose.yml ввести в терминале команду:
```bash
docker compose up
```
### 5. Миграции, загрузка тестовых пользователей, ингридиентов и тегов произойдут автоматически.
### 6. Открыть в браузере URL http://localhost/ для работы с сайтом или запустить программу Postman(или аналогичную для работы с API) для выполнения запросов.



## Алгоритм регистрации пользователей
1. Пользователь отправляет POST-запрос на добавление нового пользователя на эндпоинт localhost/api/users/ со следующими обязательными параметрами:
```JSON
{
    "email": "vpupkin@yandex.ru",
    "username": "vasya.pupkin",
    "first_name": "Вася",
    "last_name": "Пупкин",
    "password": "Qwerty123"
}
```
2. Для получения auth token пользователь отправляет POST-запрос с параметрами username и passworn на эндпоинт /api/auth/token/login/:
```JSON
{
    "email": "vpupkin@yandex.ru",
    "password": "Qwerty123"
}
```
4. Далее, при выполнении запросов через Postman, требующих аутентификации пользователя, необходимо указываеть в Headers параметр Autorization со значением Token <код полученного auth token>.

## Пользовательские роли
Аноним — может просматривать описания рецептов, просматривать страницы пользователей.
Аутентифицированный пользователь (user) — может, как и Аноним, читать всё, дополнительно он может публиковать и редактировать свои рецепты, 
добавлять любые рецепты их в избранное, подписываться на пользователей и скачивать свой "Список покупок". Эта роль присваивается по умолчанию каждому новому пользователю.
Суперюзер Django — обладет правами администратора (admin), полные права на управление всем контентом проекта.

## Базовые запросы к API c помощью POSTMAN(или аналогичной программы для работы с API):

1. GET localhost/api/users/ - получить список всех пользователей.
2. GET localhost/api/users/id(целое число)/ - получить профиль пользователя.
3. POST localhost/api/users/ - зарегистрировать нового пользователя.
Содержимое(обязательные поля)
```JSON
{
    "email": "vpupkin@yandex.ru",
    "username": "vasya.pupkin",
    "first_name": "Вася",
    "last_name": "Пупкин",
    "password": "Qwerty123"
}
```
4. POST http://localhost/api/auth/token/login/ - получить токен авторизации.
Содержимое(обязательные поля)
```JSON
{
    "email": "vpupkin@yandex.ru",
    "password": "Qwerty123"
}
```
5. POST localhost/api/users/id(целое число)/subscribe/ - подписаться на пользователя.
6. GET localhost/api/recipes/ - получить список всех рецептов.
7. GET localhost/api/recipes/id(целое число)/ - получить рецепт.
8. POST localhost/api/recipes/ (доступно только авторизованным пользователям.)
Содержимое(обязательные поля)
```JSON
{
    "ingredients": [
{
    "id": 1123,
    "amount": 10
}
    ],
    "tags": [
    1,
    2
    ],
    "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
    "name": "string",
    "text": "string",
    "cooking_time": 1
}
```
9. POST http://localhost/api/recipes/id(целое число)/favorite/ - добавление рецепта в Избранное.
10. POST http://localhost/api/recipes/id(целое число)/shopping_cart/ - добавление рецепта в Список покупок.
11. GET http://localhost/api/recipes/download_shopping_cart/ - скачать список покупок в виде PDF или TXT файла.

