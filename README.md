# counter

This example is a Django application. I made this application to serve as a template for creating a live, multi-player web game.
The application uses Daphne 4.0 and Channels 3.4.1 to enable websocket communication via consumers (Channels 4.0.0 has been glitchy for me,
hence the earlier version). We use Redis as the backend for Channels. We also use Celery 5.2.7 to create background tasks that broadcast to
websocket consumers. We supplement the default communication pathways between consumers and celery tasks through Redis via the python
Redis 4.5.4 package.

The most recent versions of Celery only run in linux. Because of that, windows users will need to install the linux subsystem.
To install the subsystem by following the steps in this guide:

[https://learn.microsoft.com/en-us/windows/wsl/install](https://learn.microsoft.com/en-us/windows/wsl/install)

I recommend installing the Ubuntu distribution since the instructions that follow presume this is your distribution.
Once you have the linux subsystem active, run the following:
```
sudo apt update
sudo apt install python3.10-venv
sudo apt install python3-pip
sudo apt install lsb-release
sudo apt install redis-server
sudo service redis-server start
```
After these installs, you can then install this application:
```
git clone ...
```

I do this by performing the following installs in a virtual environment:
```
pip install "channels-redis==3.4.1"
pip install "daphne==4.0.0"
```
