from flask import Flask, jsonify, render_template
from datetime import datetime, timedelta
import time
from redis import Redis
from rq import Queue
import tasks
import logging
import sys

queue = Queue(connection=Redis())
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger_stderr = logging.getLogger('error_logger')
# Info logger - will write to stdout
logger_stdout = logging.getLogger(__name__)
logger_stdout.setLevel(logging.DEBUG)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)
logger_stdout.addHandler(stdout_handler)

app = Flask(__name__)

@app.route('/index/')
def index():
    return flask.jsonify(ok=true)

def queue_tasks():
    queue.enqueue(tasks.print_task, 5)
    queue.enqueue(tasks.sendWelcomeEmail)

def main():
    queue_tasks()

if __name__ == '__main__':
    main()
    app.run(debug=True)