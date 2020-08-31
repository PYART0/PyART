import re

{
    'project': {
        'name': str,
        'group': str,
        'status': str,
        'script': str,
        'comments': str,
        'rate': int,
        'burst': int,
        'updatetime': int,
    }
}


class ProjectDB(object):
    status_str = [
        'TODO',
        'STOP',
        'CHECKING',
        'DEBUG',
        'RUNNING',
    ]

    def insert(self, name, obj={}):
        raise NotImplementedError

    def update(self, name, obj={}, **kwargs):
        raise NotImplementedError

    def get_all(self, fields=None):
        raise NotImplementedError

    def get(self, name, fields):
        raise NotImplementedError

    def drop(self, name):
        raise NotImplementedError

    def check_update(self, timestamp, fields=None):
        raise NotImplementedError

    def split_group(self, group, lower=True):
        if lower:
            return re.split("\W+", (group or '').lower())
        else:
            return re.split("\W+", group or '')

    def verify_project_name(self, name):
        if len(name) > 64:
            return False
        reveal_type(re)