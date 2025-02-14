import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt5.QtGui import QFont
import sqlite3
from Designs.collections_window import Ui_MainWindowcol
from Designs.training_window import Ui_MainWindowtrain
from Designs.main_window import Ui_MainWindow

ALPHABET = {"а", "б", "в", "г", "д", "е", "ё", "ж", "з", "и", "й", "к", "л", "м", "н", "о",
            "п", "р", "с", "т", "у", "ф", "х", "ц", "ч", "ш", "щ", "ъ", "ы", "ь", "э", "ю", "я"}


class FormatError(Exception):
    pass


class WordTypeError(Exception):
    pass


class Collectionsdialog(QMainWindow, Ui_MainWindowcol):
    def __init__(self):
        super().__init__()
        self.con = sqlite3.connect("DataBases/CollectionsData.db")
        self.cur = self.con.cursor()
        self.words_pairs = list()
        self.setupUi(self)
        self.InitUi()

    def InitUi(self):
        self.addButton.clicked.connect(self.addPair)
        self.createNew.clicked.connect(self.newTable)

    def addPair(self):
        try:
            if not (self.word.text() and self.translation.text()):
                raise FormatError
            if len(ALPHABET.intersection(set(self.word.text().lower()))) and len(ALPHABET.intersection(
                    set(self.translation.text().lower()))) == 0:
                raise WordTypeError
            if (self.word.text(), self.translation.text()) in self.words_pairs:
                raise ValueError
            self.words_pairs.append((self.word.text(), self.translation.text()))
            self.label.setText(f"Добавлена пара слов {self.word.text()} - {self.translation.text()}")
        except ValueError:
            self.label.setText('Такая пара уже существует в коллекции')
        except FormatError:
            self.label.setText('Введите названия слов')
        except WordTypeError:
            self.label.setText('В полях для ввода использованы неверные символы')

    def newTable(self):
        try:
            if self.collectionName.text() == '':
                raise ValueError
            else:
                self.cur.execute(f"""CREATE TABLE IF NOT EXISTS {self.collectionName.text()}(
                    id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                    word STRING  NOT NULL,
                    translation STRING  NOT NULL);
                """)
                for i in self.words_pairs:
                    self.cur.execute(
                        f'''INSERT INTO {self.collectionName.text()}(word,translation) VALUES('{i[0]}','{i[1]}')''')
                self.con.commit()
                self.label.setText('Коллекция добавлена')
                self.words_pairs.clear()
                ex.close()
                ex.show()
        except ValueError:
            self.label.setText('Введите название коллекции')


class Trainingwords(QMainWindow, Ui_MainWindowtrain):
    def __init__(self, name):
        super().__init__()
        self.setupUi(self)
        self.con = sqlite3.connect("DataBases/CollectionsData.db")
        self.cur = self.con.cursor()
        self.name = name
        self.count = 0
        self.true = 0
        self.false = 0
        self.words = self.cur.execute(f"""SELECT word, translation FROM {self.name}""").fetchall()
        self.InitUi()

    def InitUi(self):
        self.wordCount.setText(f"{self.count}/{len(self.words)} слов")
        self.word, self.translation = self.words[self.count][0], self.words[self.count][1]
        self.label.setText(self.word)
        self.okButton.clicked.connect(self.Compare)
        self.out.clicked.connect(self.close)
        self.answer.installEventFilter(self)

    def Compare(self):
        try:
            if self.answer.text():
                self.messages.setText('')
                if self.answer.text().lower() == self.translation.lower():
                    self.statusbar.setStyleSheet("background-color: rgb(0, 255, 0)")
                    self.statusbar.showMessage("Верно!")
                    self.true += 1
                    self.right.setText(f'Верных ответов: {self.true}')
                else:
                    self.statusbar.setStyleSheet("background-color: rgb(255, 0, 0)")
                    self.statusbar.showMessage("Неправильный ответ")
                    self.false += 1
                    self.wrong.setText(f'Неверных ответов: {self.false}')
                self.count += 1
                self.wordCount.setText(f"{self.count}/{len(self.words)} слов")
                if self.count == len(self.words):
                    self.okButton.setEnabled(False)
                    self.wordCount.setText(f"Тренировка завершена. Нажмите кнопку 'Выйти' для выхода")
                else:
                    self.word, self.translation = self.words[self.count][0], self.words[self.count][1]
                    self.label.setText(self.word)
                    self.answer.setText('')
            else:
                raise ValueError
        except ValueError:
            self.messages.setText('Введите ответ')

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress and obj is self.answer:
            if event.key() == QtCore.Qt.Key_Return and self.answer.hasFocus():
                self.Compare()
        return super().eventFilter(obj, event)

    def End(self):
        self.train.close()


class Translator(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setGeometry(600, 200, 800, 600)
        self.setWindowTitle('Главное окно')
        self.con = sqlite3.connect("DataBases/CollectionsData.db")
        self.cur = self.con.cursor()
        self.collections = list()
        self.InitUi()

    def InitUi(self):
        tables = self.cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()[1:]
        font = QFont()
        font.setFamily("Segoe UI Historic")
        font.setPointSize(14)
        for i in range(len(tables)):
            btn = QPushButton(self)
            btn.setFont(font)
            btn.setGeometry(260 * (i % 3) + 40, 180 * (i // 3) + 90, 150, 130)
            btn.clicked.connect(self.Training)
            btn.setObjectName(str(tables[i][0]))
            btn.setText(str(tables[i][0]))
            self.collections.append(btn)
        self.newCollection = QPushButton(self)
        self.newCollection.setFont(font)
        self.newCollection.setGeometry(260 * (len(tables) % 3) + 40, 180 * (len(tables) // 3) + 90, 150, 130)
        self.newCollection.clicked.connect(self.New)
        self.newCollection.setText('+')

    def Training(self):
        name = self.sender().objectName()
        self.train = Trainingwords(name)
        self.train.show()

    def New(self):
        self.new = Collectionsdialog()
        self.new.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Translator()
    ex.show()
    sys.exit(app.exec_())
