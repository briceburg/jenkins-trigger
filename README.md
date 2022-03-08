# jenkins-trigger
trigger a jenkins job and [optionally] bubble the result


## requirements

* python 3.4+
* [requests](https://docs.python-requests.org/en/latest/)
* [black](https://github.com/psf/black) (for stylechecking)

### in a virtual environment

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./jenkins-trigger.py ...
```
