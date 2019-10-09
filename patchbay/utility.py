import os
import sys


def app_path(relative=''):
    """Get the absolute path to the application root.

    :param relative: subpath to append to the returned path
    :return: string path
    """
    path_root = os.path.dirname(__file__)
    if hasattr(sys, "_MEIPASS"):
        path_root = sys._MEIPASS
    return os.path.join(path_root, relative)


def resources_path(relative=''):
    """Get the absolute path to the resource directory.

    :param relative: subpath to append to the returned path
    :return: string path
    """
    return os.path.join(app_path('resources'), relative)
