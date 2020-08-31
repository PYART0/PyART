from __future__ import unicode_literals

from ..models import GitHubCore
from ..repos import Repository


class CodeSearchResult(GitHubCore):
    def _update_attributes(self, data):
        reveal_type(data)