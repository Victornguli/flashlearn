# Flashlearn
[![Tests](https://github.com/Victornguli/flashlearn/actions/workflows/test.yml/badge.svg)](https://github.com/Victornguli/flashlearn/actions/workflows/test.yml)
[![Coverage Status](https://coveralls.io/repos/github/Victornguli/flashlearn/badge.svg?branch=master)](https://coveralls.io/github/Victornguli/flashlearn?branch=master)

**Master difficult concepts via spaced repetition using flashcards**

# Getting Started
### Dependencies

To run a copy of this project locally you will require:
+ Python 3.6+
+ Postgresql(Optional)
+ Docker(Optional)
+ Redis server(Optional)


### Installation

You can run a local version of flashlearn by cloning this repo
and following these instructions

    git clone https://github.com/Victornguli/flashlearn.git
    cd flashlearn
    # Create a virtualenv, install requirements

    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt

If pip installation fails but you dont need postgresql database feel free to remove **psycopg2** from the list and try the installation again.
The file .flaskenv is populated with default development configs that you
can override to suit your needs.
To run the server directly type

    flask run --host=0.0.0.0



#### Setting up Postgresql
First ensure the latest version of postgresql is installed!
To setup psql proceed as follows:

+ Create a new postgres user, set the user password and make sure that you can access psql shell
+ Update .flaskenv with correct database url details
+ Type **flask db upgrade** to run migrations

Ignore this step to use sqlite3




#### Setting up Redis cache
Ensure you have redis server installed in your system.
Enable Redis cache from BaseConfig class file in /instance/config.py by
changing the value of **USE_REDIS_CACHE** from False to True



#### Running on Docker
First ensure docker and docker-compose are installed in your machine, then run:

  + Copy paste the contents of .env.dev into a new file named.env.prod

  To run the app with all services defined in the docker-compose file run:

        docker-compose up --build 

