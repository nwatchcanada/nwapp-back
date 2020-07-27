# Vagrant Installation

Clone the project to your local machine

```
local$ git clone https://github.com/nwatchcanada/nwapp-back.git
```

Enter the backend repository and start the Vagrant environment:

```
local$ cd nwapp-back
local$ vagrant up
```

Once the virtual machine is running, you'll need to SSH into it and run the following commands.

```
local$ vagrant ssh
[vagrant@localhost] cd /vagrant
[vagrant@localhost vagrant] source centos_env/bin/activate
(centos_env) [vagrant@localhost vagrant] cd nwapp
```

You are now ready to run the developer instance.

# Usage
## runserver

To start running the server:

```
(centos_env) [vagrant@localhost nwapp] python3 manage.py runserver 0.0.0.0:8001
```

Now in your browser, you should have access to the server via [http://127.0.0.1:8080](http://127.0.0.1:8080).

## rqworker

Run the background process handler.

```
(centos_env) [vagrant@localhost nwapp] python3 manage.py rqworker
```

## rqscheduler

Run the background scheduler.

```
(centos_env) [vagrant@localhost nwapp] python3 manage.py rqscheduler
```
