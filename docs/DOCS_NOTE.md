# Mkdocs

```
virtualenv -p python3.6 env_docs
source env_docs/bin/activate
pip install mkdocs
mkdocs --version
mkdocs new docs
cd docs
```


According to [this link](https://click.palletsprojects.com/en/7.x/python3/) that if you get the following error.

```
Traceback (most recent call last):
  ...
RuntimeError: Click will abort further execution because Python 3 was
  configured to use ASCII as encoding for the environment. Either switch
  to Python 2 or consult the Python 3 section of the docs for
  mitigation steps.
```

then all you have to do is change to your local language and it fixes the issue. I entered:

```
export LANG=en_CA.UTF-8
export LC_ALL=en_CA.UTF-8
```

Afterwords to run the server, enter:

```
mkdocs serve
```

http://127.0.0.1:8000
