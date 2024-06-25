from PySide2 import QtCore, QtWidgets, QtGui

from package.api.card import Collection, Card, COLLECTION_PATH

class AddCardDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Add Flash Card')
        self.setModal(True)
        self.setLayout(QtWidgets.QVBoxLayout())

        self.question_input = QtWidgets.QLineEdit(self)
        self.question_input.setPlaceholderText('Enter question')
        self.layout().addWidget(self.question_input)

        self.answer_input = QtWidgets.QLineEdit(self)
        self.answer_input.setPlaceholderText('Enter answer')
        self.layout().addWidget(self.answer_input)

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel, self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self.layout().addWidget(button_box)

    def get_question_and_answer(self):
        return self.question_input.text(), self.answer_input.text()
    
class QuizWindow(QtWidgets.QWidget):
    quizStopped = QtCore.Signal()  # Signal personnalisé pour indiquer que le quiz est arrêté

    def __init__(self, collection=None, parent=None):
        super().__init__(parent)
        self.collection = collection if collection else Collection()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # Enlever les décorations de la fenêtre
        self.setFixedSize(1000, 300)  # Taille fixe pour éviter le redimensionnement
        self.setup_ui()
        self.answer_seen = False

    def setup_ui(self) -> None:
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()
        self.choose_card()

    def create_widgets(self) -> None:
        self.lbl_question = QtWidgets.QLabel("", self)
        self.lbl_answer = QtWidgets.QLabel("", self)
        self.btn_show_answer = QtWidgets.QPushButton('Voir la réponse', self)
        self.btn_understood = QtWidgets.QPushButton('Bonne réponse', self)
        self.btn_not_understood = QtWidgets.QPushButton('Mauvaise réponse', self)
        self.btn_stop_quizz = QtWidgets.QPushButton('Arrêter le quiz', self)

    def modify_widgets(self) -> None:
        self.lbl_question.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_answer.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_answer.hide()
        
        self.btn_understood.setStyleSheet('background-color: green')
        self.btn_understood.setEnabled(False)
        self.btn_not_understood.setStyleSheet('background-color: red')
        self.btn_not_understood.setEnabled(False)

    def create_layouts(self) -> None:
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.btn_layout = QtWidgets.QHBoxLayout()

    def add_widgets_to_layouts(self) -> None:
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.lbl_question)
        self.main_layout.addWidget(self.lbl_answer)
        self.main_layout.addStretch()
        
        self.btn_layout.addWidget(self.btn_show_answer)
        self.btn_layout.addWidget(self.btn_understood)
        self.btn_layout.addWidget(self.btn_not_understood)
        self.btn_layout.addWidget(self.btn_stop_quizz)
        
        self.main_layout.addLayout(self.btn_layout)

    def setup_connections(self) -> None:
        self.btn_show_answer.clicked.connect(self.switch_card)
        self.btn_understood.clicked.connect(self.understood)
        self.btn_not_understood.clicked.connect(self.not_understood)
        self.btn_stop_quizz.clicked.connect(self.stop_quiz)  # Modifier la connexion ici

    def switch_card(self, reset : bool = False):
        if self.lbl_question.isVisible() and not reset:
            self.lbl_question.hide()
            self.lbl_answer.show()
            self.answer_seen = True
        elif reset:
            self.btn_understood.setEnabled(False)
            self.btn_not_understood.setEnabled(False)
            self.lbl_answer.hide()
            self.lbl_question.show()
        else:
            self.lbl_answer.hide()
            self.lbl_question.show()
            
        self.btn_show_answer.setText('Show Question' if self.lbl_answer.isVisible() else 'Show Answer')
        
        if self.answer_seen:
            self.btn_understood.setEnabled(True)
            self.btn_not_understood.setEnabled(True)

    def choose_card(self):
        self.card = self.collection.get_card()
        self.lbl_question.setText(self.card.question)
        self.lbl_answer.setText(self.card.answer)
        self.answer_seen = False
        
    def understood(self):
        self.card.understood_count_up()
        self.choose_card()
        self.switch_card(reset=True)
        
    def not_understood(self):
        self.card.understood_count_down()
        self.choose_card()
        self.switch_card(reset=True)

    def stop_quiz(self):
        self.quizStopped.emit()  # Émettre le signal lorsque le quiz est arrêté

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, ctx) -> None:
        super().__init__()
        self.ctx = ctx
        self.setWindowTitle("PyCards")
        self.collection = Collection()
        self.setup_ui()
        self.import_path = ""
        
    def setup_ui(self) -> None:
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()
    
    def create_widgets(self) -> None:
        # Créer le widget central
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Widgets
        self.toolbar = QtWidgets.QToolBar()
        self.table_widget = QtWidgets.QTableWidget()
        self.btn_add_card = QtWidgets.QPushButton("Ajouter une carte")
        self.btn_start_quiz = QtWidgets.QPushButton("Commencer le quiz")
        
        # Icons
        self.icon_load_collection = QtGui.QIcon(self.ctx.get_resource("download.svg"))
        self.icon_export_collection = QtGui.QIcon(self.ctx.get_resource("export.svg"))
        
        # Actions
        self.act_load = self.toolbar.addAction(self.icon_load_collection, "Load Collection")
        self.act_export = self.toolbar.addAction(self.icon_export_collection, "Export Collection")

    def modify_widgets(self) -> None:
        self.table_widget.setRowCount(0)  # Initialiser avec 0 lignes
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(['Question', 'Réponse'])
        self.table_widget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

    def create_layouts(self) -> None:
        self.main_layout = QtWidgets.QGridLayout()
        self.central_widget.setLayout(self.main_layout)
        self.quiz_layout = QtWidgets.QVBoxLayout()

    def add_widgets_to_layouts(self) -> None:
        self.addToolBar(self.toolbar)
        self.main_layout.addWidget(self.table_widget, 0, 0, 1, 2)
        self.main_layout.addWidget(self.btn_add_card, 1, 0)
        self.main_layout.addWidget(self.btn_start_quiz, 1, 1)

    def setup_connections(self) -> None:
        self.act_load.triggered.connect(self.load_collection)
        self.act_export.triggered.connect(self.export_collection)
        self.btn_add_card.clicked.connect(self.add_card)
        self.btn_start_quiz.clicked.connect(self.start_quiz)
        
    def load_collection(self) -> None:
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setMimeTypeFilters(["json"])
        file_dialog.setDirectory(COLLECTION_PATH)
        if file_dialog.exec_() == QtWidgets.QDialog.Accepted:
            selected_urls = file_dialog.selectedUrls()
            if selected_urls:
                collection_url = selected_urls[0]
                collection_path = collection_url.toLocalFile()
                self.import_path = collection_path
                print("Selected file:", collection_path)
                self.collection.load_collection(collection_path)
                self.populate_table_widget()
                
    def populate_table_widget(self):
        self.table_widget.setRowCount(len(self.collection.cards))
        for row, card in enumerate(self.collection.cards):
            question_item = QtWidgets.QTableWidgetItem(card.question)
            answer_item = QtWidgets.QTableWidgetItem(card.answer)
            
            # Centrer le texte dans les cellules
            question_item.setTextAlignment(QtCore.Qt.AlignCenter)
            answer_item.setTextAlignment(QtCore.Qt.AlignCenter)
            
            self.table_widget.setItem(row, 0, question_item)
            self.table_widget.setItem(row, 1, answer_item)
            
    def add_card(self) -> None:
        dialog = AddCardDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            question, answer = dialog.get_question_and_answer()
            self.collection.add_card(question, answer)
            self.populate_table_widget() 
            
    def export_collection(self) -> None:
        collection_name, ok = QtWidgets.QInputDialog.getText(self, 
                                                             "Export Collection",
                                                             "Enter collection name:")
        
        if ok:
            self.collection.export_collection(COLLECTION_PATH, f"{collection_name}.json")
            print(f"Collection {collection_name} exported successfully!")
    
    def start_quiz(self) -> None:
        self.wdg_quiz = QuizWindow(self.collection)
        self.wdg_quiz.quizStopped.connect(self.show_main_window)  # Connecter le signal quizStopped
        self.hide()
        self.wdg_quiz.show()

    def show_main_window(self):
        self.wdg_quiz.deleteLater()  # Supprimer le widget du quiz
        self.show()  # Réafficher la fenêtre principale lorsque le quiz est arrêté
        
    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        # Intercepter l'événement de fermeture de la fenêtre principale
        # Vous pouvez ajouter ici des opérations de nettoyage ou de confirmation
        
        reply = QtWidgets.QMessageBox.question(self, 'Message', 
            "Are you sure to quit?", QtWidgets.QMessageBox.Yes | 
            QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            if self.import_path:
                self.collection.export_collection(self.import_path)
            event.accept()
        else:
            event.ignore()


        