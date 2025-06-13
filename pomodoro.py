import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QComboBox, QSpinBox, QMessageBox, QSystemTrayIcon, QMenu
)
from PySide6.QtCore import QTimer, Qt, QSettings
from PySide6.QtGui import QPainter, QPen, QColor, QIcon, QFont

class PomodoroTimer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pomodoro Profesional")
        self.setFixedSize(340, 420)
        self.setStyleSheet(
            """
            QWidget {background-color: #f2f2f2; color: #333; font-family: Arial;}
            QComboBox, QPushButton {
                background-color: #fff;
                border: 1px solid #ccc;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {background-color: #eee;}
            """
        )

        self.settings = QSettings('future', 'pomodoro')
        # Default durations in minutes
        self.duracion_trabajo = self.settings.value('trabajo', 25, int)
        self.duracion_descanso_corto = self.settings.value('corto', 5, int)
        self.duracion_descanso_largo = self.settings.value('largo', 15, int)

        self.tiempo_total = self.duracion_trabajo * 60
        self.tiempo_restante = self.tiempo_total

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_tiempo)

        self.tray = QSystemTrayIcon(QIcon(), self)
        self.tray.setToolTip("Pomodoro en curso")
        tray_menu = QMenu()
        tray_menu.addAction('Mostrar', self.showNormal)
        tray_menu.addAction('Salir', QApplication.quit)
        self.tray.setContextMenu(tray_menu)
        self.tray.show()

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(alignment=Qt.AlignCenter)
        main_layout.setContentsMargins(30, 30, 30, 30)

        self.reloj = QLabel(self.formato_tiempo(self.tiempo_restante))
        self.reloj.setAlignment(Qt.AlignCenter)
        self.reloj.setFont(QFont("Arial", 40, QFont.Bold))
        main_layout.addWidget(self.reloj)

        # Duration controls
        dur_layout = QHBoxLayout()
        self.spin_trabajo = QSpinBox()
        self.spin_trabajo.setRange(1, 120)
        self.spin_trabajo.setValue(self.duracion_trabajo)
        self.spin_trabajo.valueChanged.connect(self.guardar_config)
        dur_layout.addWidget(QLabel("Trabajo:"))
        dur_layout.addWidget(self.spin_trabajo)

        self.spin_corto = QSpinBox()
        self.spin_corto.setRange(1, 60)
        self.spin_corto.setValue(self.duracion_descanso_corto)
        self.spin_corto.valueChanged.connect(self.guardar_config)
        dur_layout.addWidget(QLabel("Corto:"))
        dur_layout.addWidget(self.spin_corto)

        self.spin_largo = QSpinBox()
        self.spin_largo.setRange(1, 60)
        self.spin_largo.setValue(self.duracion_descanso_largo)
        self.spin_largo.valueChanged.connect(self.guardar_config)
        dur_layout.addWidget(QLabel("Largo:"))
        dur_layout.addWidget(self.spin_largo)

        main_layout.addLayout(dur_layout)

        self.combo = QComboBox()
        self.combo.addItems(["Pomodoro", "Descanso corto", "Descanso largo"])
        self.combo.currentIndexChanged.connect(self.cambiar_modo)
        main_layout.addWidget(self.combo)

        btn_layout = QHBoxLayout()
        self.boton_inicio = QPushButton("Iniciar")
        self.boton_inicio.clicked.connect(self.toggle_timer)
        btn_layout.addWidget(self.boton_inicio)

        self.boton_reset = QPushButton("Reset")
        self.boton_reset.clicked.connect(self.reset_timer)
        btn_layout.addWidget(self.boton_reset)

        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def guardar_config(self):
        self.duracion_trabajo = self.spin_trabajo.value()
        self.duracion_descanso_corto = self.spin_corto.value()
        self.duracion_descanso_largo = self.spin_largo.value()
        self.settings.setValue('trabajo', self.duracion_trabajo)
        self.settings.setValue('corto', self.duracion_descanso_corto)
        self.settings.setValue('largo', self.duracion_descanso_largo)
        self.cambiar_modo()

    def cambiar_modo(self):
        modo = self.combo.currentText()
        if modo == "Pomodoro":
            self.tiempo_total = self.duracion_trabajo * 60
        elif modo == "Descanso corto":
            self.tiempo_total = self.duracion_descanso_corto * 60
        else:
            self.tiempo_total = self.duracion_descanso_largo * 60
        self.tiempo_restante = self.tiempo_total
        self.reloj.setText(self.formato_tiempo(self.tiempo_restante))
        self.update()

    def toggle_timer(self):
        if self.timer.isActive():
            self.timer.stop()
            self.boton_inicio.setText("Iniciar")
        else:
            self.timer.start(1000)
            self.boton_inicio.setText("Pausar")

    def reset_timer(self):
        self.timer.stop()
        self.cambiar_modo()
        self.boton_inicio.setText("Iniciar")

    def actualizar_tiempo(self):
        if self.tiempo_restante > 0:
            self.tiempo_restante -= 1
            self.reloj.setText(self.formato_tiempo(self.tiempo_restante))
            self.update()
        else:
            self.timer.stop()
            self.tray.showMessage('Pomodoro', 'Tiempo finalizado')
            self.boton_inicio.setText("Iniciar")

    def formato_tiempo(self, segundos):
        m, s = divmod(segundos, 60)
        return f"{m:02}:{s:02}"

    def paintEvent(self, _):
        if self.tiempo_total == 0:
            return
        progreso = 1 - (self.tiempo_restante / self.tiempo_total)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(40, 40, -40, -180)
        track_pen = QPen(QColor("#d0d0d0"), 10)
        painter.setPen(track_pen)
        painter.drawArc(rect, 0, 360 * 16)

        pen = QPen(QColor("#7e5bef"), 10)
        painter.setPen(pen)
        painter.drawArc(rect, 90 * 16, -progreso * 360 * 16)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    timer = PomodoroTimer()
    timer.show()
    sys.exit(app.exec())
