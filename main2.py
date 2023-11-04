import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication, QLabel, QLineEdit,
                             QComboBox, QPushButton, QTreeView, QMessageBox,
                             QInputDialog, QCalendarWidget, QGridLayout, QWidget, QAction)
from PyQt5.QtCore import QTime
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QToolTip, QHeaderView, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt
class SalaoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.base_style = """
            * {
                font-size: 16pt; /* Tamanho de fonte grande para todos os elementos */
            }
            QHeaderView::section {
                padding-left: 10px;
                padding-right: 10px;
                border: 1px solid black;  /* This is optional. */
                font-size: 16pt; /* Exemplo de tamanho de fonte para o cabeçalho */
            }
            QTableView::item {
                padding: 50px;
                border: 1px solid #444;
                font-size: 9pt; /* Exemplo de tamanho de fonte para itens da tabela */
            }
            QCalendarWidget QHeaderView::section {
                padding: 5px;
                font-size: 8pt; /* Exemplo de tamanho de fonte para cabeçalho do calendário */
            }
            """


        # Aplicar o estilo base inicialmente
        self.setStyleSheet(self.base_style)
        self.toggle_dark_theme(False)  # Iniciar com o modo claro, por exemplo

        self.setWindowTitle("Sistema de Agendamento para Salão de Cabeleireiro")
        self.agendamentos = {}
        
        # Cria um QTabWidget
        self.tab_widget = QTabWidget(self)
        self.setCentralWidget(self.tab_widget)
        # Alterando a fonte apenas das abas do QTabWidget
        font_aba = QFont()
        font_aba.setPointSize(12)  # Ajuste o tamanho da fonte conforme desejar
        self.tab_widget.tabBar().setFont(font_aba)

        # Primeira aba
        self.tab1 = QWidget()
        self.tab_widget.addTab(self.tab1, "Agendamento")
        font = QFont()
        font.setPointSize(20)
        self.tab_widget.setFont(font)
        self.setup_first_tab()
        
        # Segunda aba
        self.tab2 = QWidget()
        self.tab_widget.addTab(self.tab2, "Clientes")
        self.setup_second_tab()
        
        self.show()

    def setup_first_tab(self):
        grid_layout = QGridLayout(self.tab1)
        self.calendario = QCalendarWidget()
        self.calendario.setGridVisible(True)
        self.calendario.selectionChanged.connect(self.atualizar_tabela_com_base_na_data)
        self.label_nome = QLabel("Nome do Cliente:")
        self.entrada_nome = QLineEdit()
        self.label_telefone = QLabel("Telefone do Cliente:")
        self.entrada_telefone = QLineEdit()
        self.label_funcionario = QLabel("Selecione o Funcionário:")
        self.selecao_funcionario = QComboBox()
        self.selecao_funcionario.addItems(["Funcionario1", "Funcionario2", "Funcionario3", "Funcionario4", "Funcionario5"])
        self.label_operacao = QLabel("Serviço:")
        self.entrada_operacao = QComboBox()
        self.entrada_operacao.addItems(["Corte", "Pintura", "Manicure", "Outros"])
        self.entrada_operacao.setEditable(self.entrada_operacao.currentIndex() == 3)
        self.entrada_operacao.currentIndexChanged.connect(self.operacao_selecionada)
        self.botao_agendar = QPushButton("Agendar")
        self.botao_agendar.clicked.connect(self.preparar_agendamento)
        self.tabela_horarios = QTreeView()
        self.tabela_horarios.setRootIsDecorated(False)
        self.tabela_horarios.setHeaderHidden(False)
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Hora', 'Funcionario1', 'Funcionario2', 'Funcionario3', 'Funcionario4', 'Funcionario5'])
        self.tabela_horarios.setModel(self.model)
        self.dark_theme_enabled = False
        grid_layout.addWidget(self.calendario, 0, 0, 1, 2)  # Row, Col, Rowspan, Colspan
        grid_layout.addWidget(self.label_nome, 1, 0)
        grid_layout.addWidget(self.entrada_nome, 1, 1)
        grid_layout.addWidget(self.label_telefone, 2, 0)
        grid_layout.addWidget(self.entrada_telefone, 2, 1)
        grid_layout.addWidget(self.label_funcionario, 3, 0)
        grid_layout.addWidget(self.selecao_funcionario, 3, 1)
        grid_layout.addWidget(self.label_operacao, 4, 0)
        grid_layout.addWidget(self.entrada_operacao, 4, 1)
        grid_layout.addWidget(self.botao_agendar, 6, 0, 1, 2)
        grid_layout.addWidget(self.tabela_horarios, 0, 2, 7, 1)
        self.tabela_horarios.setMouseTracking(True)
        self.tabela_horarios.setToolTipDuration(1000)
        self.tabela_horarios.entered.connect(self.mostrar_tooltip)
        self.preencher_tabela_horarios()
        self.resize(800, 600)
        self.menu_bar = self.menuBar()
        view_menu = self.menu_bar.addMenu("View")
        toggle_theme_action = QAction("Tema Escuro", self)
        toggle_theme_action.setCheckable(True)
        toggle_theme_action.triggered.connect(self.toggle_dark_theme)
        view_menu.addAction(toggle_theme_action)
        self.showFullScreen()
        self.showMaximized()
        self.tabela_horarios.header().setStretchLastSection(True)  # Estende a última coluna para preencher espaço vazio
        for column in range(self.model.columnCount()):
            self.tabela_horarios.resizeColumnToContents(column)  # Ajusta as colunas ao conteúdo

        # Adiciona o QComboBox para a seleção do horário
        self.label_horario = QLabel("Horário:")
        self.horario_combo_box = QComboBox()
        hora_inicio = QTime(8, 0)
        hora_final = QTime(19, 30)
        current_time = hora_inicio
        while current_time <= hora_final:
            self.horario_combo_box.addItem(current_time.toString("HH:mm"))
            current_time = current_time.addSecs(1800)  # Incrementa 30 minutos
        grid_layout.addWidget(self.label_horario, 5, 0)
        grid_layout.addWidget(self.horario_combo_box, 5, 1)  # Adiciona o QComboBox ao layout

        # Aplica um estilo para aumentar o espaçamento entre as colunas
        self.tabela_horarios.setStyleSheet("""
            QTreeView::item {
                border: 1px solid transparent;  # Adiciona uma borda transparente
                padding: 5px 15px;  # Ajusta o preenchimento: 5px vertical e 15px horizontal
            }
        """)        
        self.tabela_horarios.header().setStretchLastSection(True)  # Estende a última coluna para preencher espaço vazio
        for column in range(self.model.columnCount()):
            self.tabela_horarios.resizeColumnToContents(column)  # Ajusta as colunas ao conteúdo

        # Aplica um estilo para aumentar o espaçamento entre as colunas
        self.tabela_horarios.setStyleSheet("""
            QTreeView::item {
                border: 1px solid transparent;  # Adiciona uma borda transparente
                padding: 5px 15px;  # Ajusta o preenchimento: 5px vertical e 15px horizontal
            }
        """)

    def setup_second_tab(self):
        # Layout for the second tab
        grid_layout = QGridLayout(self.tab2)
        self.tabela_clientes = QTableWidget()
        self.tabela_clientes.setColumnCount(5)  # Set to the desired number of columns
        self.tabela_clientes.setHorizontalHeaderLabels(['Nome do Cliente', 'Telefone', 'Horário', 'Data', 'Ações'])
        grid_layout.addWidget(self.tabela_clientes, 0, 0, 1, 1)
        header = self.tabela_clientes.horizontalHeader()

        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)  # Nome do Cliente
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)  # Telefone
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)  # Horário
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)  # Data
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)  # Ações

        # Allow the text to be broken
        for row in range(self.tabela_clientes.rowCount()):
            for col in range(self.tabela_clientes.columnCount()):
                item = self.tabela_clientes.item(row, col)
                if item is not None:
                    item.setTextAlignment(Qt.AlignCenter)

        # Set the table style
        self.tabela_clientes.setStyleSheet("""
            QTableWidget {
                gridline-color: #000000;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)

    def atualizar_tabela_clientes(self):
        print(self.agendamentos)  
        try:
            self.tabela_clientes.setRowCount(0)
            for data, agendamentos in self.agendamentos.items():
                for (horario, funcionario), (nome, telefone) in agendamentos.items():
                    row_position = self.tabela_clientes.rowCount()
                    self.tabela_clientes.insertRow(row_position)
                    self.tabela_clientes.setItem(row_position, 0, QTableWidgetItem(str(nome)))
                    self.tabela_clientes.setItem(row_position, 1, QTableWidgetItem(str(telefone)))
                    self.tabela_clientes.setItem(row_position, 2, QTableWidgetItem(str(horario)))
        except Exception as e:
            print(f"Ocorreu um erro ao atualizar a tabela: {e}")


    def mostrar_tooltip(self, index):
        if index.data():
            data_selecionada = self.calendario.selectedDate().toString("yyyy-MM-dd")
            horario = self.model.item(index.row(), 0).text()
            funcionario = self.model.horizontalHeaderItem(index.column()).text()
            chave_agendamento = (horario, funcionario)
            nome, telefone, operacao = self.agendamentos.get(data_selecionada, {}).get(chave_agendamento, ('', '', ''))
            if index.column() == 0:
                QToolTip.showText(QCursor.pos(), "Hora", self.tabela_horarios)
            else:
                QToolTip.showText(QCursor.pos(), f"Nome: {nome}\nTelefone: {telefone}\nServiço: {operacao}", self.tabela_horarios)
    def preencher_tabela_horarios(self):
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['Hora', 'Funcionario1', 'Funcionario2', 'Funcionario3', 'Funcionario4', 'Funcionario5'])
        hora_inicio = QTime(8, 0)
        hora_final = QTime(19, 30)
        current_time = hora_inicio
        while current_time <= hora_final:
            row = [
                QStandardItem(current_time.toString("HH:mm"))
            ] + [QStandardItem('') for _ in range(5)]
            self.model.appendRow(row)
            current_time = current_time.addSecs(1800)  # Incrementa 30 minutos
        self.atualizar_tabela_com_base_na_data()
    def atualizar_tabela_com_base_na_data(self):
        data_selecionada = self.calendario.selectedDate().toString("yyyy-MM-dd")
        agendamentos_do_dia = self.agendamentos.get(data_selecionada, {})
        for row in range(self.model.rowCount()):
            horario = self.model.item(row, 0).text()
            for col in range(1, 6):
                item = self.model.item(row, col)
                funcionario = self.model.horizontalHeaderItem(col).text()
                chave_agendamento = (horario, funcionario)
                if chave_agendamento in agendamentos_do_dia:
                    nome, telefone = agendamentos_do_dia[chave_agendamento]
                    item.setText(f"{nome}\n{telefone}")
                else:
                    item.setText('')
    def operacao_selecionada(self, index):
        is_outros = self.entrada_operacao.itemText(index) == "Outros"
        self.entrada_operacao.setEditable(is_outros)
        if is_outros and self.dark_theme_enabled:
            self.entrada_operacao.setStyleSheet("QLineEdit { background-color: #333; color: #FFF; }")
        else:
            self.entrada_operacao.setStyleSheet("")

    def preparar_agendamento(self):
        nome_cliente = self.entrada_nome.text()
        telefone_cliente = self.entrada_telefone.text()
        funcionario_selecionado = self.selecao_funcionario.currentText()
        data_selecionada = self.calendario.selectedDate().toString("yyyy-MM-dd")
        operacao = self.entrada_operacao.currentText()

        horario = self.horario_combo_box.currentText()  # Usa o valor selecionado no QComboBox

        if not nome_cliente or not telefone_cliente or not horario:
            QMessageBox.warning(self, "Aviso", "Por favor, preencha todos os campos.")
            return

        chave_agendamento = (horario, funcionario_selecionado)
        agendamentos_do_dia = self.agendamentos.setdefault(data_selecionada, {})

        if chave_agendamento in agendamentos_do_dia:
            QMessageBox.critical(self, "Erro", "Este horário já está agendado para o funcionário selecionado.")
            return

        agendamentos_do_dia[chave_agendamento] = (nome_cliente, telefone_cliente, operacao)
        QMessageBox.information(self, "Agendado", "Cliente agendado com sucesso!")
        self.limpar_campos()
        self.atualizar_tabela_com_base_na_data()
    def limpar_campos(self):
        self.entrada_nome.clear()
        self.entrada_telefone.clear()

    def toggle_dark_theme(self, checked):
        if checked:
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

    def verificar_horario_na_tabela(self, horario):
        """Verifica se o horário informado está disponível na tabela de horários."""
        for row in range(self.model.rowCount()):
            if self.model.item(row, 0).text() == horario:
                return True
        return False

    def atualizar_tabela_com_base_na_data(self):
        data_selecionada = self.calendario.selectedDate().toString("yyyy-MM-dd")
        agendamentos_do_dia = self.agendamentos.get(data_selecionada, {})
        for row in range(self.model.rowCount()):
            horario = self.model.item(row, 0).text()
            for col in range(1, 6):
                item = self.model.item(row, col)
                funcionario = self.model.horizontalHeaderItem(col).text()
                chave_agendamento = (horario, funcionario)
                if chave_agendamento in agendamentos_do_dia:
                    nome, telefone, operacao = agendamentos_do_dia[chave_agendamento]
                    item.setText(nome)
                    item.setToolTip(f"Telefone: {telefone}\nServiço: {operacao}")
                else:
                    item.setText('')
                    item.setToolTip('')

    def toggle_dark_theme(self, checked):
        self.dark_theme_enabled = checked
        """Toggle the dark theme."""
        if checked:
            dark_style = (
                """
                QWidget {
                    background-color: #333;
                    color: #FFF;
                }
                QPushButton#agendarButton {
                    border: 1px solid #FFF;
                }
                QHeaderView::section {
                    background-color: #555;
                    border: 1px solid #444;
                }
                QTableView {
                    color: #FFF;
                }
                QTreeView, QCalendarWidget {
                    alternate-background-color: #444;
                    background: #333;
                    gridline-color: #444;
                    selection-background-color: #888;
                    selection-color: #EEE;
                }
                QCalendarWidget QAbstractItemView {
                    selection-background-color: #555;
                }
                QCalendarWidget QWidget {
                    alternate-background-color: #222;
                    background-color: #333;
                    color: #FFF;
                }
                QTabWidget::pane { /* The tab widget frame */
                    border-top: 2px solid #C2C7CB;
                }
                QTabWidget::tab-bar {
                    left: 5px; /* move to the right by 5px */
                }
                QTabBar::tab {
                    background: #333;
                    color: #FFF;
                    border: 2px solid #C4C4C3;
                    border-bottom-color: #333; /* same as the tab color */
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    min-width: 8ex;
                    padding: 2px;
                }
                QTabBar::tab:selected, QTabBar::tab:hover {
                    background: #444;
                }
                QTabBar::tab:selected {
                    border-color: #9B9B9B;
                    border-bottom-color: #444; /* same as pane color */
                }
                """
            )
            self.setStyleSheet(self.base_style + dark_style)
        else:
            self.setStyleSheet(self.base_style)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = SalaoApp()
    janela.show()
    sys.exit(app.exec_())
