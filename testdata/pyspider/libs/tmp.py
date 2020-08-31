import six
import platform
import multiprocessing
from multiprocessing.queues import Queue as BaseQueue



class SharedCounter(object):

    def __init__(self, n=0):
        self.count = multiprocessing.Value('i', n)

    def increment(self, n=1):
        with self.count.get_lock():
            self.count.value += n

    @property
    def value(self):
        return self.count.value


class MultiProcessingQueue(BaseQueue):
    def __init__(self, *args, **kwargs):
        super(MultiProcessingQueue, self).__init__(*args, **kwargs)
        self.size = SharedCounter(0)

    def put(self, *args, **kwargs):
        self.size.increment(1)
        super(MultiProcessingQueue, self).put(*args, **kwargs)

    def get(self, *args, **kwargs):
        v = super(MultiProcessingQueue, self).get(*args, **kwargs)
        self.size.increment(-1)
        return v

    def qsize(self):
        return self.size.value


if platform.system() == 'Darwin':
    if hasattr(multiprocessing, 'get_context'):  # for py34
        def Queue(maxsize=0):
            reveal_type(multiprocessing)