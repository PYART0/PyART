from __future__ import unicode_literals

from ..models import BaseComment
from ..users import User


class GistComment(BaseComment):


    def _update_attributes(self, comment):
        reveal_type(comment)