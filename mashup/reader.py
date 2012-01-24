# -*- coding: utf-8 -*-

from __future__ import with_statement
import codecs, os, re, sys

import yaml
from yaml import YAMLError

#
# Item reading/crawler:
#

def has_yaml_header(filepath):
    """
    Open filepath as a binary file and check if it can be a content item.
    It must start with either '---' or UTF-8 BOM + '---'.
    """
    try:
        with open(filepath, 'rb') as fd:
            test = fd.read(3)

            return (test == b'---' or
                   (test == codecs.BOM_UTF8 and fd.read(3) == b'---'))

    except IOError as err:
        exit("error reading: %s \n %s" % (filepath, str(err)))

def read_content_item(filepath):
    """
    Open filepath as UTF-8, split it as an item into Yaml header and content
    and return a dict where both are merged.
    """
    try:
        with codecs.open(filepath, encoding='utf-8') as fd:
            parts = re.split('^---+\s*\n', fd.read(), maxsplit=2, flags = re.M)

            if len(parts) != 3:
                raise ValueError("invalid item header: %s" % filepath)

            header = yaml.load(parts[1])
            content = parts[2]

            return dict(header or {}, src = filepath, raw = content, itemtype = 'content')

    # not exhaustive against all the exceptions that `yaml.load' may throw:
    except (IOError, ValueError, YAMLError) as err:
        exit("error reading item: %s \n %s" % (filepath, str(err)))

def read_page_item(filepath):
    """
    Same as above, but for single-page items, that is: HTML and XML files.
    """
    try:
        with codecs.open(filepath, encoding='utf-8') as fd:
            content = fd.read()
            return dict(src = filepath, raw = content, itemtype = 'page')

    except IOError as err:
        exit("error reading page: %s \n %s" % (filepath, str(err)))

def read_static_item(filepath):
    """
    Same as above, but for static items such as binary files.
    """
    return dict(src = filepath, itemtype = 'static')

def read_item(filepath, section):
    """
    Read any given item, which will result in:
    - .html or .xml?: a page item
    - Yaml header present?: a content item
    - otherwise: a static item
    """
    if section.lower() in ['html', 'xml']: return read_page_item(filepath)

    if has_yaml_header(filepath):
        return read_content_item(filepath)
    else:
        return read_static_item(filepath)

def get_item_section(filename):
    """
    An item section is calculated from its filename extension.
    This function supports both 'multiple' extensions
    or no extension at all which will return '.':

      >>> get_item_section("Foo.bar.baz")
      'bar.baz'
      >>> get_item_section("noextension")
      '.'
    """
    return ''.join(filename.split('.', 1)[1:]) or '.'

def walk(dirpath):
    """
    Search dirpath recursively and gather all the items it contains.
    Returns a dict, where the key is the file extension, and the value
    is a list of all the items in that section.
    """
    items = {}

    for root, dirs, files in os.walk(dirpath):
        for filename in files:
            filepath = os.path.join(root, filename)
            section = get_item_section(filename)
            item = read_item(filepath, section)

            items.setdefault(section, [])
            items[section].append(item)

    return items

