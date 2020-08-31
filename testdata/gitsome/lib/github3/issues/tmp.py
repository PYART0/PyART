from __future__ import unicode_literals

from ..models import GitHubCore
from ..users import User


class IssueEvent(GitHubCore):
    def _update_attributes(self, event):
        reveal_type(event)