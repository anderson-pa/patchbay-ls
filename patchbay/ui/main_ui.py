import os
from importlib import import_module

from PySide2.QtCore import QSettings
from PySide2.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QFrame

import ui.actions


class PatchBay(QMainWindow):
    """Main Screen."""

    def __init__(self):
        super().__init__()
        self.config = None
        self.current_configuration = ''
        self.actions = self.get_actions()
        self.widgets = {}

        self.add_menubar()
        self.add_toolbar()

        self.statusBar()
        self.init_ui()

    def get_actions(self):
        """Retrieve user actions for this user interface.

        :return: dict of QActions keyed by name"""
        actions = {'about': ui.actions.about(self),
                   'close': ui.actions.close(self),
                   'load': ui.actions.load(self),
                   'quit': ui.actions.quit(self),
                   'run': ui.actions.run(self),
                   'stop': ui.actions.stop(self)}
        return actions

    def add_menubar(self):
        """Add a menu bar to the interface."""
        menubar = self.menuBar()

        file_menu = menubar.addMenu('&File')
        file_menu.addAction(self.actions['load'])
        file_menu.addAction(self.actions['close'])
        file_menu.addAction(self.actions['quit'])

        help_menu = menubar.addMenu('&Help')
        help_menu.addAction(self.actions['about'])

    def add_toolbar(self):
        """Add a toolbar to the interface."""
        self.toolbar = self.addToolBar('Main Toolbar')
        self.toolbar.setObjectName('MainToolbar')
        self.toolbar.addAction(self.actions['run'])
        self.toolbar.addAction(self.actions['stop'])

    def add_config_actions(self, actions):
        for action in actions:
            self.toolbar.addAction(action(self))

    def init_ui(self):
        """Initialize and show the user interface."""
        self.restore_settings()

        self.setWindowTitle('Patch Bay')
        self.show()
        if self.current_configuration:
            self.load_configuration(self.current_configuration)

    def restore_settings(self):
        """Restore saved settings prior session."""
        settings = QSettings()
        self.restoreGeometry(settings.value('MainWindow/Geometry', b''))
        self.restoreState(settings.value('MainWindow/State', b''))
        self.current_configuration = (settings.value('LastPatchFile', b''))
        settings.setValue('LastPatchFile', '')

    def closeEvent(self, event):
        """Persist user settings before calling parent closeEvent."""
        if self.config:
            self.config.close()

        settings = QSettings()
        settings.setValue('MainWindow/Geometry', self.saveGeometry())
        settings.setValue('MainWindow/State', self.saveState())
        settings.setValue('LastPatchFile', self.current_configuration)
        QMainWindow.closeEvent(self, event)

    def run(self):
        try:
            self.config.run()
        except AttributeError:
            pass

    def stop(self):
        try:
            self.config.stop()
        except AttributeError:
            pass

    def load_configuration(self, config_file=None):
        if not config_file:
            dialog = QFileDialog(self)
            dialog.setFileMode(QFileDialog.AnyFile)
            dialog.setNameFilter("Configurations (*.py *.xpm *.jpg)")
            dialog.setViewMode(QFileDialog.Detail)
            dialog.setOption(QFileDialog.DontUseNativeDialog)

            if dialog.exec_():
                file = dialog.selectedFiles()
                config_file = os.path.splitext(os.path.basename(file[0]))[0]
            else:
                return
        if self.config:
            self.config.close()

        self.config = import_module(config_file).Patch(self)
        self.setCentralWidget(self.config.ui)
        self.add_config_actions(self.config.get_actions())
        self.current_configuration = config_file

    def close_configuration(self):
        try:
            self.config.close()
        except AttributeError:
            pass

        self.config = None
        self.setCentralWidget(QFrame())
        self.current_configuration = None

    def show_about_dialog(self):
        """Display a dialog with information about the software."""
        QMessageBox.about(self, 'Patch Bay',
                          'Written by:<br>'
                          'Phillip Anderson<br>')
