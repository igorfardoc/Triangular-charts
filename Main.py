# -*- coding: utf8 -*-
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTableWidgetItem, QComboBox, QCheckBox
from PyQt5.QtWidgets import QFileDialog
import sys
import pygame
from PyQt5 import uic
from PyQt5.QtGui import QIcon, QPixmap
import win32clipboard
from PyQt5.QtCore import Qt, QEvent
import math

pygame.init()


def get_angle(k):
    i = 0.1
    while i <= 59.9:
        now = math.sin(i / 180 * math.pi) / math.sin((60 - i) / 180 * math.pi)
        if now >= k:
            return i
        i += 0.1
    raise ValueError


class EditData(QWidget):
    def __init__(self):
        super().__init__()
        self.file = ''
        self.size_pygame = 600
        self.painter = PyGame()
        self.table = [['', '', '', '', '', 0, False]]
        self.axes = ['', '', '']
        self.net_visible = False
        self.procents_visible = False
        self.icon_size = 10
        self.axes_size = 40
        self.procents_size = 10
        self.picture_size = 200
        self.table1 = []
        self.metkas = [('Красный квадрат', 'red_square.jpg'), ('Чёрный ромб', 'black_romb.jpg'),
                       ('Синий треугольник', 'blue_triangle.jpg'),
                       ('Красный круг', 'red_circle.jpg'), ('Чёрный треугольник', 'black_triangle.jpg')]
        self.edit = True
        self.initUI()

    def initUI(self):
        uic.loadUi('Main.ui', self)
        self.screen = pygame.display.set_mode((self.size_pygame, self.size_pygame))
        self.draw_py_game()

        self.pasteButton.clicked.connect(self.paste)
        self.tablew.setColumnCount(7)
        self.tablew.setHorizontalHeaderLabels(['№ образца', 'A', 'B', 'C', 'Имя группы', 'Маркер', 'Отображать'])
        self.tablew.setRowCount(1)
        self.tablew.cellChanged.connect(self.change_data_table)

        self.axe1.textChanged.connect(self.change_params)
        self.axe2.textChanged.connect(self.change_params)
        self.axe3.textChanged.connect(self.change_params)
        self.net.stateChanged.connect(self.change_params)
        self.procents.stateChanged.connect(self.change_params)
        self.marker_size.valueChanged.connect(self.change_params)
        self.axe_size.valueChanged.connect(self.change_params)
        self.procent_size.valueChanged.connect(self.change_params)
        self.spin_size.valueChanged.connect(self.change_params)
        self.open_file.clicked.connect(self.open_file_d)
        self.save_as_file.clicked.connect(self.save_as)
        self.save_file.clicked.connect(self.save_file1)

        self.save_picture.clicked.connect(self.save)

        self.tablew1.setColumnCount(3)
        self.tablew1.setHorizontalHeaderLabels(['Имя группы', 'Маркер', 'Отображать'])
        self.tablew1.setRowCount(0)
        self.print_table()

    def convert(self, str1):
        return str1 == '1'

    def open_file_d(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Выберете файл", "",
                            "Charts Files (*.cf)")
        if fileName:
            self.file = fileName
            mass = open(fileName).read().split('\n')
            self.net_visible = self.convert(mass[0])
            self.net.setChecked(self.net_visible)
            self.procents_visible = self.convert(mass[1])
            self.procents.setChecked(self.procents_visible)
            self.axes = mass[2:5]
            self.axe1.setText(mass[2])
            self.axe2.setText(mass[3])
            self.axe3.setText(mass[4])
            self.icon_size = int(mass[5])
            self.marker_size.setValue(self.icon_size)
            self.axes_size = int(mass[6])
            self.axe_size.setValue(self.axes_size)
            self.procents_size = int(mass[7])
            self.procent_size.setValue(self.procents_size)
            self.picture_size = int(mass[8])
            self.spin_size.setValue(self.picture_size)
            self.table = []
            for i in range(9, len(mass)):
                mass1 = mass[i].split('~')
                self.table.append(mass1[:5] + [int(mass1[5]), self.convert(mass1[6])])
            self.table1 = []
            self.update_table1()
            self.draw_table1()
            self.print_table()
            self.draw_py_game()

    def convert1(self, str1):
        if str1:
            return '1'
        return '0'

    def save_as(self):
        name, _ = QFileDialog.getSaveFileName(self, 'Сохраните файл', directory='Chart.cf', filter="Charts Files (*.cf)")
        if name:
            self.file = name
            mass = []
            mass.append(self.convert1(self.net_visible))
            mass.append(self.convert1(self.procents_visible))
            mass += self.axes
            mass.append(str(self.icon_size))
            mass.append(str(self.axes_size))
            mass.append(str(self.procents_size))
            mass.append(str(self.picture_size))
            for i in range(len(self.table)):
                a = self.table[i][:5] + [str(self.table[i][5]), self.convert1(self.table[i][6])]
                mass.append('~'.join(a))
            open(name, 'w').write('\n'.join(mass))

    def save_file1(self):
        if not self.file:
            self.save_as()
            return
        name = self.file
        mass = []
        mass.append(self.convert1(self.net_visible))
        mass.append(self.convert1(self.procents_visible))
        mass += self.axes
        mass.append(str(self.icon_size))
        mass.append(str(self.axes_size))
        mass.append(str(self.procents_size))
        mass.append(str(self.picture_size))
        for i in range(len(self.table)):
            mass.append('~'.join(self.table[i][:5] + [str(self.table[i][5]), self.convert1(self.table[i][6])]))
        open(name, 'w').write('\n'.join(mass))

    def save(self):
        name = QFileDialog.getSaveFileName(self, 'Сохранение', filter='.png file (*.png)',
                                           directory='picture.png')
        if name[0]:
            koef = self.picture_size / self.size_pygame
            points = []
            for i in range(len(self.table)):
                if self.table[i][6]:
                    now = []
                    now.append(['', '', ''])
                    for j in range(3):
                        try:
                            now[0][j] = int(self.table[i][1 + j])
                        except:
                            continue
                    now.append(self.metkas[self.table[i][5]][0])
                    points.append(now)
            d = {'points': points, 'sizei': int(self.icon_size * koef), 'net': self.net_visible,
                 'sides': self.axes, 'side_size': int(self.axes_size * koef), 'procents': self.procents_visible,
                 'procent_size': int(self.procents_size * koef)}
            surface = self.painter.get_surface(d, self.picture_size)
            pygame.image.save(surface, name[0])

    def change_params(self, val):
        self.axes[0] = self.axe1.text()
        self.axes[1] = self.axe2.text()
        self.axes[2] = self.axe3.text()
        self.procents_visible = self.procents.isChecked()
        self.net_visible = self.net.isChecked()
        self.procents_size = self.procent_size.value()
        self.axes_size = self.axe_size.value()
        self.icon_size = self.marker_size.value()
        self.picture_size = self.spin_size.value()
        self.draw_py_game()

    def paste(self):
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        data = data.split('\r\n')
        r = self.tablew.currentRow()
        c = self.tablew.currentColumn()
        mass = []
        for i in range(len(data)):
            now = [''] * c
            if data[i] == '':
                continue
            data[i] = data[i].split('\t')
            for j in range(len(data[i])):
                now.append(data[i][j])
            if len(now) > 5:
                return
            mass.append(now + [''] * (5 - len(now)) + [0, False])
        self.table = self.table[:r] + mass + self.table[r:]
        self.update_table1()
        self.draw_table1()
        self.print_table()

    def nothing(self):
        pass

    def change_data_table(self, r, c):
        if not self.edit:
            return
        self.table[r][c] = self.tablew.item(r, c).text()
        if self.table[len(self.table) - 1][:5] != ['', '', '', '', '']:
            self.table.append(['', '', '', '', '', 0, False])
        self.update_table1()
        self.draw_table1()
        self.print_table()
        self.draw_py_game()

    def update_table1(self):
        newtable1 = []
        have = set()
        for i in self.table:
            if i[4] == '' or i[4] in have:
                continue
            ok = False
            for j in self.table1:
                if j[0] == i[4]:
                    ok = True
                    newtable1.append(j)
                    break
            if not ok:
                newtable1.append([i[4], 0, False])
            have.add(i[4])
        self.table1 = newtable1

    def draw_table1(self):
        self.tablew1.setColumnCount(3)
        self.tablew1.setHorizontalHeaderLabels(['Имя группы', 'Маркер', 'Отображать'])
        self.tablew1.setRowCount(len(self.table1))
        for i in range(len(self.table1)):
            a = QTableWidgetItem(self.table1[i][0])
            a.setFlags(a.flags() ^ Qt.ItemIsEditable)
            self.tablew1.setItem(i, 0, a)

            self.tablew1.setCellWidget(i, 1, QComboBox())
            for k, l in self.metkas[::-1]:
                self.tablew1.cellWidget(i, 1).insertItem(0, k)
                self.tablew1.cellWidget(i, 1).setItemIcon(0, QIcon(QPixmap(l)))
            self.tablew1.cellWidget(i, 1).setCurrentIndex(self.table1[i][1])
            self.tablew1.cellWidget(i, 1).currentIndexChanged.connect(self.table1_combo_change)

            d = QCheckBox()
            d.setChecked(self.table1[i][2])
            d.stateChanged.connect(self.table1_checkbox_change)
            self.tablew1.setCellWidget(i, 2, d)

    def table1_combo_change(self, state):
        name = ''
        for i in range(len(self.table1)):
            if self.tablew1.cellWidget(i, 1) == self.sender():
                self.table1[i][1] = state
                name = self.table1[i][0]
                break
        if name != '':
            for i in range(len(self.table)):
                if self.table[i][4] == name:
                    self.table[i][5] = state
        self.print_table()
        self.draw_py_game()

    def table1_checkbox_change(self, state):
        name = ''
        for i in range(len(self.table1)):
            if self.tablew1.cellWidget(i, 2) == self.sender():
                if state == 2:
                    self.table1[i][2] = True
                else:
                    self.table1[i][2] = False
                name = self.table1[i][0]
                break
        if name != '':
            for i in range(len(self.table)):
                if self.table[i][4] == name:
                    if state == 2:
                        self.table[i][6] = True
                    else:
                        self.table[i][6] = False
        self.print_table()
        self.draw_py_game()

    def combo_change(self, state):
        for i in range(len(self.table)):
            if self.tablew.cellWidget(i, 5) == self.sender():
                self.table[i][5] = state
                break
        self.draw_py_game()

    def checkbox_change(self, state):
        for i in range(len(self.table)):
            if self.tablew.cellWidget(i, 6) == self.sender():
                if state == 2:
                    self.table[i][6] = True
                else:
                    self.table[i][6] = False
                break
        self.draw_py_game()

    def print_table(self):
        self.edit = False
        self.tablew.setRowCount(len(self.table))
        if len(self.table) > 1:
            1 == 1
        for i in range(len(self.table)):
            for j in range(5):
                self.tablew.setItem(i, j, QTableWidgetItem(self.table[i][j]))
            self.tablew.setCellWidget(i, 5, QComboBox())
            for k, l in self.metkas[::-1]:
                self.tablew.cellWidget(i, 5).insertItem(0, k)
                self.tablew.cellWidget(i, 5).setItemIcon(0, QIcon(QPixmap(l)))
            self.tablew.cellWidget(i, 5).setCurrentIndex(self.table[i][5])
            self.tablew.cellWidget(i, 5).currentIndexChanged.connect(self.combo_change)

            d = QCheckBox()
            d.setChecked(self.table[i][6])
            d.stateChanged.connect(self.checkbox_change)
            self.tablew.setCellWidget(i, 6, d)
        self.edit = True

    def draw_py_game(self):
        points = []
        for i in range(len(self.table)):
            if self.table[i][6]:
                now = []
                now.append(['', '', ''])
                for j in range(3):
                    try:
                        now[0][j] = int(self.table[i][1 + j])
                    except:
                        continue
                now.append(self.metkas[self.table[i][5]][0])
                points.append(now)
        d1 = {'points': points, 'sizei': self.icon_size, 'net': self.net_visible,
             'sides': self.axes, 'side_size': self.axes_size, 'procents': self.procents_visible,
             'procent_size': self.procents_size}
        global d, size
        d = d1
        size = self.size_pygame
        self.screen.blit(self.painter.get_surface(), (0, 0))
        pygame.display.flip()


d = {}
size = 0


class PyGame:
    def __init__(self):
        pass

    def get_surface(self):
        global d, size
        sc = pygame.Surface((size, size))
        a = size / 4 * 3
        med = (a * a - a * a / 4) ** 0.5
        sc.fill((255, 255, 255))
        #############################
        fs = d['side_size']
        f = pygame.font.SysFont('arial', fs)
        t1 = f.render(d['sides'][0], 1, (0, 0, 0))
        x = size / 2 - t1.get_width() / 2
        y = size / 2 + med / 3 + t1.get_height() / 3
        sc.blit(t1, (round(x), round(y)))
        #
        t2 = f.render(d['sides'][1], 1, (0, 0, 0))
        sur1 = pygame.Surface((t2.get_width(), t2.get_height()))
        sur1.fill((255, 255, 255))
        sur1.blit(t2, (0, 0))
        sur1 = pygame.transform.rotate(sur1, 60)
        w = t2.get_width()
        h = t2.get_height()
        x, y = size / 2 - a / 4, size / 2 + med / 3 - a / 2 * (3 ** 0.5 / 2)
        vec = [-3 ** 0.5, -1]
        l = (vec[0] * vec[0] + vec[1] * vec[1]) ** 0.5
        vec[0], vec[1] = vec[0] / l, vec[1] / l
        x, y = x + vec[0] * 0.8333 * h, y + vec[1] * 0.8333 * h
        x -= (h * (3 ** 0.5 / 2) + 1 / 2 * w) / 2
        y -= (w * (3 ** 0.5 / 2) + 1 / 2 * h) / 2
        sc.blit(sur1, (round(x), round(y)))
        #
        t3 = f.render(d['sides'][2], 1, (0, 0, 0))
        sur2 = pygame.Surface((t3.get_width(), t3.get_height()))
        sur2.fill((255, 255, 255))
        sur2.blit(t3, (0, 0))
        sur2 = pygame.transform.rotate(sur2, 300)
        w = t3.get_width()
        h = t3.get_height()
        x, y = size / 2 + a / 4, size / 2 + med / 3 - a / 2 * (3 ** 0.5 / 2)
        vec = [3 ** 0.5, -1]
        l = (vec[0] * vec[0] + vec[1] * vec[1]) ** 0.5
        vec[0], vec[1] = vec[0] / l, vec[1] / l
        x, y = x + vec[0] * 0.8333 * h, y + vec[1] * 0.8333 * h
        x -= (h * (3 ** 0.5 / 2) + 1 / 2 * w) / 2
        y -= (w * (3 ** 0.5 / 2) + 1 / 2 * h) / 2
        sc.blit(sur2, (round(x), round(y)))
        ############################
        if d['procents']:
            f = pygame.font.SysFont('arial', d['procent_size'])
            for i in range(11):
                t = f.render(str(i * 10), 1, (0, 0, 0))
                w = t.get_width()
                h = t.get_height()
                x = size / 2 + a * (-i + 5) / 10 - w / 2
                y = size / 2 + med / 3 + h / 10
                sc.blit(t, (x, y))
            for i in range(11):
                t = f.render(str(i * 10), 1, (0, 0, 0))
                w = t.get_width()
                h = t.get_height()
                s = pygame.Surface((w, h))
                s.fill((255, 255, 255))
                s.blit(t, (0, 0))
                x = size / 2 - a / 2 + 1 / 2 * i * a / 10
                y = size / 2 + med / 3 - (3 ** 0.5 / 2) * i * a / 10
                vec = [-(3 ** 0.5), -1]
                l = (vec[0] * vec[0] + vec[1] * vec[1]) ** 0.5
                vec[0], vec[1] = vec[0] / l, vec[1] / l
                x += vec[0] * (h / 2 + h / 10)
                y += vec[1] * (h / 2 + h / 10)
                s = pygame.transform.rotate(s, 60)
                x -= (1 / 2 * w + (3 ** 0.5 / 2) * h) / 2
                y -= (1 / 2 * h + (3 ** 0.5 / 2) * w) / 2
                sc.blit(s, (x, y))
            for i in range(11):
                t = f.render(str((10 - i) * 10), 1, (0, 0, 0))
                w = t.get_width()
                h = t.get_height()
                s = pygame.Surface((w, h))
                s.fill((255, 255, 255))
                s.blit(t, (0, 0))
                x = size / 2 + a / 2 - 1 / 2 * i * a / 10
                y = size / 2 + med / 3 - (3 ** 0.5 / 2) * i * a / 10
                vec = [(3 ** 0.5), -1]
                l = (vec[0] * vec[0] + vec[1] * vec[1]) ** 0.5
                vec[0], vec[1] = vec[0] / l, vec[1] / l
                x += vec[0] * (h / 2 + h / 10)
                y += vec[1] * (h / 2 + h / 10)
                s = pygame.transform.rotate(s, 300)
                x -= (1 / 2 * w + (3 ** 0.5 / 2) * h) / 2
                y -= (1 / 2 * h + (3 ** 0.5 / 2) * w) / 2
                sc.blit(s, (x, y))
        ################################
        pointa = (round(size / 2 - a / 2), round(size / 2 + med / 3))
        pointb = (round(size / 2), round(size / 2 - med / 3 * 2))
        pointc = (round(size / 2 + a / 2), round(size / 2 + med / 3))
        pygame.draw.line(sc, (0, 0, 0), pointa, pointb)
        pygame.draw.line(sc, (0, 0, 0), pointa, pointc)
        pygame.draw.line(sc, (0, 0, 0), pointc, pointb)
        if d['net']:
            net_col = (200, 200, 200)
            for i in range(9):
                pygame.draw.line(sc, net_col, (size / 2 - a / 2 + (1 + i) * a / 10, size / 2 + med / 3),
                                 (size / 2 + a / 2 - 1 / 2 * (9 - i) * a / 10,
                                  size / 2 + med / 3 - (9 - i) / 10 * a * (3 ** 0.5 / 2)))
                pygame.draw.line(sc, net_col, (size / 2 - a / 2 + (1 + i) * a / 10, size / 2 + med / 3),
                                 (size / 2 - a / 2 + 1 / 2 * (1 + i) * a / 10,
                                  size / 2 + med / 3 - (i + 1) / 10 * a * (3 ** 0.5 / 2)))
                pygame.draw.line(sc, net_col, (
                size / 2 - 1 / 2 * a * (i + 1) / 10, size / 2 - med / 3 * 2 + (3 ** 0.5 / 2) * a * (i + 1) / 10),
                                 (size / 2 + 1 / 2 * a * (i + 1) / 10,
                                  size / 2 - med / 3 * 2 + (3 ** 0.5 / 2) * a * (i + 1) / 10))
        mass = d['points']
        sizei = d['sizei']
        for i in mass:
            point = i[0]
            fig = i[1].lower()
            if point[0] == '':
                continue
            try:
                a1 = float(point[0])
                b1 = float(point[1])
            except:
                continue
            c1 = 0
            if point[2] == '':
                c1 = 100 - b1 - a1
            else:
                try:
                    c1 = float(point[2])
                except:
                    continue
                a1, b1, c1 = a1 * 100 / (a1 + b1 + c1), b1 * 100 / (a1 + b1 + c1), c1 * 100 / (a1 + b1 + c1)
            # координаты точки
            k1 = b1 / a1
            k2 = b1 / c1
            ang1 = get_angle(k1)
            ang2 = get_angle(k2)
            t2 = math.tan(ang1 / 180 * math.pi)
            t1 = math.tan(ang2 / 180 * math.pi)
            # t1*x=(a - x) * t2
            x = (a * t2) / (t1 + t2)
            y = t1 * x
            x += size / 2 - a / 2
            y = size / 2 + med / 3 - y
            #
            icon = pygame.Surface((sizei, sizei))
            icon.fill((255, 255, 255))
            col = (0, 0, 0)
            if 'красный' in fig:
                col = (255, 0, 0)
            elif 'чёрный' in fig:
                col = (0, 0, 0)
            elif 'зелёный' in fig:
                col = (0, 255, 0)
            elif 'синий' in fig:
                col = (0, 0, 255)
            if 'квадрат' in fig:
                pygame.draw.polygon(icon, col, [(0, 0), (0, sizei), (sizei, sizei), (sizei, 0)])
            elif 'ромб' in fig:
                pygame.draw.polygon(icon, col, [(0, sizei / 2), (sizei / 2, sizei), (sizei, sizei / 2), (sizei / 2, 0)])
            elif 'круг' in fig:
                pygame.draw.circle(icon, col, (int(sizei / 2), int(sizei / 2)), int(sizei / 2))
            elif 'треугольник' in fig:
                pygame.draw.polygon(icon, col, [(0, sizei), (sizei, sizei), (sizei / 2, 0)])
            sc.blit(icon, (x - sizei / 2, y - sizei / 2))
        return sc


app = QApplication([])
ex = EditData()
ex.show()
sys.exit(app.exec())