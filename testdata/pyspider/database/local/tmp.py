import os
import re
import six
import glob
import logging

from pyspider.database.base.projectdb import ProjectDB as BaseProjectDB


class ProjectDB(BaseProjectDB):

    def __init__(self, files):
        self.files = files
        self.projects = {}
        self.load_scripts()

    def load_scripts(self):
        project_names = set(self.projects.keys())
        for path in self.files:
            for filename in glob.glob(path):
                name = os.path.splitext(os.path.basename(filename))[0]
                if name in project_names:
                    project_names.remove(name)
                updatetime = os.path.getmtime(filename)
                if name not in self.projects or updatetime > self.projects[name]['updatetime']:
                    project = self._build_project(filename)
                    if not project:
                        continue
                    self.projects[project['name']] = project

        for name in project_names:
            del self.projects[name]

    rate_re = re.compile(r'^\s*#\s*rate.*?(\d+(\.\d+)?)', re.I | re.M)
    burst_re = re.compile(r'^\s*#\s*burst.*?(\d+(\.\d+)?)', re.I | re.M)

    def _build_project(self, filename):
        try:
            with open(filename) as fp:
                script = fp.read()
            m = self.rate_re.search(script)
            if m:
                rate = float(m.group(1))
            else:
                rate = 1

            m = self.burst_re.search(script)
            if m:
                burst = float(m.group(1))
            else:
                burst = 3

            return {
                'name': os.path.splitext(os.path.basename(filename))[0],
                'group': None,
                'status': 'RUNNING',
                'script': script,
                'comments': None,
                'rate': rate,
                'burst': burst,
                'updatetime': os.path.getmtime(filename),
            }
        except OSError as e:
            logging.error('loading project script error: %s', e)
            return None

    def get_all(self, fields=None):
        for projectname in self.projects:
            yield self.get(projectname, fields)

    def get(self, name, fields=None):
        if name not in self.projects:
            return None
        project = self.projects[name]
        result = {}
        for f in fields or project:
            if f in project:
                result[f] = project[f]
            else:
                result[f] = None
        return result

    def check_update(self, timestamp, fields=None):
        self.load_scripts()
        reveal_type(six)