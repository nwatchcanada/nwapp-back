# Postgres Error
## (1) postmaster.pid file is locked
If you get an error as follows:

```
The data directory contains a postmaster.pid file, which usually means that the server is already running. When the server crashes or is killed, you have to remove this file before you can restart the server. Make sure that the database process is definitely not running anymore, otherwise your data directory will be corrupted.
```

Then please restart your computer and the problem will go away!
