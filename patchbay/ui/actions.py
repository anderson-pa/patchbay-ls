from PySide2.QtGui import QIcon, QKeySequence
from PySide2.QtWidgets import QAction

from utility import resources_path


def about(parent):
    action = QAction('About...', parent)
    action.setStatusTip('About...')
    action.triggered.connect(parent.show_about_dialog)
    return action


def close(parent):
    action = QAction('Close', parent)
    action.setIcon(QIcon(resources_path('ionicons/md-close.svg')))
    action.setStatusTip('Close')
    action.triggered.connect(parent.close_configuration)
    return action


def load(parent):
    action = QAction('Load...', parent)
    action.setIcon(QIcon(resources_path('ionicons/md-open.svg')))
    action.setStatusTip('Load...')
    action.triggered.connect(parent.load_configuration)
    return action


def run(parent):
    action = QAction('Run', parent)
    action.setIcon(QIcon(resources_path('ionicons/md-play.svg')))
    action.setShortcut(QKeySequence('Ctrl+R'))
    action.setStatusTip('Run')
    action.triggered.connect(parent.run)
    return action


def stop(parent):
    action = QAction('Stop', parent)
    action.setIcon(QIcon(resources_path('ionicons/md-square.svg')))
    action.setShortcut(QKeySequence('Esc'))
    action.setStatusTip('Stop')
    action.triggered.connect(parent.stop)
    return action


def new_video_window(parent):
    action = QAction('Video Window', parent)
    action.setIcon(QIcon(resources_path('ionicons/md-image.svg')))
    action.setStatusTip('New Video Window')
    action.triggered.connect(parent.config.open_new_video_window)
    return action


def quit(parent):
    action = QAction('Quit', parent)
    action.setShortcut(QKeySequence('Ctrl+Q'))
    action.setStatusTip('Quit')
    action.triggered.connect(parent.close)
    return action
