#pip install matplotlib sympy PyQt6
import sys  
import math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QGridLayout, QPushButton, QLineEdit, QFrame, QSplitter, QGraphicsDropShadowEffect, QLabel,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QScrollArea, QStackedWidget
)
from PyQt6.QtGui import QFont, QColor, QDoubleValidator
from PyQt6.QtCore import Qt, QEvent

# Se importan herramientas de Sympy para trabajar con funciones simbólicas
from sympy import symbols, diff, lambdify, sin, cos, exp, sqrt, E, tan, log
# Se importa el parser avanzado de Sympy para interpretar las funciones de entrada
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
# Se importan herramientas de matplotlib para realizar la gráfica
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class CalculatorPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window  
        self.current_input = None  
        self.initUI()

    def initUI(self):
        self.setStyleSheet("background-color: white; color: black;")

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background-color: gray; width: 2px; }")

        # ================
        # PANEL IZQUIERDO
        # ================
        left_frame = QFrame()
        left_frame.setStyleSheet("background-color: white;")
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(40, 40, 40, 40)
        left_layout.addStretch(1)

        title_label = QLabel("Calculadora Newton-Raphson")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: black; padding-bottom: 20px;")
        left_layout.addWidget(title_label)

        calc_container = QFrame()
        calc_container.setStyleSheet("background-color: white;")
        calc_container.setMinimumWidth(550)
        calc_layout = QVBoxLayout(calc_container)
        calc_layout.setSpacing(20)

        def aplicar_sombra(widget):
            sombra = QGraphicsDropShadowEffect()
            sombra.setBlurRadius(10)
            sombra.setOffset(3, 3)
            sombra.setColor(QColor(0, 0, 0, 100))
            widget.setGraphicsEffect(sombra)

        # Entradas
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
        self.function_input.installEventFilter(self)
        aplicar_sombra(self.function_input)
        calc_layout.addWidget(self.function_input)

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
        self.x0_input.setValidator(QDoubleValidator(-1e9, 1e9, 6))
        self.x0_input.installEventFilter(self)
        aplicar_sombra(self.x0_input)
        calc_layout.addWidget(self.x0_input)

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
        self.tolerance_input.setValidator(QDoubleValidator(-1e9, 1e9, 6))
        self.tolerance_input.installEventFilter(self)
        aplicar_sombra(self.tolerance_input)
        calc_layout.addWidget(self.tolerance_input)

        # Teclado Virtual
        def on_button_clicked(text):
            widget = self.current_input if self.current_input else self.function_input
            if text == "CE":
                widget.clear()
            elif text == "C":
                current_text = widget.text()
                widget.setText(current_text[:-1])
            else:
                cursor_pos = widget.cursorPosition()
                current_text = widget.text()
                new_text = current_text[:cursor_pos] + text + current_text[cursor_pos:]
                widget.setText(new_text)
                widget.setCursorPosition(cursor_pos + len(text))

        # Se define una lista de listas para ubicar cada botón en el grid
        buttons = [
            ["CE", "C",  "(",  ")",    "e"  ],
            ["7",  "8",  "9",  "+",    "^"  ],
            ["4",  "5",  "6",  "/",    "√"  ],
            ["1",  "2",  "3",  "*",    "sin"],
            ["0",  ",",  "x",  "-",    "cos"],
            ["",   "",   "",   "tan",  "ln" ]
        ]

        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(15)
        grid_layout.setVerticalSpacing(15)

        for row, button_row in enumerate(buttons):
            for col, text in enumerate(button_row):
                if text:
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
                    button.clicked.connect(lambda _, t=text: on_button_clicked(t))
                    grid_layout.addWidget(button, row, col)
                else:
                    # Espacio vacío (se podría dejar un QWidget o un QLabel en blanco)
                    space_widget = QWidget()
                    grid_layout.addWidget(space_widget, row, col)

        calc_layout.addLayout(grid_layout)

        # Botón para Calcular
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
        self.calculate_button.clicked.connect(self.calcular)

        # Botón Manual
        self.manual_button = QPushButton("Manual")
        self.manual_button.setFont(QFont("Arial", 16))
        self.manual_button.setStyleSheet(
            "QPushButton {"
            "  background-color: #28a745;"
            "  color: white;"
            "  border-radius: 10px;"
            "  padding: 10px;"
            "  font-weight: bold;"
            "}"
            "QPushButton:hover {"
            "  background-color: #218838;"
            "}"
        )
        aplicar_sombra(self.manual_button)
        calc_layout.addWidget(self.manual_button)
        self.manual_button.clicked.connect(self.mostrar_manual)

        # ================
        # BOTÓN "Borrar Todo" EN EL GRID (debajo de 0 y x)
        # ================
        self.clear_all_button = QPushButton("Borrar Todo")
        self.clear_all_button.setFont(QFont("Arial", 16))
        self.clear_all_button.setStyleSheet(
            "QPushButton {"
            "  background-color: #dc3545;"  # Rojo
            "  color: white;"
            "  border-radius: 10px;"
            "  padding: 10px;"
            "  font-weight: bold;"
            "}"
            "QPushButton:hover {"
            "  background-color: #c82333;"
            "}"
        )
        aplicar_sombra(self.clear_all_button)
        # Se ubica en la fila 5, columna 0, abarcando 3 columnas para que ocupe el espacio vacío
        grid_layout.addWidget(self.clear_all_button, 5, 0, 1, 3)
        self.clear_all_button.clicked.connect(self.limpiar_campos)

        left_layout.addWidget(calc_container, alignment=Qt.AlignmentFlag.AlignHCenter)
        left_layout.addStretch(1)

        # ================
        # PANEL DERECHO
        # ================
        right_frame = QFrame()
        right_frame.setStyleSheet("background-color: white;")
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(20, 20, 20, 20)

        table_title = QLabel("Tabla de Iteraciones Newton-Raphson")
        table_title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        table_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(table_title)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["Iteración", "xi", "f(xi)", "f'(xi)", "Error"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setStyleSheet("""
            QTableWidget {
                border: 1px solid #d3d3d3;
                gridline-color: #e0e0e0;
                background-color: white;
                alternate-background-color: #f9f9f9;
                color: black;
            }
            QHeaderView::section {
                background-color: #4a2df9;
                color: white;
                padding: 6px;
                font-weight: bold;
                border: none;
            }
            QTableWidget::item {
                color: black;
                font-size: 14px;
                padding: 4px;
            }
        """)
        right_layout.addWidget(self.tabla, stretch=1)

        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(300)
        right_layout.addWidget(self.canvas, stretch=1)

        splitter.addWidget(left_frame)
        splitter.addWidget(right_frame)
        splitter.setSizes([700, 700])

        main_layout = QHBoxLayout(self)
        main_layout.addWidget(splitter)

    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.FocusIn:
            if isinstance(source, QLineEdit):
                self.current_input = source
        return super().eventFilter(source, event)

    def limpiar_campos(self):
        # Limpia todos los campos de entrada
        self.function_input.clear()
        self.x0_input.clear()
        self.tolerance_input.clear()

    def calcular(self):
        func_str = self.function_input.text().strip()
        x0_str = self.x0_input.text().strip()
        tol_str = self.tolerance_input.text().strip()

        x0_str = x0_str.replace(',', '.')
        tol_str = tol_str.replace(',', '.')

        if not func_str or not x0_str or not tol_str:
            QMessageBox.warning(self, "Error", "Por favor, complete todos los campos.")
            return

        try:
            x0 = float(x0_str)
            tol = float(tol_str)
        except ValueError:
            QMessageBox.warning(self, "Error", "x0 y tolerancia deben ser números.")
            return

        x = symbols('x')
        transformations = (standard_transformations + (implicit_multiplication_application, convert_xor))

        # Sustitución del símbolo √ por sqrt()
        func_str = func_str.replace('√(', 'sqrt(')
        func_str = func_str.replace('√x', 'sqrt(x)')

        local_dict = {
            'x': x,
            'e': E,
            'E': E,
            'sin': sin,
            'cos': cos,
            'tan': tan,
            'ln': log,
            'exp': exp,
            'sqrt': sqrt
        }

        try:
            f_sym = parse_expr(func_str, transformations=transformations, local_dict=local_dict)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al interpretar f(x): {e}")
            return

        try:
            fprime_sym = diff(f_sym, x)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al calcular la derivada: {e}")
            return

        try:
            f_num = lambdify(x, f_sym, modules=['math'])
            fprime_num = lambdify(x, fprime_sym, modules=['math'])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al convertir la función: {e}")
            return

        max_iter = 50
        iteraciones = []
        xi = x0
        error_rel_porcentaje = float('inf')
        i = 0

        try:
            fxi = f_num(xi)
            fprime_xi = fprime_num(xi)
            iteraciones.append((i, xi, fxi, fprime_xi, float('inf')))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error en la evaluación inicial: {e}")
            return

        i = 1
        while error_rel_porcentaje > tol and i <= max_iter:
            try:
                fxi = f_num(xi)
                fprime_xi = fprime_num(xi)
                if abs(fprime_xi) < 1e-10:
                    QMessageBox.warning(self, "Error", "La derivada es casi cero; no se puede continuar.")
                    return

                xi_new = xi - fxi / fprime_xi
                if abs(xi_new) < 1e-10:
                    error_rel_porcentaje = abs(xi_new - xi) * 100
                else:
                    error_rel_porcentaje = abs((xi_new - xi) / xi_new) * 100

                fxi_new = f_num(xi_new)
                fprime_xi_new = fprime_num(xi_new)
                iteraciones.append((i, xi_new, fxi_new, fprime_xi_new, error_rel_porcentaje))

                if error_rel_porcentaje <= tol:
                    break

                xi = xi_new
                i += 1
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error en la iteración {i}: {e}")
                return

        self.mostrar_resultados(iteraciones)
        self.graficar_resultados(iteraciones)

    def mostrar_resultados(self, iteraciones):
        self.tabla.clearContents()
        self.tabla.setRowCount(len(iteraciones))
        for row, data in enumerate(iteraciones):
            for col, value in enumerate(data):
                if col == 0:
                    text = str(int(value))
                elif col == 4 and row == 0:
                    text = "---"
                else:
                    text = f"{value:.4f}"
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setForeground(QColor(0, 0, 0))
                self.tabla.setItem(row, col, item)
        self.tabla.update()
        QApplication.processEvents()

    def graficar_resultados(self, iteraciones):
        xi_vals = [it[1] for it in iteraciones]
        fxi_vals = [it[2] for it in iteraciones]
        fprime_vals = [it[3] for it in iteraciones]

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(xi_vals, fxi_vals, marker='o', linestyle='-', label='$f(x_i)$')
        ax.plot(xi_vals, fprime_vals, marker='s', linestyle='--', label="$f'(x_i)$")
        ax.set_xlabel("$x_i$")
        ax.set_ylabel("Valor")
        ax.set_title("Gráfica de $f(x_i)$ y $f'(x_i)$ vs $x_i$")
        ax.legend()
        ax.grid(True)
        self.canvas.draw()

    def mostrar_manual(self):
        self.main_window.show_manual_page()


class ManualPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        self.setStyleSheet("background-color: white; color: black;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)

        title_label = QLabel("Manual de Uso de la Calculadora Newton-Raphson")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: white;")
        layout.addWidget(scroll_area)

        content = QWidget()
        content.setStyleSheet("background-color: white;")
        scroll_area.setWidget(content)
        content_layout = QVBoxLayout(content)

        manual_text = (
            "<h3>Descripción de Campos y Funcionalidades</h3>"
            "<p><b>Campo f(x):</b> Ingrese la función matemática de la cual se desea encontrar la raíz. "
            "Se aceptan expresiones simbólicas. Ejemplo: <i>2*sin(√x) - x</i>.</p>"
            "<p><b>Campo x0:</b> Valor inicial para iniciar el método. Es vital para la convergencia.</p>"
            "<p><b>Campo Tolerancia:</b> Porcentaje de error permitido para considerar la convergencia.</p>"
            "<h3>Uso de los Botones</h3>"
            "<p><b>Teclado Virtual:</b> Facilita la entrada de la función. Incluye botones para borrar (CE, C), "
            "operaciones básicas, paréntesis, potencia (^), raíz (√), trigonometría (sin, cos, tan) y logaritmo (ln).</p>"
            "<p><b>Botón Calcular:</b> Ejecuta el método Newton-Raphson y muestra los resultados en una tabla y en una gráfica.</p>"
            "<h3>Resultados y Gráficas</h3>"
            "<p><b>Tabla de Resultados:</b> Muestra cada iteración con xi, f(xi), f'(xi) y el error relativo.</p>"
            "<p><b>Gráfica:</b> Visualiza la evolución de f(xi) y f'(x_i) a lo largo de las iteraciones.</p>"
            "<h3>Navegación</h3>"
            "<p>Esta página cubre toda la pantalla. Para volver a la calculadora, presione el botón 'Regresar'.</p>"
        )
        manual_label = QLabel(manual_text)
        manual_label.setWordWrap(True)
        manual_label.setTextFormat(Qt.TextFormat.RichText)
        manual_label.setFont(QFont("Arial", 12))
        content_layout.addWidget(manual_label)

        self.back_button = QPushButton("Regresar")
        self.back_button.setFont(QFont("Arial", 16))
        self.back_button.setStyleSheet(
            "QPushButton {"
            "  background-color: #dc3545;"
            "  color: white;"
            "  border-radius: 10px;"
            "  padding: 10px;"
            "  font-weight: bold;"
            "}"
            "QPushButton:hover {"
            "  background-color: #c82333;"
            "}"
        )
        self.back_button.clicked.connect(self.regresar)
        content_layout.addWidget(self.back_button)

    def regresar(self):
        self.main_window.show_calculator_page()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora Newton-Raphson")
        self.stacked_widget = QStackedWidget()

        self.calculator_page = CalculatorPage(self)
        self.manual_page = ManualPage(self)
        self.stacked_widget.addWidget(self.calculator_page)
        self.stacked_widget.addWidget(self.manual_page)
        self.setCentralWidget(self.stacked_widget)

        self.setStyleSheet("background-color: white; color: black;")
        self.showMaximized()

    def show_manual_page(self):
        self.stacked_widget.setCurrentWidget(self.manual_page)

    def show_calculator_page(self):
        self.stacked_widget.setCurrentWidget(self.calculator_page)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
