import sys
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QTextEdit
from PyQt5.QtCore import QSettings, Qt, pyqtSignal
from PyQt5.QtGui import QKeyEvent
from fuzzywuzzy import process


TEMPLATES = {
    'define': '''Please explain any challenging or unusual terms in the following passage. 
YOU MUST respond using the same language as the one that the passage is written in.
Passage:
{clipboard}
''',
    'translate': '''Translate the following passage to english:
{clipboard}''',
    'fun fact': '''Today is {date}. 
What is something fun and lighthearted that happened on this day in the past?''',
}


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
        self.setWindowTitle('Command Palette')
        self.setGeometry(100, 100, 600, 400)
        
        self.settings = QSettings("MyCompany", "MyApp")
        self.settings.clear()
        
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
        
        self.commands = list(TEMPLATES.keys())

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
            matches = process.extract(text, self.commands, limit=5)
            for match in matches:
                item = QListWidgetItem(match[0])
                self.resultsList.addItem(item)
            if not self.resultsList.count() == 0:
                self.setRowSelected(0) # Automatically select the first (closest match) item
        else:
            # If there's no text, show MRU or default commands
            self.populateMRUorDefaultResults()
    
    def populateMRUorDefaultResults(self):
        mruCommands = self.settings.value("mruCommands", [])
        showlist = []
        if mruCommands:
            for command in mruCommands:
                showlist.append(command)

        for command in self.commands:
            if len(showlist) >= 6:
                break
            if command in showlist:
                continue
            showlist.append(command)

        for item in showlist:
            self.resultsList.addItem(QListWidgetItem(item))
        self.setRowSelected(0)

    def setRowSelected(self, row_num):
        self.resultsList.setCurrentRow(row_num)
        key = self.resultsList.currentItem().text()
        self.preview.setPlainText(TEMPLATES[key])
    
    def itemSelected(self, item):
        self.processCommand(item.text())
    
    def selectHighlightedCommand(self):
        currentItem = self.resultsList.currentItem()
        if currentItem:
            self.processCommand(currentItem.text())
    
    def processCommand(self, commandText):
        # Update MRU commands list
        mruCommands = self.settings.value("mruCommands", [])
        if commandText in mruCommands:
            mruCommands.remove(commandText)
        mruCommands.insert(0, commandText)
        # Keep only the latest 5 MRU commands
        self.settings.setValue("mruCommands", mruCommands[:5])
        
        print(f"Selected command: {commandText}")
        self.commandSelected.emit(commandText)
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = CommandPalette()
    mainWin.show()
    sys.exit(app.exec_())
