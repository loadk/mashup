# -*- coding: utf-8 -*-

from __future__ import with_statement
import codecs, os

import yaml
from yaml import YAMLError

class ConfigLoader(object):

    def __init__(self, strict=False):
        self.strict = strict
        self.config = {}

        self.default = dict(
            date_input = '%d/%m/%Y',
            date_output = '%A, %d. %B %Y',
            markdown_extensions = ['codehilite', 'extra']
        )

    def load_file(self, filepath):
        """
        Load a configuration file from filepath, unless such file does exist,
        and merge the settings with the current configuration.
        """
        if os.path.isfile(filepath):
            try:
                with codecs.open(filepath, encoding='utf-8') as fd:
                    self.config.update(yaml.load(fd))
                    return self.config

            except (YAMLError, IOError):
                exit("error: can't load the configuration file: %s" % filepath)

        # In strict mode: raise an error.
        # In normal mode: return the loaded configuration unless it's empty
        #                 in which case, return the default settings.
        else:
            if self.strict:
                exit("strict error: config file not found: %s" % filepath)
            else:
                return self.config or self.default

