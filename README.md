# Mailgun Sender

**Mailgun Sender** is a Django app to create and send simple emails using the [Mailgun API](https://app.mailgun.com/). An interactive dashboard is provided for monitoring, creating and check your emails. All the emails are sent asynchronously with Celery, it means you create an email and an external queue system will do the job for you. 

This application is writen in python, using Django, Postgresql and Celery with RabbitMq as broker.

The original briefing is available [here](https://www.notion.so/Backend-Engineering-Challenge-5fa3cde9bc9d4f96a086123c82a200d5)

## Installation
Make sure you have docker and docker-compose installed.  
1. Clone git repository.
```
git clone https://github.com/augdiebold/mailgun_sender.git
```
2. Run docker-compose.
```
docker-compose up --build
```
The server will run at port 8000: http://localhost:8000.

## Environment Setup
1. Create an environment file named `.env-docker`.  
2. Set the `.env-docker` values.  

##### Mailgun Setup
```
EMAIL_BASE_URL=<https://api.mailgun.net/v3> OR <https://api.eu.mailgun.net/v3/>
EMAIL_DOMAIN=<your_domain.com>
EMAIL_API_KEY=<your_api_key>
EMAIL_ALLOWED_SENDERS=<from1@your_domain.com>,<from2@your_domain.com>
```
- The default is `EMAIL_BASE_URL` = "https://api.mailgun.net/v3", which connects to Mailgun’s US service. You must change this if you are using Mailgun’s **European region**:

```EMAIL_BASE_URL=https://api.eu.mailgun.net/v3```

 - Mailgun’s API requires identifying the sender domain, use 
`EMAIL_DOMAIN` to set it. The domain is everything after @. (e.g., “example.com” for “from@example.com”)


- `EMAIL_API_KEY` - Your Mailgun “Private API key” from the [Mailgun API security settings](https://app.mailgun.com/app/account/security/api_keys).

- Use `EMAIL_ALLOWED_SENDERS` to set addresses, separated by commas, to be available on **`_from`** select field. ***The email DOMAIN should be the same set in*** `EMAIL_DOMAIN`. (e.g., john@**example.com**, doe@**example.com**)

### Create an User
```
docker-compose run web python manage.py createsuperuser --username youruser --email your@email.com
```

## Features

#### Send status
In order to imporve the user experience, colors are set to every send status. Asynchronously, a Celery task will change status based on the Mailgun API response.
| STATUS  |  COLOR  |  DESCRIPTION  |
| ------------------- | ------------------- | ------------------- |
|  PENDING |  Orange |  When an e-mail is created, the status is set to 'pending'.  |
|  SENT |  Green |  If the API response status code **is 200**, set status as 'sent' |
|  FAILED |  Red |  If the API response status code **is not 200**, set status as 'failed' |

#### Send again
With one action, you can easily send a list of selected emails that were sent.
