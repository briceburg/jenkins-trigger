#!/usr/bin/env python3
#
# @requires requests
#
# usage: jenkins-trigger.py [-h] [--user USER] [--token TOKEN] [-p [name=value] ...] [--no-wait] [-vv] job_url
#
# Trigger a Jenkins job and [optionally] bubble its result. Returns 0 on success, 1 on error, 2 on aborted.
#

import sys
import argparse
import logging
import os

import requests
import re
import time


def main(args):
    """Trigger a Jenkins Job over the REST API"""

    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.DEBUG if args.verbose else logging.INFO,
    )

    try:
        client = JenkinsJobClient(args.job_url, args.user, args.token)
        queueId = client.triggerJob(args.job_params)
        logging.info("successfully triggered job with queueId: %d" % queueId)
        if args.no_wait:
            return

        start_time = time.time()
        job_url = None
        logging.info("polling for job completion")
        while time.time() < start_time + args.timeout:
            time.sleep(args.interval)
            job = client.getJobByQueueId(queueId)
            if not job:
                logging.info("job is still in queue")
            else:
                status = job["result"]
                if not status:
                    logging.info("currently executing build %s" % job["id"])
                elif status == "SUCCESS":
                    logging.info("job completed successfully")
                    sys.exit(0)
                elif status == "FAILURE":
                    logging.error("job completed in failure")
                    sys.exit(100)
                elif status == "ABORTED":
                    logging.error("job was aborted")
                    sys.exit(101)
                else:
                    logging.error("job returned status: %s" % status)
                    sys.exit(102)

        logging.error("Timeout waiting for job to complete")
        raise TimeoutError()

    except SystemExit as e:
        sys.exit(e)
    except Exception as e:
        logging.critical(e)
        sys.exit(1)
    finally:
        try:
            # print the job url if it's available at the end.
            # this way we aren't filling logs with long URLs.
            logging.info("job url: %s" % job["url"])
        except:
            pass


class JenkinsJobClient:
    def __init__(self, job_url, user=None, password=None):
        self.job_url = job_url.strip("/")
        self.auth = (user, password) if user and password else None

        # ensure we can accesss the job API
        logging.info("determining if job is buildable")
        json = self.get_json("/api/json")
        if not "buildable" in json or not json["buildable"]:
            raise ValueError("%s does not appear to be a buildable job" % self.job_url)

    def triggerJob(self, params=[]):
        logging.info("building %s" % self.job_url)
        path = "/buildWithParameters" if params else "/build"
        r = requests.post(self.job_url + path, data=params, auth=self.auth)
        self.response(r)

        # triggering a job returns the queue location
        if not r.headers["Location"]:
            raise Exception("failed to trigger job")

        # extract the queueId and return it
        match = re.search(r"/queue/item/(\d+)", r.headers["Location"])
        if not match:
            raise Exception("failed determining job queueId")

        return int(match.group(1))

    def getJobByQueueId(self, queueId: int):
        """given a queueId, fetch the related job and return its status. None if no job matches the queueId"""
        logging.debug("fetching job status")
        json = self.get_json("/api/json?tree=builds[url,id,result,queueId]")
        if not "builds" in json:
            raise Exception("failed fetching builds for %s" % self.job_url)

        for build in json["builds"]:
            if build["queueId"] == queueId:
                return build

        return None

    def get_json(self, path):
        r = requests.get(self.job_url + path, auth=self.auth)
        self.response(r)
        return r.json()

    def response(self, r: requests.Response):
        self.log_request(r.request)
        self.log_response(r)
        r.raise_for_status()

    def log_request(self, req):
        logging.debug(
            "HTTP/1.1 {method} {url}\n{headers}\n\n{body}".format(
                method=req.method,
                url=req.url,
                headers="\n".join(
                    "{}: {}".format(k, v) for k, v in req.headers.items()
                ),
                body=req.body,
            )
        )

    def log_response(self, res):
        logging.debug(
            "HTTP/1.1 {status_code}\n{headers}\n\n{body}".format(
                status_code=res.status_code,
                headers="\n".join(
                    "{}: {}".format(k, v) for k, v in res.headers.items()
                ),
                body=res.content,
            )
        )


if __name__ == "__main__":

    class KVArg(argparse.Action):
        """argparse action supporting Key=Value arguments"""

        def __call__(self, parser, args, value, option_string=None):
            try:
                for k, v in [value.split("=", 1)]:
                    getattr(args, self.dest).append((k, v))
            except Exception as e:
                raise argparse.ArgumentError(
                    self, "Could not parse '%s'. Please use key=value format" % value
                )

    parser = argparse.ArgumentParser(
        description="Trigger a Jenkins job and [optionally] bubble its result. Returns 0 on success, 100 on failue, 101 on aborted, 102 on other.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "job_url",
        help="Job URL, e.g. 'https://jenkins.iceburg.net/job/test-folder/job/foo-job'. (Env: JOB_URL)",
        nargs="?",
        default=os.environ.get("JOB_URL"),
    )
    parser.add_argument(
        "-u",
        "--user",
        help="User Name (Env: JOB_USER_NAME)",
        default=os.environ.get("JOB_USER_NAME"),
    )
    parser.add_argument(
        "-p",
        "--token",
        "--password",
        help="User Token or Password (Env: JOB_USER_TOKEN)",
    )
    parser.add_argument(
        "--param",
        dest="job_params",
        nargs="?",
        action=KVArg,
        metavar="name=value",
        help="Job Parameters, e.g. 'color=purple'. stackable.",
        default=[],
    )
    parser.add_argument(
        "--no-wait",
        help="Return immediately and do not bubble job completion status.",
        action="store_true",
    )
    parser.add_argument(
        "--timeout",
        help="Time in seconds to wait for job to complete",
        default=1800,
        type=int,
    )
    parser.add_argument(
        "--interval", help="Poll interval in seconds", default=10, type=int
    )
    parser.add_argument(
        "-vv", "--verbose", help="enables debug output", action="store_true"
    )

    args = parser.parse_args()

    if not args.job_url:
        sys.exit(parser.print_help())

    if not args.token:
        args.token = os.environ.get("JOB_USER_TOKEN")

    main(args)
