from __future__ import unicode_literals

from .models import GitHubCore


class License(GitHubCore):

    CUSTOM_HEADERS = {
        'Accept': 'application/vnd.github.drax-preview+json'
    }

    def _update_attributes(self, license):
        reveal_type(license)