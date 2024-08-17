#!/usr/bin/env python3
import os
import sys
import hmac
import json
import logging
import random
import sched
import time
import datetime
import http.client

logger = logging.getLogger(__name__)

# 创建 scheduler 实例
scheduler = sched.scheduler(time.time, time.sleep)
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"

def setup_logger() -> None:
    form = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    handler.setFormatter(form)

    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

def sign_message(message: bytes, key: bytes) -> str:
    message_hmac = hmac.new(key, message, digestmod="sha256")
    return message_hmac.hexdigest()


def update_dns_record(url: str, key: str):
	timestamp = time.time()
	payload = json.dumps({"timestamp": timestamp}).encode("utf8")
	signature = sign_message(payload, key.encode("utf8"))
	req = http.client.HTTPSConnection(url)
	headers = { 'Content-Type': "application/json; charset=utf-8",	"User-Agent":USER_AGENT,	"Authorization": signature}
	req.request("POST", "/", payload, headers)
	logger.info("DNS Record updated successfully")

def update_once() -> None:
	key = ""
	url = ""
	try:
		update_dns_record(url, key)
	except (error.URLError, error.HTTPError) as err:
		logger.exception("Failed to update DNS record")

if __name__ == "__main__":
	setup_logger()
	while True:
		scheduler.enter(1, 1, update_once, ())
		# 一分钟运行一次定时任务
		scheduler.run()
    
