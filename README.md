# jenkins-trigger
trigger a jenkins job and [optionally] bubble the result


## requirements

* python 3.5+ (type hinting)
  * [requests](https://docs.python-requests.org/en/latest/)
  * [black](https://github.com/psf/black) (for stylechecking)
* if an authenticated user is required to create and view jobs, an **API token** (and not password) for that user must be provided to support [improved CSRF protection](https://www.jenkins.io/doc/upgrade-guide/2.176/#upgrading-to-jenkins-lts-2-176-3).

### in a virtual environment

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./jenkins-trigger.py ...
```

## usage

```
jenkins-trigger.py [-h] [-u USER] [-p TOKEN] [--param [name=value]] [--no-wait] [--timeout TIMEOUT] [--interval INTERVAL] [-vv] [job_url]

Trigger a Jenkins job and [optionally] bubble its result. Returns 0 on success, 100 on failue, 101 on aborted, 102 on other.

positional arguments:
  job_url               Job URL, e.g. 'https://jenkins.iceburg.net/job/test-folder/job/foo-job'. (Env: JOB_URL) (default: None)

options:
  -h, --help            show this help message and exit
  -u USER, --user USER  User Name (Env: JOB_USER_NAME) (default: None)
  -p TOKEN, --token TOKEN, --password TOKEN
                        User Token or Password (Env: JOB_USER_TOKEN) (default: None)
  --param [name=value]  Job Parameters, e.g. 'color=purple'. stackable. (default: [])
  --no-wait             Return immediately and do not bubble job completion status. (default: False)
  --timeout TIMEOUT     Time in seconds to wait for job to complete (default: 1800)
  --interval INTERVAL   Poll interval in seconds (default: 10)
  -vv, --verbose        enables debug output (default: False)
```

### examples

> :bulb: provide appropriate username and token values, these are examples.

* trigger the 'tests/trigger-success' job provided by the [containerized jenkins](tests/docker-compose.yaml) used in testing.
  ```
  JOB_USER_NAME="test-user" \
  JOB_USER_TOKEN="secret" \
    ./jenkins-trigger.py http://localhost:8080/job/tests/job/trigger-success
  ```

* trigger the 'tests/trigger-checkboxes' job, which receives parameters
  ```
  ./jenkins-trigger.py http://localhost:8080/job/tests/job/trigger-checkboxes  \
    -u test-user \
    -p secret \
    --param COLORS=green \
    --param COLORS=red
  ```
