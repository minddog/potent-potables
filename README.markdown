Potent Potables is a quiz show application based on the concepts of popular television shows.

The software included will allow end-users and developers to build a quiz show server that can 
display the board /quizshow/board, host the show from a console /quizshow/console, and 
buzz in through different mediums using a REST API request or Mobile web UI /quizshow/buzzer.

## Multi-tenancy
Potent Potables brings the promise of a quiz-show application that anyone can setup and use. 
Multiple games can run in parallel, if you are to run this on a server. 

## Question Management
Questions are crowd-sourced from folks and can be added to the compilation via pull requests.  

## Host Console
An interface to manage the show from.  Try not to face any contestants when used.

## Installing

Clone the repo and setup a virtual environment
> git clone https://github.com/adam/potent-potables.git

> cd potent-potables

> mkvirtualenv potables

> pip install -r requirements.txt

Install the application
> python setup.py install

Configure the database
> vim db.xml

> mysql -u<user> -e 'CREATE DATABASE gameshow';

> python setup.py db

Run the server
> python scripts/runserver.py

## Requirements
* python 2.7.x
* a linux or mac server
* a host
* some teams
* sense of humour
