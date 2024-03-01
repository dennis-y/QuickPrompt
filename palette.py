import sys
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QTextEdit
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeyEvent
from settings import settings


class CommandLineEdit(QLineEdit):
    enterPressed = pyqtSignal()
    arrowUpPressed = pyqtSignal()
    arrowDownPressed = pyqtSignal()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.enterPressed.emit()
        elif event.key() == Qt.Key_Up:
            self.arrowUpPressed.emit()
        elif event.key() == Qt.Key_Down:
            self.arrowDownPressed.emit()
        else:
            super().keyPressEvent(event)


class CommandPalette(QDialog):
    commandSelected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Prompt Palette')
        self.setGeometry(100, 100, 600, 400)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.searchBar = CommandLineEdit(self)
        self.searchBar.setPlaceholderText("Type here to search...")
        self.searchBar.textChanged.connect(self.updateResults)
        self.searchBar.enterPressed.connect(self.selectHighlightedCommand)
        self.searchBar.arrowUpPressed.connect(self.navigateUp)
        self.searchBar.arrowDownPressed.connect(self.navigateDown) 
        layout.addWidget(self.searchBar)

        self.resultsList = QListWidget()
        self.resultsList.setMinimumHeight(300)
        self.resultsList.itemActivated.connect(self.itemSelected)
        layout.addWidget(self.resultsList)

        self.preview = QTextEdit(self)
        self.preview.setMinimumHeight(400)
        layout.addWidget(self.preview)
        
        # TODO: Rename MRU -> frequent
        # Populate the list with MRU commands or default commands
        self.populateMRUorDefaultResults()
    
    def navigateUp(self):
        currentRow = self.resultsList.currentRow()
        self.setRowSelected(max(0, currentRow - 1))

    def navigateDown(self):
        currentRow = self.resultsList.currentRow()
        self.setRowSelected(min(self.resultsList.count() - 1, currentRow + 1))

    def updateResults(self, text):
        self.resultsList.clear()
        if text:
            for match in settings.getMatchingPromptNames(text):
                item = QListWidgetItem(match[0])
                self.resultsList.addItem(item)
            if not self.resultsList.count() == 0:
                self.setRowSelected(0) # Automatically select the first (closest match) item
        else:
            # If there's no text, show MRU or default commands
            self.populateMRUorDefaultResults()
    
    def populateMRUorDefaultResults(self):
        for name in settings.getMostRecentPromptNames():
            self.resultsList.addItem(QListWidgetItem(name))
        self.setRowSelected(0)

    def setRowSelected(self, row_num):
        self.resultsList.setCurrentRow(row_num)
        key = self.resultsList.currentItem().text()
        self.preview.setPlainText(settings.getTemplateForPromptNamed(key))
    
    def itemSelected(self, item):
        self.processCommand(item.text())
    
    def selectHighlightedCommand(self):
        currentItem = self.resultsList.currentItem()
        if currentItem:
            self.processCommand(currentItem.text())
    
    def processCommand(self, commandText):
        print(f"Selected command: {commandText}")
        self.commandSelected.emit(commandText)
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = CommandPalette()
    mainWin.show()
    sys.exit(app.exec_())
