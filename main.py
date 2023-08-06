import sys
import time
import os

from browser import init_browser, get_detail
from area import get_province, get_city, search
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QWidget,
    QApplication,
    QLabel,
    QLineEdit,
    QPushButton,
    QGridLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QComboBox
)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class JDTools(QWidget):
    def __init__(self):
        super().__init__()
        # Init for Search
        # self.debug = True
        self.debug = False
        self.browser = init_browser(self.debug)

        # Init For Area
        self.province_data = get_province()
        self.current_province_id = 1
        self.city_data = get_city(self.current_province_id)
        self.current_city_id = next(iter(self.city_data))
        self.search_data = search(self.current_city_id)
        self.current_search_id = next(iter(self.search_data))
        self.areaId_value = ""
        self.initUI()

    def initUI(self):
        self.grid = QGridLayout()
        self.grid.setSpacing(10)

        self.initSearchUI()
        self.initAreaUI()

        self.setLayout(self.grid)
        self.setWindowTitle('JD Tools')
        self.setWindowIcon(QIcon(resource_path('logo.ico')))
        self.show()

    def initSearchUI(self):
        skuLabel = QLabel('商品SKU')
        self.skuEdit = QLineEdit()
        self.grid.addWidget(skuLabel, 1, 0)
        self.grid.addWidget(self.skuEdit, 1, 1)

        self.startButton = QPushButton("查询")
        self.startButton.clicked[bool].connect(self.startSearch)
        self.grid.addWidget(self.startButton, 1, 2)

        self.detailTable = QTableWidget(0, 2)
        self.detailTable.setHorizontalHeaderLabels(['Key', 'Value'])
        self.detailTable.setHidden(True)
        self.detailTable.setEditTriggers(QTableWidget.NoEditTriggers)  # 不可编辑
        self.detailTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.detailTable.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.grid.addWidget(self.detailTable, 2, 0, 1, 3)

        self.statusLabel = QLabel('等待查询')
        self.grid.addWidget(self.statusLabel, 3, 0, 1, 3)

    def initAreaUI(self):
        self.combo1, self.combo2, self.combo3 = QComboBox(), QComboBox(), QComboBox()

        self.set_combo_data(self.combo1, self.province_data, default_key=self.current_province_id)
        self.set_combo_data(self.combo2, self.city_data)
        self.set_combo_data(self.combo3, self.search_data, default_key=72)

        self.combo1.currentIndexChanged.connect(self.update_combo2)
        self.combo2.currentIndexChanged.connect(self.update_combo3)
        self.combo3.currentIndexChanged.connect(self.update_label)

        self.grid.addWidget(self.combo1, 0, 0)
        self.grid.addWidget(self.combo2, 0, 1)
        self.grid.addWidget(self.combo3, 0, 2)

    def set_combo_data(self, combo, data, default_key=None):
        combo.clear()
        combo.addItems([data[key] for key in sorted(data.keys())])
        if default_key and default_key in data:
            combo.setCurrentText(data[default_key])

    def update_combo2(self):
        self.current_province_id = self.get_key_from_value(self.province_data, self.combo1.currentText())
        self.city_data = get_city(self.current_province_id)
        self.set_combo_data(self.combo2, self.city_data)
        self.update_combo3()

    def update_combo3(self):
        self.current_city_id = self.get_key_from_value(self.city_data, self.combo2.currentText())
        if self.current_city_id not in self.city_data:
            self.current_city_id = next(iter(self.city_data))
        self.search_data = search(self.current_city_id)
        self.set_combo_data(self.combo3, self.search_data)
        self.update_label()

    def update_label(self):
        self.current_search_id = self.get_key_from_value(self.search_data, self.combo3.currentText())
        self.areaId_value = f"{self.current_province_id}_{self.current_city_id}_{self.current_search_id}_0"
        
        # Check if areaId already exists in the table
        self.detailTable.setHidden(False)
        for row in range(self.detailTable.rowCount()):
            if self.detailTable.item(row, 0).text() == "areaId":
                self.detailTable.item(row, 1).setText(self.areaId_value)  # Update its value
                break
        else:
            # If areaId is not found in the table, add it
            current_row = self.detailTable.rowCount()
            self.detailTable.insertRow(current_row)
            self.detailTable.setItem(current_row, 0, QTableWidgetItem("areaId"))
            self.detailTable.setItem(current_row, 1, QTableWidgetItem(self.areaId_value))

    @staticmethod
    def get_key_from_value(data, value):
        return next((key for key, val in data.items() if val == value), None)

    def startSearch(self):
        self.statusLabel.setText('正在查询...')
        start_time = time.time()

        skuid = self.skuEdit.text()
        self.disableStartBtn()

        try:
            result = get_detail(self.browser, skuid)
            self.detailTable.setRowCount(len(result))
            for row, (key, value) in enumerate(result.items()):
                self.detailTable.setItem(row, 0, QTableWidgetItem(str(key)))
                self.detailTable.setItem(row, 1, QTableWidgetItem(str(value)))
            if self.areaId_value:
                current_row = self.detailTable.rowCount()
                self.detailTable.insertRow(current_row)
                self.detailTable.setItem(current_row, 0, QTableWidgetItem("areaId"))
                self.detailTable.setItem(current_row, 1, QTableWidgetItem(self.areaId_value))
            self.detailTable.setFixedHeight(self.detailTable.verticalHeader().length() + self.detailTable.horizontalHeader().height() + self.detailTable.rowHeight(0) * self.detailTable.rowCount())
            self.detailTable.setHidden(False)

            end_time = time.time()
            elapsed_time = end_time - start_time
            self.statusLabel.setText(f'查询成功，耗时 {elapsed_time:.2f} 秒')
        except Exception as e:
            self.statusLabel.setText('查询失败')
        finally:
            self.resumeSatrtBtn()

    def disableStartBtn(self):
        self.startButton.setDisabled(True)

    def resumeSatrtBtn(self):
        self.startButton.setDisabled(False)

def main():
    app = QApplication(sys.argv)
    ui = JDTools()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()