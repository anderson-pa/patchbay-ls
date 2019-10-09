import asyncio
import sys

from PySide2.QtWidgets import QApplication
from asyncqt import QEventLoop

from ui.main_ui import PatchBay

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setOrganizationName('Patch Bay')
    app.setOrganizationDomain('patchbay.io')
    app.setApplicationName('Patch Bay')

    asyncio.set_event_loop(QEventLoop(app))

    patchbay_ui = PatchBay()
    sys.exit(app.exec_())
