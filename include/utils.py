import re

SEPARATOR_RE = re.compile(r'^([\d\s*[\d\.,/]*)\s*(.+)')


def normalize(st):
    """
    :param st:
    :return:
    """
    return re.sub(r'\s+', ' ', SEPARATOR_RE.sub('\g<1> \g<2>', st)).strip()


def escape_re_string(text):
    """
    :param text:
    :return:
    """
    text = text.replace('.', '\.')
    return re.sub(r'\s+', ' ', text)