### Setup


# create a virtual env and update it with the following commands:
    virtualenv --python=/usr/bin/python3.10 env
    source env/bin/activate

# install requirements:
    only flask is being used for creation of server. rest of the code is pure python libraries
    run command:

    pip install requirements.txt


# run server:
    python server.py
    or 
    flask --app server.py run --debug

# API Documentation:
You can use the Postman API collection and load it to run the APIs. The file is: `Glow Assessment API.postman_collection.json`.

APIs include:
- `GET /business/{fein}`
- `POST /business/`
- `POST /business/{fein}/industry/`
- `POST /business/{fein}/contact/`
- `POST /business/{fein}/complete-process/`

# Assumptions:

1. Once a business is created its name and fein cannot be changed. This is done for simplicity and no patch api is available

2. You can move back in a process. So, if industry or phone number is changed even after a business has been won
it can go back to a previous state. This made sense to me. Otherwise in my original implementation there was no way to go back in the process, which made the code simpler.

3. All my design decisions are based on two assumptions. This project should be extensible and the business logic
should follow common sense. I have tried to make sure the code follows 12 factors app methodology


# Test cases not added