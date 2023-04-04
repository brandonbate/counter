# Counter Example (pun intended!)

This example is a Django application. I made this application to serve as a template for creating a live, multi-player web game.
The application uses Daphne 4.0 and Channels 3.4.1 for websocket communication via consumers (Channels 4.0.0 has been glitchy for me,
hence the earlier version). I use Redis as the backend for Channels. I also use Celery 5.2.7 to create a game loop tasks for each game
instance. These tasks broadcast to back to websocket consumers using channels. User game actions are received though a websocket consumer
and then passed to the Redis backend (without using channels). The celery taks for the game loop checks Redis for user game actions
and updates appropriately. This supplementary communication pathways between consumers and celery tasks is done via the python
Redis 4.5.4 package.

As far as "games" go, this is quite boring. Once two players visit the site, they will see a counter increment by 1 each second.
Each player can press a button called "Skip 10" that skips the counter ahead by 10. That's it. But this does provide a framework for
a web game where game state is continually broadcasted to players and player actions cause changes within the game.

The most recent versions of Celery only run in linux. Because of that, windows users will need to install the linux subsystem.
To install the subsystem by following the steps in this guide:

[https://learn.microsoft.com/en-us/windows/wsl/install](https://learn.microsoft.com/en-us/windows/wsl/install)

I recommend installing the Ubuntu distribution since the instructions that follow presume this is your distribution.
Once you have the linux subsystem active, run the following:
```
sudo apt update
sudo apt install python3.10-venv python3-pip lsb-release redis-server
sudo service redis-server start
```
After these installs, you can then install this application:
```
git clone ...
```
Navigate into the folder for this repository and create a virtual environment:
```
python3 -m venv virtualenv
source virtualenv/bin/activate
```
Then install the following through pip:
```
pip install "channels-redis==3.4.1"
pip install "daphne==4.0.0"
pip install celery django-celery-results redis
```
Ignore the warnings you get after installing Daphne.

To run the game, you will need to open up two terminals. In one terminal, run:
```
python manage.py migrate
python manage.py runserver
```
In the other terminal, run
```
celery -A supercounter worker --loglevel=INFO
```
