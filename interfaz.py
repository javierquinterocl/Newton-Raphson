# pip install matplotlib sympy PyQt6
import sys  # Importa el módulo sys para interactuar con el sistema(Terminal)
import math  # Módulo para operaciones matemáticas básicas

# Importación de componentes de PyQt6 para construir la interfaz gráfica
from PyQt6.QtWidgets import (
    QApplication,     # Clase principal que administra la aplicación Qt
    QMainWindow,      # Clase para crear la ventana principal
    QWidget,          # Clase base para todos los widgets
    QHBoxLayout,      # Layout horizontal para distribuir widgets en línea
    QVBoxLayout,      # Layout vertical para distribuir widgets en columna
    QGridLayout,      # Layout en forma de cuadrícula (usado para el teclado virtual)
    QPushButton,      # Widget de botón interactivo
    QLineEdit,        # Campo de texto donde el usuario ingresa información
    QFrame,           # Contenedor que agrupa widgets
    QSplitter,        # Widget que divide el área en paneles redimensionables
    QGraphicsDropShadowEffect,  # Efecto visual para aplicar sombra a los widgets
    QLabel,           # Widget para mostrar texto o imágenes
    QTableWidget,     # Tabla para mostrar datos de forma estructurada
    QTableWidgetItem, # Elemento de la tabla (celda) para mostrar contenido
    QMessageBox,      # Widget emergente para mostrar mensajes de error o alerta
    QHeaderView,      # Configura el aspecto de las cabeceras en la tabla
    QScrollArea,      # Área de desplazamiento para contenido extenso (Usado en el manual)
    QStackedWidget    # Widget que apila múltiples páginas, permitiendo cambiar entre ellas
)
# Importación de herramientas gráficas (fuente, color)
from PyQt6.QtGui import QFont, QColor, QDoubleValidator
# Importación de utilidades de PyQt6 para eventos (por ejemplo, para manejar el enfoque de los QLineEdit)
from PyQt6.QtCore import Qt, QEvent

# Importación de herramientas de Sympy para trabajar con funciones simbólicas
from sympy import symbols, diff, lambdify, sin, cos, exp, sqrt, E, tan, log
# Se utiliza el parser avanzado de Sympy para interpretar cadenas y convertirlas en expresiones simbólicas
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
# Importación de Matplotlib para integrar gráficos en la interfaz (usando el backend para Qt)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# Clase CalculatorPage: Define la interfaz y funcionalidad

class CalculatorPage(QWidget):
    def __init__(self, main_window):
        """
        Inicializa la página de la calculadora y guarda la referencia a la ventana principal
        para permitir la navegación entre páginas.
        """
        super().__init__()
        self.main_window = main_window  # Guarda referencia a la ventana principal
        self.current_input = None       # Controla cuál QLineEdit tiene el foco actualmente
        self.initUI()                   # Inicializa la interfaz gráfica de la calculadora

    def initUI(self):
        """
        Configura la interfaz gráfica de la calculadora.
        Crea el panel izquierdo con los campos de entrada, el teclado virtual,
        y los botones; y el panel derecho con la tabla de iteraciones, el resultado final
        y la gráfica de los resultados.
        """
        # Establece el estilo general de la página 
        self.setStyleSheet("background-color: white; color: black;")

        # Crea un QSplitter para dividir la ventana en dos paneles (izquierdo y derecho)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background-color: gray; width: 2px; }")

       
        # PANEL IZQUIERDO: Entradas y Teclado
       
        left_frame = QFrame()
        left_frame.setStyleSheet("background-color: white;")
        left_layout = QVBoxLayout(left_frame)
        # Se definen márgenes alrededor del contenido
        left_layout.setContentsMargins(40, 40, 40, 40)
        left_layout.addStretch(1)  # Se añade espacio elástico para centrar el contenido verticalmente

        # Título del panel izquierdo
        title_label = QLabel("Calculadora Newton-Raphson")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: black; padding-bottom: 20px;")
        # Añadimos el widget al Layout
        left_layout.addWidget(title_label)

        # Contenedor para los campos de entrada y el teclado virtual
        calc_container = QFrame()
        calc_container.setStyleSheet("background-color: white;")
        calc_container.setMinimumWidth(550)
        calc_layout = QVBoxLayout(calc_container)
        calc_layout.setSpacing(20)  # Espacio entre widgets en el contenedor

        def aplicar_sombra(widget):
            """
            Aplica un efecto de sombra al widget
            """
            sombra = QGraphicsDropShadowEffect()
            sombra.setBlurRadius(10)  # Define el radio del desenfoque
            sombra.setOffset(3, 3)    # Define el desplazamiento en x e y
            sombra.setColor(QColor(0, 0, 0, 100))  # Establece el color y la transparencia de la sombra
            widget.setGraphicsEffect(sombra)

       
        # Campos de Entrada
        
        # Campo para ingresar la función f(x)
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
        # Se instala un filtro de eventos para detectar el momento en que el campo recibe foco
        self.function_input.installEventFilter(self)
        aplicar_sombra(self.function_input)
        calc_layout.addWidget(self.function_input)

        # Campo para ingresar el valor inicial x0
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
        # Se utiliza un validador para que solo se ingresen números
        self.x0_input.setValidator(QDoubleValidator(-1e9, 1e9, 6))
        self.x0_input.installEventFilter(self)
        aplicar_sombra(self.x0_input)
        calc_layout.addWidget(self.x0_input)

        # Campo para ingresar la tolerancia
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
         # Se utiliza un validador para que solo se ingresen números
        self.tolerance_input.setValidator(QDoubleValidator(-1e9, 1e9, 6))
        self.tolerance_input.installEventFilter(self)
        aplicar_sombra(self.tolerance_input)
        calc_layout.addWidget(self.tolerance_input)

       
        # Teclado Virtual
       
        def on_button_clicked(text):
            """
            Función que inserta el texto correspondiente en el campo actualmente activo
            cuando se presiona un botón del teclado virtual.
            """
            widget = self.current_input if self.current_input else self.function_input
            if text == "CE":
                widget.clear()  # Borra todo el contenido
            elif text == "C":
                # Borra el último carácter
                current_text = widget.text()
                widget.setText(current_text[:-1])
            else:
                # Inserta el texto del botón en la posición del cursor
                cursor_pos = widget.cursorPosition()
                current_text = widget.text()
                new_text = current_text[:cursor_pos] + text + current_text[cursor_pos:]
                widget.setText(new_text)
                widget.setCursorPosition(cursor_pos + len(text))

        # Lista de listas que define el teclado virtual (cada sublista es una fila)
        buttons = [
            ["CE", "C",  "(",  ")",    "e"  ],
            ["7",  "8",  "9",  "+",    "^"  ],
            ["4",  "5",  "6",  "/",    "√"  ],
            ["1",  "2",  "3",  "*",    "sin"],
            ["0",  ",",  "x",  "-",    "cos"],
            ["",   "",   "",   "tan",  "ln" ]
        ]

        # Se crea un GridLayout para colocar los botones en forma de cuadrícula
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(15)  # Espacio horizontal entre botones
        grid_layout.setVerticalSpacing(15)    # Espacio vertical entre botones

        # Se agrega cada botón al grid basado en su posición en la lista
        for row, button_row in enumerate(buttons):
            for col, text in enumerate(button_row):
                if text:
                    button = QPushButton(text)
                    button.setFont(QFont("Arial", 10))
                    button.setStyleSheet(
                        "QPushButton {"
                        "  background-color: #4a2df9;"  
                        "  color: white;"               
                        "  border-radius: 10px;"         
                        "  padding: 4px;"              
                        "  font-weight: bold;"          
                        "}"
                        "QPushButton:hover {"
                        "  background-color: #5939ec;"  
                        "}"
                    )
                    # Conecta el clic del botón con la función on_button_clicked
                    button.clicked.connect(lambda _, t=text: on_button_clicked(t))
                    grid_layout.addWidget(button, row, col)
                else:
                    # Si el espacio está vacío, se utiliza un widget vacío para ocupar el lugar
                    space_widget = QWidget()
                    grid_layout.addWidget(space_widget, row, col)

        # Se añade el teclado virtual (el grid layout) al layout del contenedor de la calculadora
        calc_layout.addLayout(grid_layout)

       
        # Botón "Calcular"
       
        # Botón que inicia el proceso del método Newton-Raphson
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
        # Conecta el botón "Calcular" al método calcular()
        self.calculate_button.clicked.connect(self.calcular)

       
        # Botón "Manual"
       
        # Botón que permite navegar a la página del manual de uso
        self.manual_button = QPushButton("Manual")
        self.manual_button.setFont(QFont("Arial", 16))
        self.manual_button.setStyleSheet(
            "QPushButton {"
            "  background-color: #28a745;"  # Color verde
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
        # Conecta el botón "Manual" para mostrar la página del manual
        self.manual_button.clicked.connect(self.mostrar_manual)

        
        # Botón "Borrar Todo" en el teclado virtual
       
       
        self.clear_all_button = QPushButton("Borrar Todo")
        self.clear_all_button.setFont(QFont("Arial", 10))
        self.clear_all_button.setStyleSheet(
            "QPushButton {"
            "  background-color: #dc3545;"  # Rojo
            "  color: white;"
            "  border-radius: 10px;"
            "  padding:4px;"
            "  font-weight: bold;"
            "}"
            "QPushButton:hover {"
            "  background-color: #c82333;"
            "}"
        )
        aplicar_sombra(self.clear_all_button)
        grid_layout.addWidget(self.clear_all_button, 5, 0, 1, 3)
        # Conecta el botón "Borrar Todo" al método que limpia los campos de entrada
        self.clear_all_button.clicked.connect(self.limpiar_campos)

        # Se añade el contenedor de la calculadora al panel izquierdo
        left_layout.addWidget(calc_container, alignment=Qt.AlignmentFlag.AlignHCenter)
        left_layout.addStretch(1)

        
        # PANEL DERECHO: Resultados, Tabla y Gráfica
        
        right_frame = QFrame()
        right_frame.setStyleSheet("background-color: white;")
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(20, 20, 20, 20)

        # Título para la tabla de iteraciones
        table_title = QLabel("Tabla de Iteraciones Newton-Raphson")
        table_title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        table_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(table_title)

        # Tabla para mostrar los resultados de cada iteración
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)  # Define las 5 columnas: Iteración, xi, f(xi), f'(xi) y Error
        self.tabla.setHorizontalHeaderLabels(["Iteración", "xi", "f(xi)", "f'(xi)", "Error"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.verticalHeader().setVisible(False)  # Se oculta la cabecera de filas
        self.tabla.setAlternatingRowColors(True)        # Alterna colores para mejorar la legibilidad
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

       
        # Label para mostrar el resultado final (último xi obtenido)
        
        self.result_label = QLabel("Resultado: ")
        self.result_label.setFont(QFont("Arial", 16))
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.result_label)

        # Área para la gráfica de Matplotlib
        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(300)
        right_layout.addWidget(self.canvas, stretch=1)

        # Se agrega cada panel (izquierdo y derecho) al QSplitter
        splitter.addWidget(left_frame)
        splitter.addWidget(right_frame)
        splitter.setSizes([700, 700])  # Define el tamaño inicial de cada panel

        # Se establece el layout principal de la página usando el QSplitter
        main_layout = QHBoxLayout(self)
        main_layout.addWidget(splitter)

    def eventFilter(self, source, event):
        """
        Método para detectar el evento de foco en los QLineEdit.
        Actualiza 'current_input' para saber cuál campo está activo.
        """
        if event.type() == QEvent.Type.FocusIn:
            if isinstance(source, QLineEdit):
                self.current_input = source
        return super().eventFilter(source, event)

    def limpiar_campos(self):
        """
        Borra el contenido de todos los campos de entrada.
        """
        self.function_input.clear()   # Limpia f(x)
        self.x0_input.clear()           # Limpia x0
        self.tolerance_input.clear()    # Limpia tolerancia

    def calcular(self):
        """
        Método que ejecuta el algoritmo Newton-Raphson.
        Lee las entradas, valida los datos, realiza las iteraciones y actualiza la tabla,
        la gráfica y el label con el resultado final.
        """
        # Se obtienen y se limpian espacios en blanco de las entradas
        func_str = self.function_input.text().strip()
        x0_str = self.x0_input.text().strip()
        tol_str = self.tolerance_input.text().strip()

        # Asegura el uso del punto como separador decimal
        x0_str = x0_str.replace(',', '.')
        tol_str = tol_str.replace(',', '.')

        # Verifica que ningún campo esté vacío
        if not func_str or not x0_str or not tol_str:
            QMessageBox.warning(self, "Error", "Por favor, complete todos los campos.")
            return

        try:
            # Conversión de las cadenas a números reales
            x0 = float(x0_str)
            tol = float(tol_str)
        except ValueError:
            QMessageBox.warning(self, "Error", "x0 y tolerancia deben ser números.")
            return

        # Se define la variable simbólica 'x'
        x = symbols('x')
        # Se aplican transformaciones para permitir la multiplicación implícita y otras notaciones
        transformations = (standard_transformations + (implicit_multiplication_application, convert_xor))

        # Reemplaza símbolos especiales (por ejemplo, '√' se cambia por 'sqrt')
        func_str = func_str.replace('√(', 'sqrt(')
        func_str = func_str.replace('√x', 'sqrt(x)')

        # Diccionario local para que el parser reconozca funciones y constantes comunes
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
            # Convierte la cadena en una expresión simbólica
            f_sym = parse_expr(func_str, transformations=transformations, local_dict=local_dict)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al interpretar f(x): {e}")
            return

        try:
            # Calcula la derivada simbólica de la función
            fprime_sym = diff(f_sym, x)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al calcular la derivada: {e}")
            return

        try:
            # Convierte la función simbólica y su derivada en funciones numéricas (utilizando el módulo math)
            f_num = lambdify(x, f_sym, modules=['math'])
            fprime_num = lambdify(x, fprime_sym, modules=['math'])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al convertir la función: {e}")
            return

        # Inicialización de parámetros para las iteraciones
        max_iter = 50  # Número máximo de iteraciones permitidas
        iteraciones = []  # Lista para almacenar cada iteración
        xi = x0  # Valor inicial
        error_rel_porcentaje = float('inf')  # Inicializa el error relativo como infinito
        i = 0

        try:
            # Evaluación inicial: calculo de f(x0) y f'(x0)
            fxi = f_num(xi)
            fprime_xi = fprime_num(xi)
            # Se guarda la primera iteración; el error se muestra como infinito en la primera fila
            iteraciones.append((i, xi, fxi, fprime_xi, float('inf')))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error en la evaluación inicial: {e}")
            return

        # Inicio del ciclo iterativo
        i = 1
        while error_rel_porcentaje > tol and i <= max_iter:
            try:
                # Evaluación de la función y su derivada en el valor actual
                fxi = f_num(xi)
                fprime_xi = fprime_num(xi)
                # Verifica que la derivada no sea cero para evitar división por cero
                if abs(fprime_xi) < 1e-10:
                    QMessageBox.warning(self, "Error", "La derivada es casi cero; no se puede continuar.")
                    return

                # Aplica la fórmula de Newton-Raphson para obtener la nueva aproximación
                xi_new = xi - fxi / fprime_xi

                # Cálculo del error relativo (en porcentaje) entre la nueva y la antigua aproximación
                if abs(xi_new) < 1e-10:
                    error_rel_porcentaje = abs(xi_new - xi) * 100
                else:
                    error_rel_porcentaje = abs((xi_new - xi) / xi_new) * 100

                # Se evalúa la función y la derivada en la nueva aproximación
                fxi_new = f_num(xi_new)
                fprime_xi_new = fprime_num(xi_new)
                # Guarda la iteración actual en la lista
                iteraciones.append((i, xi_new, fxi_new, fprime_xi_new, error_rel_porcentaje))

                # Si el error es menor o igual que la tolerancia, se finaliza el ciclo
                if error_rel_porcentaje <= tol:
                    break

                # Actualiza xi para la siguiente iteración
                xi = xi_new
                i += 1
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error en la iteración {i}: {e}")
                return

        # Se actualizan la tabla y la gráfica con los resultados obtenidos
        self.mostrar_resultados(iteraciones)
        self.graficar_resultados(iteraciones)
        # Se actualiza el label "Resultado:" con el último xi obtenido (formateado a 4 decimales)
        resultado_final = iteraciones[-1][1]
        self.result_label.setText(f"Resultado de Xi= {resultado_final:.4f}")

    def mostrar_resultados(self, iteraciones):
        """
        Actualiza la tabla de resultados con los datos de cada iteración.
        Cada fila de la tabla muestra: Iteración, xi, f(xi), f'(xi) y error relativo.
        """
        self.tabla.clearContents()
        self.tabla.setRowCount(len(iteraciones))
        for row, data in enumerate(iteraciones):
            for col, value in enumerate(data):
                # Se formatea la columna de la iteración como entero
                if col == 0:
                    text = str(int(value))
                # En la primera iteración el error se muestra como "---"
                elif col == 4 and row == 0:
                    text = "---"
                else:
                    text = f"{value:.4f}"  # Formato a 4 decimales para los demás valores
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setForeground(QColor(0, 0, 0))
                self.tabla.setItem(row, col, item)
        self.tabla.update()  # Refresca la visualización de la tabla
        QApplication.processEvents()  # Asegura que la interfaz se actualice correctamente

    def graficar_resultados(self, iteraciones):
        """
        Genera la gráfica de la evolución de f(xi) y f'(xi) a lo largo de las iteraciones utilizando Matplotlib.
        """
        # Extrae las listas de valores de xi, f(xi) y f'(xi) de cada iteración
        xi_vals = [it[1] for it in iteraciones]
        fxi_vals = [it[2] for it in iteraciones]
        fprime_vals = [it[3] for it in iteraciones]

        self.figure.clear()  # Limpia la figura actual
        ax = self.figure.add_subplot(111)  # Crea un subgráfico en la figura
        # Grafica f(xi) con círculos y línea continua
        ax.plot(xi_vals, fxi_vals, marker='o', linestyle='-', label='$f(x_i)$')
        # Grafica f'(xi) con cuadrados y línea discontinua
        ax.plot(xi_vals, fprime_vals, marker='s', linestyle='--', label="$f'(x_i)$")
        ax.set_xlabel("$x_i$")  # Etiqueta del eje x
        ax.set_ylabel("Valor")   # Etiqueta del eje y
        ax.set_title("Gráfica de $f(x_i)$ y $f'(x_i)$ vs $x_i$")
        ax.legend()              
        ax.grid(True)            # Activa la cuadrícula
        self.canvas.draw()      

    def mostrar_manual(self):
        """
        Cambia a la página del manual de uso.
        """
        self.main_window.show_manual_page()



# Clase ManualPage: Define la interfaz del manual de uso

class ManualPage(QWidget):
    def __init__(self, main_window):
        """
        Constructor de la página del manual.
        Recibe la ventana principal para permitir la navegación.
        """
        super().__init__()
        self.main_window = main_window
        self.initUI()  # Inicializa la interfaz del manual

    def initUI(self):
        # Define el estilo general de la página del manual (fondo blanco y texto negro)
        self.setStyleSheet("background-color: white; color: black;")
        
        # Crea el layout principal (vertical) para la página
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)

        # Título del manual
        title_label = QLabel("Manual de Uso de la Calculadora Newton-Raphson")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Se crea un área de desplazamiento para el contenido del manual
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: white;")
        layout.addWidget(scroll_area)

        # Contenedor del contenido del manual
        content = QWidget()
        content.setStyleSheet("background-color: white;")
        scroll_area.setWidget(content)
        content_layout = QVBoxLayout(content)

        # Texto formateado en HTML para el manual
        manual_text = (
            "<h3>Descripción de Campos y Funcionalidades</h3>"
            "<p><b>Campo f(x):</b> Ingrese la función matemática de la cual se desea encontrar la raíz. "
            "Se aceptan expresiones simbólicas. "
            "<p><b>Campo x0:</b> Valor inicial para iniciar el método. Es vital para la convergencia.</p>"
            "<p><b>Campo Tolerancia:</b> Porcentaje de error permitido para considerar la convergencia.</p>"
            "<h3>Uso de los Botones</h3>"
            "<p><b>Teclado Virtual:</b> Facilita la entrada de la función. Incluye botones para borrar (CE, C), "
            "operaciones básicas, paréntesis, potencia (^), raíz (√), trigonometría (sin, cos, tan) y logaritmo (ln).</p>"
            "<p><b>Botón Calcular:</b> Ejecuta el método Newton-Raphson y muestra los resultados en una tabla y en una gráfica.</p>"
            "<h3>Resultados y Gráficas</h3>"
            "<p><b>Tabla de Resultados:</b> Muestra cada iteración con xi, f(xi), f'(x_i) y el error relativo.</p>"
            "<p><b>Gráfica:</b> Visualiza la evolución de f(xi) y f'(x_i) a lo largo de las iteraciones.</p>"
            "<h3>Navegación</h3>"
            "<p>Esta página cubre toda la pantalla. Para volver a la calculadora, presione el botón 'Regresar'.</p>"
        )
        manual_label = QLabel(manual_text)
        manual_label.setWordWrap(True)
        manual_label.setTextFormat(Qt.TextFormat.RichText)
        manual_label.setFont(QFont("Arial", 12))
        content_layout.addWidget(manual_label)

        # Botón para regresar a la página de la calculadora
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
        # Conecta el botón "Regresar" al método regresar()
        self.back_button.clicked.connect(self.regresar)
        content_layout.addWidget(self.back_button)

    def regresar(self):
        """
        Cambia a la página de la calculadora.
        """
        self.main_window.show_calculator_page()


# ========================================================
# Clase MainWindow: Ventana Principal de la Aplicación
# ========================================================
class MainWindow(QMainWindow):
    def __init__(self):
        """
        Inicializa la ventana principal y configura la navegación entre la calculadora y el manual.
        """
        super().__init__()
        self.setWindowTitle("Calculadora Newton-Raphson")
        self.stacked_widget = QStackedWidget()  # Crea un widget apilado para cambiar entre páginas

        # Instancia las páginas de la calculadora y del manual
        self.calculator_page = CalculatorPage(self)
        self.manual_page = ManualPage(self)
        # Añade las páginas al widget apilado
        self.stacked_widget.addWidget(self.calculator_page)
        self.stacked_widget.addWidget(self.manual_page)
        # Establece el widget apilado como el contenido central de la ventana
        self.setCentralWidget(self.stacked_widget)

        self.setStyleSheet("background-color: white; color: black;")
        self.showMaximized()  # Muestra la ventana en modo maximizado

    def show_manual_page(self):
        """
        Cambia la visualización a la página del manual.
        """
        self.stacked_widget.setCurrentWidget(self.manual_page)

    def show_calculator_page(self):
        """
        Cambia la visualización a la página de la calculadora.
        """
        self.stacked_widget.setCurrentWidget(self.calculator_page)


# ========================================================
# Inicio de la Aplicación
# ========================================================
if __name__ == "__main__":
    # Se crea la aplicación Qt
    app = QApplication(sys.argv)
    # Se instancia la ventana principal
    window = MainWindow()
    window.show()  # Se muestra la ventana
    # Se ejecuta el bucle de eventos de la aplicación hasta que se cierre
    sys.exit(app.exec())
