#!/usr/bin/env python3
#
# @requires requests
#
# usage: jenkins-trigger.py [-h] [--user USER] [--token TOKEN] [-p [key=value] ...] [--no-wait] [-vv] job_url
#
# Trigger a Jenkins job and [optionally] bubble its result. Returns 0 on success, 1 on error, 2 on aborted.
#

import sys
import argparse
import logging
import os

import requests
import re
import json


def main(args):
    """Trigger a Jenkins Job over the REST API"""

    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.DEBUG if args.verbose else logging.INFO,
    )

    for k, v in args.job_params:
        print("posting param: %s" % k)

    exit(args)


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
        description="Trigger a Jenkins job and [optionally] bubble its result. Returns 0 on success, 1 on error, 2 on aborted.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "job_url",
        help="Job URL, e.g. 'https://jenkins.iceburg.net/job/test-folder/job/foo-job'. (Env: JOB_URL)",
        nargs="?",
        default=os.environ.get("JOB_URL"),
    )
    parser.add_argument(
        "--user",
        help="User Name, e.g. 'robocop' (Env: JOB_USER_NAME)",
        default=os.environ.get("JOB_USER_NAME"),
    )
    parser.add_argument(
        "--token",
        "--password",
        help="User Token or Password , e.g. 'secret' (Env: JOB_USER_TOKEN)",
    )
    parser.add_argument(
        "-p",
        "--param",
        dest="job_params",
        nargs="?",
        action=KVArg,
        metavar="key=value",
        help="Job Parameters. E.g. 'color=purple'. stackable.",
        default=[],
    )
    parser.add_argument(
        "--no-wait",
        help="Return immediately and do not bubble job completion status.",
        action="store_true",
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
