import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath


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
        
        
        self.rury = [self.rura1, self.rura2, self.rura3, self.rura4]

        



        

        self.timer = QTimer()
        self.timer.timeout.connect(self.logika_przeplywu)

        self.btn_start = QPushButton("Start / Stop", self)
        self.btn_start.setGeometry(20, 570, 120, 30)
        self.btn_start.clicked.connect(self.przelacz_symulacje)

        # --- PANEL PRZYCISKÓW ---
        self.dodaj_przyciski_zbiornikow()

        self.running = False
        self.flow_speed = 0.8



    # ===== PRZYCISKI =====
    def dodaj_przyciski_zbiornikow(self):
        y = 570
        x = 170
        step = 230

        self.btn_z1_plus = QPushButton("Z1 +", self)
        self.btn_z1_minus = QPushButton("Z1 -", self)
        self.btn_z1_plus.setGeometry(x, y, 50, 30)
        self.btn_z1_minus.setGeometry(x + 60, y, 50, 30)
        self.btn_z1_plus.clicked.connect(lambda: self.napelnij(self.z1))
        self.btn_z1_minus.clicked.connect(lambda: self.oproznij(self.z1))

        self.btn_z2_plus = QPushButton("Z2 +", self)
        self.btn_z2_minus = QPushButton("Z2 -", self)
        self.btn_z2_plus.setGeometry(x + step, y, 50, 30)
        self.btn_z2_minus.setGeometry(x + step + 60, y, 50, 30)
        self.btn_z2_plus.clicked.connect(lambda: self.napelnij(self.z2))
        self.btn_z2_minus.clicked.connect(lambda: self.oproznij(self.z2))

        self.btn_z3_plus = QPushButton("Z3 +", self)
        self.btn_z3_minus = QPushButton("Z3 -", self)
        self.btn_z3_plus.setGeometry(x + 2 * step, y, 50, 30)
        self.btn_z3_minus.setGeometry(x + 2 * step + 60, y, 50, 30)
        self.btn_z3_plus.clicked.connect(lambda: self.napelnij(self.z3))
        self.btn_z3_minus.clicked.connect(lambda: self.oproznij(self.z3))

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
            self.z5.dodaj_ciecz(self.z3.usun_ciecz(self.flow_speed))
            self.rura4.ustaw_przeplyw(True)
        else:
            self.rura3.ustaw_przeplyw(False)
            self.rura4.ustaw_przeplyw(False)

        self.update()
#zrob tak żeby był warunek że zbiornik drugi musi sie zapelnic zeby zbiornik 3 sie zaczal napelniac
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        for r in self.rury:
            r.draw(p)
        for z in self.zbiorniki:
            z.draw(p)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = SymulacjaKaskady()
    w.show()
    sys.exit(app.exec_())
