import sys
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath
import numpy as np
import pyqtgraph as pg

class Rura:
    def __init__(self, punkty, grubosc=12, kolor=Qt.gray):
        self.punkty = [QPointF(float(p[0]), float(p[1])) for p in punkty]
        self.grubosc = grubosc
        self.kolor_rury = kolor
        self.kolor_cieczy = QColor(0, 180, 255)
        self.czy_plynie = False

    def ustaw_przeplyw(self, plynie):
        self.czy_plynie = plynie
   
    def draw(self, painter):
        if len(self.punkty) < 2:
            return

        path = QPainterPath()
        path.moveTo(self.punkty[0])
        for p in self.punkty[1:]:
            path.lineTo(p)

        pen_rura = QPen(self.kolor_rury, self.grubosc, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen_rura)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

        if self.czy_plynie:
            pen_ciecz = QPen(self.kolor_cieczy, self.grubosc - 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen_ciecz)
            painter.drawPath(path)


class Zbiornik:
    def __init__(self, x, y, width=100, height=140, nazwa=""):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.nazwa = nazwa

        self.pojemnosc = 100.0
        self.aktualna_ilosc = 0.0
        self.poziom = 0.0

    def dodaj_ciecz(self, ilosc):
        wolne = self.pojemnosc - self.aktualna_ilosc
        dodano = min(ilosc, wolne)
        self.aktualna_ilosc += dodano
        self.aktualizuj_poziom()
        return dodano

    def usun_ciecz(self, ilosc):
        usunieto = min(ilosc, self.aktualna_ilosc)
        self.aktualna_ilosc -= usunieto
        self.aktualizuj_poziom()
        return usunieto

    def aktualizuj_poziom(self):
        self.poziom = self.aktualna_ilosc / self.pojemnosc

    def czy_pusty(self):
        return self.aktualna_ilosc <= 0.1

    def czy_pelny(self):
        return self.aktualna_ilosc >= self.pojemnosc - 0.1

    def punkt_gora_srodek(self):
        return (self.x + self.width / 2, self.y)

    def punkt_dol_srodek(self):
        return (self.x + self.width / 2, self.y + self.height)
    
    def srodek_x(self):
        return (self.x + self.width / 2)

    def draw(self, painter):
        if self.poziom > 0:
            h = self.height * self.poziom
            y = self.y + self.height - h
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(0, 120, 255, 200))
            painter.drawRect(int(self.x + 3), int(y), int(self.width - 6), int(h - 2))

        pen = QPen(Qt.white, 4)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))
        painter.drawText(int(self.x), int(self.y - 10), self.nazwa)


class Pompa:
    def __init__(self, x, y, moc=1.2):
        self.x = x
        self.y = y
        self.moc = moc
        self.wlaczona = False

    def wlacz(self):
        self.wlaczona = True

    def wylacz(self):
        self.wlaczona = False

    def toggle(self):
        self.wlaczona = not self.wlaczona

    def draw(self, painter):
        # obudowa
        painter.setPen(QPen(Qt.white, 3))
        painter.setBrush(QColor(60, 60, 60))
        painter.drawEllipse(self.x - 20, self.y - 20, 40, 40)

        # środek (status)
        kolor = QColor(0, 255, 0) if self.wlaczona else QColor(150, 0, 0)
        painter.setBrush(kolor)
        painter.drawEllipse(self.x - 8, self.y - 8, 16, 16)

        # opis
        painter.setPen(Qt.white)
        painter.drawText(self.x - 25, self.y + 35, "Pompa")



class PanelSterowania(QWidget):
    def __init__(self, symulacja):
        super().__init__()
        self.sym = symulacja

        self.setWindowTitle("Panel sterowania")
        self.setFixedSize(400, 200)

        # --- PRZYCISKI ---
        self.btn_start = QPushButton("Start / Stop", self)
        self.btn_start.setGeometry(20, 20, 120, 30)
        self.btn_start.clicked.connect(self.sym.przelacz_symulacje)

        self.btn_z2_plus = QPushButton("Z2 +", self)
        self.btn_z2_plus.setGeometry(20, 70, 60, 30)
        self.btn_z2_plus.clicked.connect(lambda: self.sym.napelnij(self.sym.z2))

        self.btn_z2_minus = QPushButton("Z2 -", self)
        self.btn_z2_minus.setGeometry(90, 70, 60, 30)
        self.btn_z2_minus.clicked.connect(lambda: self.sym.oproznij(self.sym.z2))

        self.btn_z3_plus = QPushButton("Z3 +", self)
        self.btn_z3_plus.setGeometry(20, 105, 60, 30)
        self.btn_z3_plus.clicked.connect(lambda: self.sym.napelnij(self.sym.z3))

        self.btn_z3_minus = QPushButton("Z3 -", self)
        self.btn_z3_minus.setGeometry(90, 105, 60, 30)
        self.btn_z3_minus.clicked.connect(lambda: self.sym.oproznij(self.sym.z3))

        self.btn_pompa1 = QPushButton("Pompa 1 ON/OFF", self)
        self.btn_pompa1.setGeometry(20, 140, 150, 30)
        self.btn_pompa1.clicked.connect(self.sym.pompa1.toggle)

        self.btn_pompa2 = QPushButton("Pompa 2 ON/OFF", self)
        self.btn_pompa2.setGeometry(200, 140, 150, 30)
        self.btn_pompa2.clicked.connect(self.sym.pompa2.toggle)


class RollingPlotWindow(QtWidgets.QMainWindow):
    def __init__(self, symulacja):
        super().__init__()

        self.sym = symulacja
        self.z1 = symulacja.z1
        

        # Konfiguracja głównego okna
        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)
        self.graphWidget.setTitle("Poziom cieczy w z1 Dane w czasie rzeczywistym")
        self.graphWidget.setLabel('left', 'Poziom cieczy')
        self.graphWidget.setLabel('bottom', 'Czas ')
        self.graphWidget.showGrid(x=True, y=True)

        # Inicjalizacja bufora danych (50 zer na start)
        self.data_range = 50
        self.y_data = [0] * self.data_range
        self.x_data = list(range(self.data_range))  # Oś X: 0..49

        # Referencja do linii wykresu (aby ją potem aktualizować)
        self.data_line = self.graphWidget.plot(
            self.x_data,
            self.y_data,
            pen='g'
        )

        # Zmienna pomocnicza do generowania "czasu" dla funkcji sin()
        self.time_counter = 0

        # Timer
        self.timer = QtCore.QTimer()
        self.timer.setInterval(500)  # 500 ms = 0.5 s
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    def update_plot_data(self):
        # 1. Przesunięcie czasu
        self.time_counter += 0.2

        # 2. Generowanie nowej danej: sin(czas + losowość)
        
        new_value = self.z1.aktualna_ilosc

        # 3. Aktualizacja bufora danych
        self.y_data = self.y_data[1:]      # usunięcie najstarszej próbki
        self.y_data.append(new_value)      # dodanie nowej

        # 4. Odświeżenie wykresu
        self.data_line.setData(self.x_data, self.y_data)



class SymulacjaKaskady(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Kaskada: Dół -> Góra")
        self.setFixedSize(900, 600)
        self.setStyleSheet("background-color: #222;")
        
        self.z1 = Zbiornik(400, 20, nazwa="Zbiornik 1")
        self.z1.aktualna_ilosc = 100
        self.z1.aktualizuj_poziom()

        self.z2 = Zbiornik(250, 220, nazwa="Zbiornik 2")
        self.z3 = Zbiornik(550, 220, nazwa="Zbiornik 3")
        self.z4 = Zbiornik(100, 420, nazwa="Zbiornik 4")
        self.z5 = Zbiornik(700, 420, nazwa="Zbiornik 5")
        self.zbiorniki = [self.z1, self.z2, self.z3, self.z4, self.z5]

        self.rura1 = Rura([self.z1.punkt_dol_srodek(),(450, 200),(self.z2.srodek_x(),200), self.z2.punkt_gora_srodek()])
        self.rura2 = Rura([self.z1.punkt_dol_srodek(),(450, 200),(self.z3.srodek_x(),200), self.z3.punkt_gora_srodek()])
        self.rura3 = Rura([self.z2.punkt_dol_srodek(),(self.z2.srodek_x(),400),(self.z4.srodek_x(),400), self.z4.punkt_gora_srodek()])
        self.rura4 = Rura([self.z3.punkt_dol_srodek(),(self.z3.srodek_x(),400),(self.z5.srodek_x(),400), self.z5.punkt_gora_srodek()])
        self.rura5 = Rura([self.z4.punkt_dol_srodek(),(self.z4.srodek_x(), 560),(80, 560),(80, 10),(405,10),self.z1.punkt_gora_srodek()])
        self.rura6 = Rura([self.z5.punkt_dol_srodek(),(self.z5.srodek_x(), 560),(820, 560),(820, 10),(495,10),self.z1.punkt_gora_srodek()])

        self.rury = [self.rura1, self.rura2, self.rura3, self.rura4, self.rura5, self.rura6]
        
        #pompa 
        self.pompa1 = Pompa(150,460)
        self.pompa2= Pompa(750,460)
        

        self.timer = QTimer()
        self.timer.timeout.connect(self.logika_przeplywu)
        self.running = False
        self.flow_speed = 0.8

       

        



  

    # ===== SLOTY =====
    def napelnij(self, zbiornik):
        zbiornik.aktualna_ilosc = zbiornik.pojemnosc
        zbiornik.aktualizuj_poziom()
        self.update()

    def oproznij(self, zbiornik):
        zbiornik.aktualna_ilosc = 0.0
        zbiornik.aktualizuj_poziom()
        self.update()

    def przelacz_symulacje(self):
        self.timer.start(20) if not self.running else self.timer.stop()
        self.running = not self.running

    def logika_przeplywu(self):
        if not self.z1.czy_pusty() and not self.z2.czy_pelny():
            self.z2.dodaj_ciecz(self.z1.usun_ciecz(self.flow_speed))
            self.z3.dodaj_ciecz(self.z1.usun_ciecz(self.flow_speed))
            self.rura1.ustaw_przeplyw(True)
            self.rura2.ustaw_przeplyw(True)
        else:
            self.rura1.ustaw_przeplyw(False)
            self.rura2.ustaw_przeplyw(False)

        if self.z2.aktualna_ilosc > 5 and not self.z4.czy_pelny():
            self.z4.dodaj_ciecz(self.z2.usun_ciecz(self.flow_speed))
            self.rura3.ustaw_przeplyw(True)
           
        else:
            self.rura3.ustaw_przeplyw(False)
            

        if self.z3.aktualna_ilosc > 5 and not self.z5.czy_pelny():
            self.z5.dodaj_ciecz(self.z3.usun_ciecz(self.flow_speed))
            self.rura4.ustaw_przeplyw(True)
        else:
            self.rura4.ustaw_przeplyw(False)
#pompa logika
        if not self.z4.czy_pusty() and (self.pompa1.wlaczona):
            self.z1.dodaj_ciecz(self.z4.usun_ciecz(self.flow_speed * self.pompa1.moc))
            self.rura5.ustaw_przeplyw(True)
        else:
            self.rura5.ustaw_przeplyw(False)
            
        if not self.z5.czy_pusty() and (self.pompa2.wlaczona):
            self.z1.dodaj_ciecz(self.z5.usun_ciecz(self.flow_speed * self.pompa2.moc))
            self.rura6.ustaw_przeplyw(True)
        else:
            self.rura6.ustaw_przeplyw(False)
        if not self.z2.czy_pusty() and (self.pompa1.wlaczona):
            self.z1.dodaj_ciecz(self.z2.usun_ciecz(self.flow_speed * self.pompa1.moc))
            self.rura5.ustaw_przeplyw(True)
        else:
            self.rura5.ustaw_przeplyw(False)
        if not self.z3.czy_pusty() and (self.pompa2.wlaczona):
            self.z1.dodaj_ciecz(self.z3.usun_ciecz(self.flow_speed * self.pompa2.moc))
            self.rura6.ustaw_przeplyw(True)
        else:
            self.rura6.ustaw_przeplyw(False)
        if (self.pompa1.wlaczona == True) and (self.pompa2.wlaczona == True) and self.z1.aktualna_ilosc > 99.0:
            self.z2.dodaj_ciecz(self.z1.usun_ciecz(self.flow_speed))
            self.z3.dodaj_ciecz(self.z1.usun_ciecz(self.flow_speed))
            self.rura1.ustaw_przeplyw(True)
            self.rura2.ustaw_przeplyw(True)
        else:
            self.rura1.ustaw_przeplyw(False)
            self.rura2.ustaw_przeplyw(False)

        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        for r in self.rury:
            r.draw(p)
        for z in self.zbiorniki:
            z.draw(p)
        self.pompa1.draw(p)
        self.pompa2.draw(p)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    sym = SymulacjaKaskady()
    panel = PanelSterowania(sym)
    main = RollingPlotWindow(sym)
    main.show()
    sym.show()
    panel.show()

    sys.exit(app.exec_())
