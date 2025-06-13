import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QSystemTrayIcon, QMenu, QButtonGroup
)
from PySide6.QtCore import QTimer, Qt, QRect, QPoint
from PySide6.QtGui import QPainter, QPen, QColor, QIcon, QFont, QPainterPath

class PomodoroTimer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pomodoro Profesional")
        self.setFixedSize(340, 420)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Durations in minutes (change here if needed)
        self.duracion_trabajo = 25
        self.duracion_descanso_corto = 5
        self.duracion_descanso_largo = 15

        self.drag_pos = None
        self.resizing = False
        self.handle_size = 16

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
        self.reloj.setFont(QFont("Arial", 48))
        main_layout.addWidget(self.reloj)

        mode_layout = QHBoxLayout()
        self.btn_pomodoro = QPushButton("Pomodoro")
        self.btn_pomodoro.setCheckable(True)
        self.btn_pomodoro.setChecked(True)
        self.btn_short = QPushButton("Short Break")
        self.btn_short.setCheckable(True)
        self.btn_long = QPushButton("Long Break")
        self.btn_long.setCheckable(True)

        btn_style = (
            "QPushButton {border:none;background:transparent;padding:6px;}"
            "QPushButton:checked {color:#7e5bef;font-weight:bold;}"
        )
        for b in (self.btn_pomodoro, self.btn_short, self.btn_long):
            b.setStyleSheet(btn_style)

        self.mode_group = QButtonGroup(self)
        self.mode_group.setExclusive(True)
        for btn in (self.btn_pomodoro, self.btn_short, self.btn_long):
            self.mode_group.addButton(btn)
            mode_layout.addWidget(btn)
            btn.clicked.connect(self.cambiar_modo)

        main_layout.addLayout(mode_layout)

        btn_layout = QHBoxLayout()
        self.boton_inicio = QPushButton("Iniciar")
        self.boton_inicio.setStyleSheet(
            """
            QPushButton {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 20px;
                font-size: 16px;
                padding: 8px 16px;
            }
            QPushButton:hover {background-color: #f0f0f0;}
            """
        )
        self.boton_inicio.clicked.connect(self.toggle_timer)
        btn_layout.addWidget(self.boton_inicio)

        self.boton_reset = QPushButton("Reset")
        self.boton_reset.clicked.connect(self.reset_timer)
        btn_layout.addWidget(self.boton_reset)

        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def cambiar_modo(self):
        if self.btn_pomodoro.isChecked():
            self.tiempo_total = self.duracion_trabajo * 60
        elif self.btn_short.isChecked():
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
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        bg_rect = self.rect().adjusted(5, 5, -5, -5)
        path = QPainterPath()
        path.addRoundedRect(bg_rect, 30, 30)
        painter.fillPath(path, QColor("#ffffff"))

        if self.tiempo_total > 0:
            progreso = 1 - (self.tiempo_restante / self.tiempo_total)
            arc_rect = bg_rect.adjusted(35, 35, -35, -175)
            track_pen = QPen(QColor("#e6e6e6"), 10)
            painter.setPen(track_pen)
            painter.drawArc(arc_rect, 0, 360 * 16)

            pen = QPen(QColor("#7e5bef"), 10)
            painter.setPen(pen)
            painter.drawArc(arc_rect, 90 * 16, -progreso * 360 * 16)

        handle = QRect(self.width() - self.handle_size,
                       self.height() - self.handle_size,
                       self.handle_size, self.handle_size)
        painter.fillRect(handle, QColor("#dddddd"))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if (self.width() - event.pos().x() <= self.handle_size and
                    self.height() - event.pos().y() <= self.handle_size):
                self.resizing = True
                self.drag_pos = event.globalPosition().toPoint()
                self.start_size = self.size()
            else:
                self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.drag_pos is None:
            return
        if self.resizing:
            delta = event.globalPosition().toPoint() - self.drag_pos
            new_width = max(200, self.start_size.width() + delta.x())
            new_height = max(200, self.start_size.height() + delta.y())
            self.resize(new_width, new_height)
        else:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, _):
        self.drag_pos = None
        self.resizing = False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    timer = PomodoroTimer()
    timer.show()
    sys.exit(app.exec())
