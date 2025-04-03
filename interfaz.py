import sys
import math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QGridLayout, QPushButton, QLineEdit, QFrame, QSplitter, QGraphicsDropShadowEffect, QLabel,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView
)
from PyQt6.QtGui import QFont, QColor, QDoubleValidator
from PyQt6.QtCore import Qt, QEvent

# Importamos sympy para manejar funciones simbólicas
from sympy import symbols, sympify, diff, lambdify, sin, cos, exp, sqrt

class NewtonRaphsonApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_input = None  # Para llevar seguimiento del input activo
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
        self.function_input.installEventFilter(self)
        aplicar_sombra(self.function_input)
        calc_layout.addWidget(self.function_input)

        # Campo de entrada: x0 (sólo números)
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

        # Campo de entrada: Tolerancia (sólo números)
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

        # Función para manejar la pulsación de botones
        def on_button_clicked(text):
            widget = self.current_input if self.current_input is not None else self.function_input

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

        # Conectar el botón de calcular a la función que ejecuta Newton-Raphson
        self.calculate_button.clicked.connect(self.calcular)

        # Agrega el contenedor de la calculadora al panel izquierdo, centrado horizontalmente
        left_layout.addWidget(calc_container, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Agregar stretch inferior para centrar verticalmente el contenido
        left_layout.addStretch(1)

        # ---------------------------
        # Panel DERECHO (para tabla de resultados)
        # ---------------------------
        self.right_frame = QFrame()
        self.right_frame.setStyleSheet("background-color: white;")
        self.right_layout = QVBoxLayout(self.right_frame)
        self.right_layout.setContentsMargins(20, 20, 20, 20)

        # Título para el panel derecho
        results_title = QLabel("Resultados del Método Newton-Raphson")
        results_title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        results_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        results_title.setStyleSheet("color: black; margin-bottom: 20px;")
        self.right_layout.addWidget(results_title)

        # Crear tabla vacía desde el inicio
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["Iteración", "xi", "f(xi)", "f'(xi)", "Error"])
        
        # Configurar la tabla para que se ajuste al contenido
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
        
        # Agregar la tabla al layout del panel derecho
        self.right_layout.addWidget(self.tabla)

        # Agregar ambos paneles al splitter
        splitter.addWidget(left_frame)
        splitter.addWidget(self.right_frame)
        splitter.setSizes([700, 700])  # Valores iniciales, ajustables por el usuario

        # Layout principal del widget central
        main_layout = QHBoxLayout(central_widget)
        main_layout.addWidget(splitter)

    # Event filter para actualizar self.current_input al recibir FocusIn
    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.FocusIn:
            if isinstance(source, QLineEdit):
                self.current_input = source
        return super().eventFilter(source, event)
    
    def calcular(self):
        # Obtén la función, x0 y tolerancia de los inputs
        func_str = self.function_input.text().strip()
        x0_str = self.x0_input.text().strip()
        tol_str = self.tolerance_input.text().strip()

        # Validar que los campos no estén vacíos
        if not func_str or not x0_str or not tol_str:
            QMessageBox.warning(self, "Error", "Por favor, complete todos los campos.")
            return

        try:
            x0 = float(x0_str)
            tol = float(tol_str)  # Tolerancia como porcentaje
        except ValueError:
            QMessageBox.warning(self, "Error", "x0 y tolerancia deben ser números.")
            return

        # Define la variable simbólica y procesa la función con sympy
        x = symbols('x')

        # Reemplazar operadores y funciones para que Sympy los reconozca
        func_str = func_str.replace('e', 'exp(1)')
        func_str = func_str.replace('^', '**')
        func_str = func_str.replace('√', 'sqrt')
       
        try:
            f_sym = sympify(func_str)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al interpretar f(x): {e}")
            return

        # Calcula la derivada de f(x)
        try:
            fprime_sym = diff(f_sym, x)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al calcular la derivada: {e}")
            return

        # Genera funciones numéricas usando lambdify
        try:
            f_num = lambdify(x, f_sym, modules=['math'])
            fprime_num = lambdify(x, fprime_sym, modules=['math'])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al convertir la función: {e}")
            return

        # Realiza las iteraciones del método de Newton-Raphson
        max_iter = 50  # Límite de 50 iteraciones
        iteraciones = []
        xi = x0
        error_rel_porcentaje = float('inf')  # Error relativo inicial en porcentaje
        i = 0  # Empezamos desde 0 para incluir el valor inicial

        # Agregar el valor inicial (antes de la primera iteración)
        try:
            fxi = f_num(xi)
            fprime_xi = fprime_num(xi)
            iteraciones.append((i, xi, fxi, fprime_xi, float('inf')))  # Error inicial es infinito
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error en la evaluación inicial: {e}")
            return

        i = 1  # Ahora empezamos las iteraciones desde 1
        
        # Bucle principal del método de Newton-Raphson
        while error_rel_porcentaje > tol and i <= max_iter:
            try:
                fxi = f_num(xi)
                fprime_xi = fprime_num(xi)
                
                # Evitar división por cero
                if abs(fprime_xi) < 1e-10:
                    QMessageBox.warning(self, "Error", "La derivada es casi cero; no se puede continuar.")
                    return
                
                # Calcular el siguiente valor de x
                xi_new = xi - fxi / fprime_xi
                
                # Calcular el error relativo porcentual: |((x_actual - x_anterior) / x_actual)| × 100
                if abs(xi_new) < 1e-10:  # Evitar división por cero
                    error_rel_porcentaje = abs(xi_new - xi) * 100  # Usar error absoluto si xi_new es casi cero
                else:
                    error_rel_porcentaje = abs((xi_new - xi) / xi_new) * 100  # Error relativo en porcentaje
                
                # Calcular f(xi_new) y f'(xi_new) para la tabla
                fxi_new = f_num(xi_new)
                fprime_xi_new = fprime_num(xi_new)
                
                # Guardar los resultados de esta iteración
                iteraciones.append((i, xi_new, fxi_new, fprime_xi_new, error_rel_porcentaje))
                
                print(f"Iteración {i}: xi={xi_new}, f(xi)={fxi_new}, f'(xi)={fprime_xi_new}, error={error_rel_porcentaje}%")
                
                # Verificar si hemos alcanzado la tolerancia
                if error_rel_porcentaje <= tol:
                    print(f"Convergencia alcanzada: Error {error_rel_porcentaje}% <= Tolerancia {tol}%")
                    break
                
                # Actualizar xi para la siguiente iteración
                xi = xi_new
                i += 1
                
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error en la iteración {i}: {e}")
                return

        # Actualiza la tabla con los resultados
        self.mostrar_resultados(iteraciones)

    def mostrar_resultados(self, iteraciones):
        # Limpiar la tabla existente
        self.tabla.clearContents()
        self.tabla.setRowCount(len(iteraciones))
        
        print(f"Mostrando {len(iteraciones)} filas en la tabla")
        
        # Rellena la tabla con los datos
        for row, data in enumerate(iteraciones):
            print(f"Procesando fila {row}: {data}")
            
            for col, value in enumerate(data):
                # Formatear los números para que sean legibles
                if col == 0:  # Iteración (entero)
                    text = str(int(value))
                elif col == 4 and row == 0:  # Error en la primera fila (infinito)
                    text = "---"
                else:  # Valores numéricos (float)
                    text = f"{value:.4f}"
                
                # Crear el item y establecer el texto
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # Establecer color de texto explícitamente
                item.setForeground(QColor(0, 0, 0))  # Negro
                
                # Insertar el item en la tabla
                self.tabla.setItem(row, col, item)
                
                print(f"Item insertado en ({row}, {col}): {text}")
        
        # Forzar actualización de la tabla
        self.tabla.update()
        QApplication.processEvents()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NewtonRaphsonApp()
    window.show()
    sys.exit(app.exec())