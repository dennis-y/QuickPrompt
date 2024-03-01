import sys
import os
import json
from PyQt5.QtGui import QKeyEvent, QTextCursor
from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QVBoxLayout, QPushButton, QDesktopWidget
from PyQt5.QtCore import QObject, QTimer, QThread, pyqtSignal, QEvent, Qt, QSettings

from datetime import datetime

import palette
import unified_chat_client


class Worker(QThread):
    data_received = pyqtSignal(str)

    def __init__(self, query):
        super().__init__()
        self.query = query
        self.acc = f'```\n{self.query}\n```\n---\n'

    def run(self):
        self.data_received.emit(self.acc)
        for chunk in unified_chat_client.call_model(self.query):
            self.acc += chunk
            self.data_received.emit(self.acc)


# TODO: combine filters
class OpenPaletteEventFilter(QObject):
    openPalette = pyqtSignal()

    def eventFilter(self, watched, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_P and event.modifiers() == Qt.ControlModifier:
                self.openPalette.emit()
                return True
        return super().eventFilter(watched, event)

class EventFilter(QObject):
    enterPressed = pyqtSignal()
    openPalette = pyqtSignal()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            key_event = event

            if key_event.key() == Qt.Key_Return:
                if not key_event.modifiers():
                    self.enterPressed.emit()
                    return True
            
        return False  # Return False to pass the event to the target object


class PlainTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def insertFromMimeData(self, source):
        if source.hasText():
            self.insertPlainText(source.text())
        else:
            super().insertFromMimeData(source)


class StackedTextEdits(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        self.settings = QSettings("MyCompany", "MyApp")

        layout = QVBoxLayout()

        self.modelResponseArea = QTextEdit(self)
        self.modelResponseArea.setMinimumHeight(800)
        self.modelResponseArea.setPlaceholderText("Model response")

        self.userArea = PlainTextEdit(self)
        self.userArea.setMinimumHeight(200) 
        self.userArea.setFocus()
        self.eventFilter = EventFilter()
        self.userArea.installEventFilter(self.eventFilter)
        self.eventFilter.enterPressed.connect(self.run_query)

        self.openPaletteFilter = OpenPaletteEventFilter()
        self.installEventFilter(self.openPaletteFilter)
        self.openPaletteFilter.openPalette.connect(self.openPalette)

        layout.addWidget(self.userArea)
        layout.addWidget(self.modelResponseArea)

        self.setLayout(layout)

        screen_geometry = QDesktopWidget().screenGeometry()

        width = screen_geometry.width() // 2
        height = screen_geometry.height()
        x = screen_geometry.width() // 2  # Start from the middle of the screen
        y = 0
        
        self.setGeometry(x, y, width, height)

        self.setWindowTitle('QuickPrompt')
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        mruCommands = self.settings.value("mruCommands", [])
        if mruCommands:
            self.commandSelected(mruCommands[0])

        self.userArea.setFocus()
        self.show()

    def append_text_to_model_response(self, text):
        # TODO: syntax highlighting for code
        self.modelResponseArea.setMarkdown(text)
        self.modelResponseArea.verticalScrollBar().setValue(
            self.modelResponseArea.verticalScrollBar().maximum())

    def run_query(self):
        query = self.userArea.toPlainText()
        self.userArea.setText('')
        self.worker = Worker(query)
        self.worker.data_received.connect(self.append_text_to_model_response)
        self.worker.start()

    def openPalette(self):
        self.palette = palette.CommandPalette(self)
        self.palette.commandSelected.connect(self.commandSelected)
        self.palette.exec_()
    
    def commandSelected(self, command):
        template = palette.TEMPLATES[command]
        text = template.format_map({
            'clipboard':  QApplication.clipboard().text(),
            'date': datetime.now().strftime("%B %d, %Y"),
        })
        self.userArea.setPlainText(text)
        self.userArea.setFocus()
        self.userArea.moveCursor(QTextCursor.End)

    # Close on focus lost. not sure if i want this
    # Maybe this would be good if there is a strong history
    # def event(self, event):
    #     # Check for focus out event
    #     if event.type() == QEvent.WindowDeactivate:
    #         self.close()  # Close the application
    #     return super().event(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()


def main():
    import time
    start_time = time.time()
    app = QApplication(sys.argv)
    font = app.font()
    font.setPointSize(16)
    app.setFont(font)
    ex = StackedTextEdits()
    end_time = time.time()
    print(f"Startup Time: {end_time - start_time} seconds")
    code = app.exec_()
    sys.exit(code)

if __name__ == '__main__':
    main()
