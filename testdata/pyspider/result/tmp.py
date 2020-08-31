import time
import json
import logging
from six.moves import queue as Queue
logger = logging.getLogger("result")


class ResultWorker(object):


    def __init__(self, resultdb, inqueue):
        self.resultdb = resultdb
        self.inqueue = inqueue
        self._quit = False

    def on_result(self, task, result):
        if not result:
            return
        if 'taskid' in task and 'project' in task and 'url' in task:
            logger.info('result %s:%s %s -> %.30r' % (
                task['project'], task['taskid'], task['url'], result))
            return self.resultdb.save(
                project=task['project'],
                taskid=task['taskid'],
                url=task['url'],
                result=result
            )
        else:
            logger.warning('result UNKNOW -> %.30r' % result)
            return

    def quit(self):
        self._quit = True

    def run(self):
        logger.info("result_worker starting...")

        while not self._quit:
            try:
                task, result = self.inqueue.get(timeout=1)
                self.on_result(task, result)
            except Queue.Empty as e:
                continue
            except KeyboardInterrupt:
                break
            except AssertionError as e:
                logger.error(e)
                continue
            except Exception as e:
                logger.exception(e)
                continue

        logger.info("result_worker exiting...")


class OneResultWorker(ResultWorker):
    def on_result(self, task, result):
        if not result:
            return
        if 'taskid' in task and 'project' in task and 'url' in task:
            logger.info('result %s:%s %s -> %.30r' % (
                task['project'], task['taskid'], task['url'], result))
            print(json.dumps({
                'taskid': task['taskid'],
                'project': task['project'],
                'url': task['url'],
                'result': result}))
            reveal_type(time)