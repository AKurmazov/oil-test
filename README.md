# Django RF Chat
This project is a test assignment given by *Oil and Gas Technology Center* of Innopolis University

### Running locally
Rename `.env.example` to `.env` and fulfill the variables with the following valies:
```
SECRET_KEY=35*stm&who3r9s*1)7p$(-^sbgx+yqv9skx2(y(!1g#k4oaw-)
DB_NAME=postgres
DB_USER=postgres
DB_PORT=5432
DB_PASSWORD=postgres
```
**Disclaimer:** I expose the environmental variables intentionally!

This project uses **Docker**, so the first step to make is to build and run the image using **docker-compose**
```
$ docker-compose up --build -d
```
This command will run the migrations, create a superuser, and set up the server at http://0.0.0.0:8000

Superuser's credentials are:
```
username: admin
password: admin
```

Also, you can run the tests I have prepared so that to ensure that the app works as intended
```
$ docker-compose run web python manage.py test
```

### API endpoints

There are several API endpoints in each of the modules
```
-- accounts --
[POST] api/accounts/register
body: {
    username: <string>
    password: <string>
}
[POST] [Authorization Token] api/accounts/login
body: {
    username: <string>
    password: <string>
}
[POST] [Authorization Token] api/accounts/logout

-- chats --
[POST] [Authorization Token] api/chats/create
body: {
    invited: <list of integers>
}
[POST] [Authorization Token] api/chats/<pk>/send_message
body: {
    text: <string>
}
[GET]  [Authorization Token] api/chats/<pk>/history
[GET]  [Authorization Token] api/chats/user
```

### cURL requests

Register and login as a new user with username **test** and password **test**
```
curl --location --request POST 'http://0.0.0.0:8000/api/accounts/register' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'username=test' \
--data-urlencode 'password=test'
```

Logout using the **token** from the previous requests' response
```
curl --location --request POST 'http://0.0.0.0:8000/api/accounts/logout' \
--header 'Authorization: Token <token>'
```

Login again as the **admin**. Credentials are mentioned above
```
curl --location --request POST 'http://0.0.0.0:8000/api/accounts/login' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'username=admin' \
--data-urlencode 'password=admin'
```

Create a new chat with no invited participants. The **token** came from the login request
```
curl --location --request POST 'http://0.0.0.0:8000/api/chats/create' \
--header 'Authorization: Token <token>' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'invited=[]'
```

Create another chat, but now inviting the user we registered above
```
curl --location --request POST 'http://0.0.0.0:8000/api/chats/create' \
--header 'Authorization: Token <token>' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'invited=[2]'
```

Send message **"Hello!"** to the first chat
```
curl --location --request POST 'http://0.0.0.0:8000/api/chats/1/send_message' \
--header 'Authorization: Token <token>' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'text=Hello!'
```

Send message **"How are you?"** to the second chat
```
curl --location --request POST 'http://0.0.0.0:8000/api/chats/2/send_message' \
--header 'Authorization: Token <token>' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'text=How are you?'
```

Get the **history** of the first chat and see the only message we sent there
```
curl --location --request GET 'http://0.0.0.0:8000/api/chats/1/history' \
--header 'Authorization: Token <token>'
```

Get the **list of chats** where our user is a **participant**
```
curl --location --request GET 'http://0.0.0.0:8000/api/chats/user' \
--header 'Authorization: Token <token>'
```