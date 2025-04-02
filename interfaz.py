import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QGridLayout, QPushButton, QLineEdit, QFrame, QSplitter, QGraphicsDropShadowEffect, QLabel
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt

class NewtonRaphsonApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Calculadora Newton-Raphson")
        self.showMaximized()  # Ocupa toda la pantalla

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # QSplitter para dividir la pantalla en dos paneles ajustables
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ---------------------------
        # Panel IZQUIERDO (Calculadora)
        # ---------------------------
        left_frame = QFrame()
        left_frame.setStyleSheet("background-color: white;")
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(40, 40, 40, 40)

        # Agregar stretch superior para centrar verticalmente el contenido
        left_layout.addStretch(1)

        # Label superior
        title_label = QLabel("Calculadora Newton-Raphson")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: black; padding-bottom: 20px;")
        left_layout.addWidget(title_label)

        # Contenedor para la calculadora, con un mínimo ancho configurable
        calc_container = QFrame()
        calc_container.setStyleSheet("background-color: white;")
        calc_container.setMinimumWidth(550)
        calc_layout = QVBoxLayout(calc_container)
        calc_layout.setSpacing(20)

        # Función para aplicar sombra a los widgets (drop shadow)
        def aplicar_sombra(widget):
            sombra = QGraphicsDropShadowEffect()
            sombra.setBlurRadius(10)
            sombra.setOffset(3, 3)
            sombra.setColor(QColor(0, 0, 0, 100))
            widget.setGraphicsEffect(sombra)

        # Campo de entrada: f(x)
        self.function_input = QLineEdit()
        self.function_input.setPlaceholderText("Ingrese f(x)")
        self.function_input.setStyleSheet(
            "QLineEdit {"
            "  border-radius: 10px;"
            "  padding: 10px;"
            "  font-size: 16px;"
            "  background-color: #f0f0f0;"
            "  color: black;"
            "}"
        )
        aplicar_sombra(self.function_input)
        calc_layout.addWidget(self.function_input)

        # Campo de entrada: x0
        self.x0_input = QLineEdit()
        self.x0_input.setPlaceholderText("Ingrese x0")
        self.x0_input.setStyleSheet(
            "QLineEdit {"
            "  border-radius: 10px;"
            "  padding: 10px;"
            "  font-size: 16px;"
            "  background-color: #f0f0f0;"
            "  color: black;"
            "}"
        )
        aplicar_sombra(self.x0_input)
        calc_layout.addWidget(self.x0_input)

        # Campo de entrada: Tolerancia
        self.tolerance_input = QLineEdit()
        self.tolerance_input.setPlaceholderText("Ingrese tolerancia")
        self.tolerance_input.setStyleSheet(
            "QLineEdit {"
            "  border-radius: 10px;"
            "  padding: 10px;"
            "  font-size: 16px;"
            "  background-color: #f0f0f0;"
            "  color: black;"
            "}"
        )
        aplicar_sombra(self.tolerance_input)
        calc_layout.addWidget(self.tolerance_input)

        # Función para manejar la pulsación de botones
        def on_button_clicked(text):
            # Determinar el QLineEdit a modificar según el foco actual
            widget = self.focusWidget()
            if not isinstance(widget, QLineEdit):
                widget = self.function_input

            if text == "CE":
                widget.clear()
            elif text == "C":
                current_text = widget.text()
                widget.setText(current_text[:-1])
            else:
                # Inserta el texto en la posición actual del cursor
                cursor_pos = widget.cursorPosition()
                current_text = widget.text()
                new_text = current_text[:cursor_pos] + text + current_text[cursor_pos:]
                widget.setText(new_text)
                widget.setCursorPosition(cursor_pos + len(text))

        # Cuadrícula de botones
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(15)
        grid_layout.setVerticalSpacing(15)

        buttons = [
            ["CE", "C", "(", ")", "e"],
            ["7",  "8",  "9",  "+", "^"],
            ["4",  "5",  "6",  "/", "√"],
            ["1",  "2",  "3",  "*", "sin"],
            ["0",  ".",  "x",  "-", "cos"],
        ]

        for row, button_row in enumerate(buttons):
            for col, text in enumerate(button_row):
                button = QPushButton(text)
                button.setFont(QFont("Arial", 16))
                button.setStyleSheet(
                    "QPushButton {"
                    "  background-color: #4a2df9;"
                    "  color: white;"
                    "  border-radius: 10px;"
                    "  padding: 10px;"
                    "  font-weight: bold;"
                    "}"
                    "QPushButton:hover {"
                    "  background-color: #5939ec;"
                    "}"
                )
                # Conectar el botón a la función on_button_clicked
                button.clicked.connect(lambda checked, t=text: on_button_clicked(t))
                grid_layout.addWidget(button, row, col)
        calc_layout.addLayout(grid_layout)

        # Botón de Calcular
        self.calculate_button = QPushButton("Calcular")
        self.calculate_button.setFont(QFont("Arial", 16))
        self.calculate_button.setStyleSheet(
            "QPushButton {"
            "  background-color: #5939ec;"
            "  color: white;"
            "  border-radius: 10px;"
            "  padding: 10px;"
            "  font-weight: bold;"
            "}"
            "QPushButton:hover {"
            "  background-color: #5939ec;"
            "}"
        )
        aplicar_sombra(self.calculate_button)
        calc_layout.addWidget(self.calculate_button)

        # Agrega el contenedor de la calculadora al panel izquierdo, centrado horizontalmente
        left_layout.addWidget(calc_container, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Agregar stretch inferior para centrar verticalmente el contenido
        left_layout.addStretch(1)

        # ---------------------------
        # Panel DERECHO (para gráfica y tabla, por ahora vacío)
        # ---------------------------
        right_frame = QFrame()
        right_frame.setStyleSheet("background-color: white;")

        # Agregar ambos paneles al splitter
        splitter.addWidget(left_frame)
        splitter.addWidget(right_frame)
        splitter.setSizes([700, 700])  # Valores iniciales, ajustables por el usuario

        # Layout principal del widget central
        main_layout = QHBoxLayout(central_widget)
        main_layout.addWidget(splitter)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NewtonRaphsonApp()
    window.show()
    sys.exit(app.exec())
