# Django RF Chat
This project is a test assignment given by *Oil and Gas Technology center* of Innopolis University

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
