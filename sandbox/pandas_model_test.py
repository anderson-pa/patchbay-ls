import pandas as pd
from PySide2.QtWidgets import QHBoxLayout, QTableView, QFrame

from ui.models import PandasModel


class Patch:
    def __init__(self):
        self.widgets = {}
        self.data = pd.DataFrame(columns=['col1', 'col2'])
        self.model = PandasModel(self.data)
        self.run()

        self.ui = self.make_ui()

    def make_ui(self):
        hbox = QHBoxLayout()

        value_table = QTableView()
        self.widgets['value_table'] = value_table

        value_table.setModel(self.model)

        hbox.addWidget(value_table)

        main_widget = QFrame()
        main_widget.setLayout(hbox)

        return main_widget

    def run(self):
        data = pd.Series({'col1': 'hello world',
                          'col2': 0.12345})
        self.data = self.data.append(data, ignore_index=True)
        self.model.layoutAboutToBeChanged.emit()
        self.model.update(self.data)

        self.model.layoutChanged.emit()

    def close(self):
        pass
