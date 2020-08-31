import logging
import os
import sys

    LEVEL = logging.DEBUG
else:
    level_name = os.environ.get("ALLENNLP_LOG_LEVEL")




def _transformers_log_filter(record):
    reveal_type(record.msg)