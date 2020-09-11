# -*- coding: utf8 -*-
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTableWidgetItem, QComboBox, QCheckBox
from PyQt5.QtWidgets import QFileDialog, QTableWidget
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
        i += 0.01
    if k >= 10000:
        return 60
    return 0


class EditData(QWidget):
    def __init__(self):
        super().__init__()
        self.file = ''
        self.size_pygame = 600
        self.painter = PyGame()
        self.table = []
        for i in range(100):
            self.table.append(['', '', '', '', '', 0, True])
        self.axes = ['', '', '']
        self.net_visible = False
        self.procents_visible = False
        self.icon_size = 10
        self.axes_size = 40
        self.procents_size = 10
        self.picture_size = 10 / 2.54 * 200
        self.table1 = []
        self.metkas = [('Красный треугольник', 'red_triangle.jpg'), ('Чёрный треугольник', 'black_triangle.jpg'),
                       ('Синий треугольник', 'blue_triangle.jpg'), ('Красный квадрат', 'red_square.jpg'),
                       ('Чёрный квадрат', 'black_square.jpg'), ('Синий квадрат', 'blue_square.jpg'),
                       ('Красный круг', 'red_circle.jpg'), ('Чёрный круг', 'black_circle.jpg'),
                       ('Синий круг', 'blue_circle.jpg')]
        self.icons = []
        for i, j in self.metkas:
            self.icons.append(QIcon(QPixmap(j)))
        self.edit = True
        self.initUI()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            r = self.tablew.currentRow()
            c = self.tablew.currentColumn()
            if c < 5:
                self.table[r][c] = ''
                self.print_table()
        if int(event.modifiers()) == (Qt.ControlModifier):
            if event.key() == Qt.Key_V:
                self.paste()
        if int(event.modifiers()) == (Qt.ControlModifier):
            if event.key() == Qt.Key_C:
                self.copy_text()

    def copy_text(self):
        text = ''
        ranges = self.tablew.selectedRanges()
        if len(ranges) != 0:
            range1 = ranges[0]
            for i in range(range1.topRow(), range1.bottomRow() + 1):
                for j in range(range1.leftColumn(), range1.rightColumn() + 1):
                    dat = self.table[i][j]
                    if j in [1, 2, 3]:
                        dat = dat.replace('.', ',')
                    if j == range1.rightColumn():
                        text += dat + '\r\n'
                    else:
                        text += dat + '\t'
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text)
        win32clipboard.CloseClipboard()

    def initUI(self):
        uic.loadUi('Main.ui', self)
        self.screen = pygame.display.set_mode((self.size_pygame, self.size_pygame))
        self.draw_py_game()

        self.pasteButton.clicked.connect(self.paste)
        self.copyButton.clicked.connect(self.copy_text)
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
        self.mod1.stateChanged.connect(self.change_params)
        self.mod2.stateChanged.connect(self.change_params)
        self.mod3.stateChanged.connect(self.change_params)
        self.open_file.clicked.connect(self.open_file_d)
        self.save_as_file.clicked.connect(self.save_as)
        self.save_file.clicked.connect(self.save_file1)

        self.save_picture.clicked.connect(self.save)
        self.save_legend.clicked.connect(self.save_legend1)

        self.tablew1.setColumnCount(3)
        self.tablew1.setHorizontalHeaderLabels(['Имя группы', 'Маркер', 'Отображать'])
        self.tablew1.setRowCount(0)
        self.print_table(start=True)

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
            self.picture_size = float(mass[8])
            self.spin_size.setValue(self.picture_size / 200 * 2.54)
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


    def save_legend1(self):
        name = QFileDialog.getSaveFileName(self, 'Сохранение легенды', filter='.png file (*.png)',
                                           directory='picture.png')
        if name[0]:
            surface = self.painter.get_legend(self.table1, self.metkas)
            pygame.image.save(surface, name[0])

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
        name = QFileDialog.getSaveFileName(self, 'Сохранение диаграммы', filter='.png file (*.png)',
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
            d1 = {'points': points, 'sizei': int(self.icon_size * koef), 'net': self.net_visible,
                 'sides': self.axes, 'side_size': int(self.axes_size * koef), 'procents': self.procents_visible,
                 'procent_size': int(self.procents_size * koef)}
            global d, size
            d = d1
            size = self.picture_size
            surface = self.painter.get_surface()
            pygame.image.save(surface, name[0])

    def change_params(self, val):
        global mods
        self.axes[0] = self.axe1.text()
        self.axes[1] = self.axe2.text()
        self.axes[2] = self.axe3.text()
        self.procents_visible = self.procents.isChecked()
        self.net_visible = self.net.isChecked()
        mods[0] = self.mod1.isChecked()
        mods[1] = self.mod2.isChecked()
        mods[2] = self.mod3.isChecked()
        self.procents_size = self.procent_size.value()
        self.axes_size = self.axe_size.value()
        self.icon_size = self.marker_size.value()
        self.picture_size = self.spin_size.value() / 2.54 * 200
        self.draw_py_game()

    def paste(self):
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        data = data.split('\r\n')
        r = self.tablew.currentRow()
        c = self.tablew.currentColumn()
        for i in range(len(data)):
            if data[i] == '':
                continue
            if i + r >= len(self.table) - 1:
                self.table.append(['', '', '', '', '', 0, True])
            data[i] = data[i].split('\t')
            for j in range(len(data[i])):
                if j + c >= 5:
                    continue
                if j + c > 0 or j + c < 4:
                    self.table[i + r][j + c] = data[i][j].replace(',', '.')
                else:
                    self.table[i + r][j + c] = data[i][j]
        if self.table[len(self.table) - 1][:5] != ['', '', '', '', '']:
            self.table.append(['', '', '', '', '', 0, True])
        self.update_table1()
        self.draw_table1()
        self.print_table()
        self.draw_py_game()

    def nothing(self):
        pass

    def change_data_table(self, r, c):
        if not self.edit:
            return
        if c in [1, 2, 3]:
            self.table[r][c] = self.tablew.item(r, c).text().replace(',', '.')
            self.edit = False
            self.tablew.setItem(r, c, QTableWidgetItem(self.table[r][c]))
            self.edit = True
        else:
            self.table[r][c] = self.tablew.item(r, c).text()
        if self.table[len(self.table) - 1][:5] != ['', '', '', '', '']:
            self.table.append(['', '', '', '', '', 0, True])
            self.print_table()
        self.update_table1()
        self.draw_table1()
        #self.print_table()
        self.tablew.resizeColumnsToContents()
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
            for k in range(len(self.metkas) - 1, -1, -1):
                self.tablew1.cellWidget(i, 1).insertItem(0, self.metkas[k][0])
                self.tablew1.cellWidget(i, 1).setItemIcon(0, self.icons[k])
            self.tablew1.cellWidget(i, 1).setCurrentIndex(self.table1[i][1])
            self.tablew1.cellWidget(i, 1).currentIndexChanged.connect(self.table1_combo_change)

            d = QCheckBox()
            d.setChecked(self.table1[i][2])
            d.stateChanged.connect(self.table1_checkbox_change)
            self.tablew1.setCellWidget(i, 2, d)
        self.tablew1.resizeColumnsToContents()
        self.tablew.setColumnWidth(1, 200)

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

    def print_table(self, start=False):
        self.edit = False
        bef = self.tablew.rowCount()
        self.tablew.setRowCount(len(self.table))
        for i in range(len(self.table)):
            for j in range(5):
                self.tablew.setItem(i, j, QTableWidgetItem(self.table[i][j]))
            if bef <= i or start:
                self.tablew.setCellWidget(i, 5, QComboBox())
                for k in range(len(self.metkas) - 1, -1, -1):
                    self.tablew.cellWidget(i, 5).insertItem(0, self.metkas[k][0])
                    self.tablew.cellWidget(i, 5).setItemIcon(0, self.icons[k])
            self.tablew.cellWidget(i, 5).setCurrentIndex(self.table[i][5])
            if bef <= i or start:
                self.tablew.cellWidget(i, 5).currentIndexChanged.connect(self.combo_change)
                self.tablew.setCellWidget(i, 6, QCheckBox())
            self.tablew.cellWidget(i, 6).setChecked(self.table[i][6])
            if bef <= i or start:
                self.tablew.cellWidget(i, 6).stateChanged.connect(self.checkbox_change)
        self.tablew.resizeColumnsToContents()
        self.tablew.setColumnWidth(5, 200)
        self.edit = True

    def draw_py_game(self):
        points = []
        for i in range(len(self.table)):
            if self.table[i][6]:
                now = []
                now.append(['', '', ''])
                for j in range(3):
                    try:
                        now[0][j] = float(self.table[i][1 + j])
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
        src = self.painter.get_surface()
        a = size / 4 * 3
        pygame.draw.line(src, (170, 170, 170), (size / 2 - a / 2, size / 10 * 9),
                         (size / 2 + a / 2, size / 10 * 9))
        pygame.draw.line(src, (170, 170, 170), (size / 2 - a / 2, size / 10 * 8.9),
                         (size / 2 - a / 2, size / 10 * 9.1))
        pygame.draw.line(src, (170, 170, 170), (size / 2 + a / 2, size / 10 * 8.9),
                         (size / 2 + a / 2, size / 10 * 9.1))
        f = pygame.font.SysFont('arial', 20)
        t1 = f.render(str(round(self.picture_size / size * a / 200 * 2.54, 2)) + ' см.', 1, (170, 170, 170))
        src.blit(t1, (size / 2 - t1.get_width() / 2, size / 10 * 9 - 25))
        self.screen.blit(src, (0, 0))
        pygame.display.flip()


d = {}
size = 0
mods = [False, False, False]


class PyGame:
    def __init__(self):
        pass


    def get_legend(self, table, metkas):
        sizei = 60
        height = 100
        width = 1000
        sizes = 50
        f = pygame.font.SysFont('arial', sizes)
        total = 0
        scs = []
        for i in range(len(table)):
            el = table[i]
            str1 = '- ' + el[0]
            fig = metkas[el[1]][0].lower()
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
            mass = []
            mass1 = str1.split(' ')
            now = ''
            for j in range(len(mass1)):
                now1 = now
                now += ' ' + mass1[j]
                t = f.render(now, 1, (0, 0, 0))
                if t.get_width() > width - 2 * sizei - 10:
                    mass.append(now1)
                    now = mass1[j]
            if now != '':
                mass.append(now)
            total += len(mass)
            sc = pygame.Surface((width, height * len(mass)))
            sc.fill((255, 255, 255))
            sc.blit(icon, (sizei / 2, (height - sizei) / 2))
            for j in range(len(mass)):
                t = f.render(mass[j], 1, (0, 0, 0))
                if j == 0:
                    sc.blit(t, (2 * sizei, (height - t.get_height()) / 2))
                else:
                    sc.blit(t, (sizei / 2, j * height + (height - t.get_height()) / 2))
            scs.append(sc)
        sc = pygame.Surface((width, height * total))
        sc.fill((255, 255, 255))
        now = 0
        for j in range(len(scs)):
            sc.blit(scs[j], (0, now))
            now += scs[j].get_height()
        return sc


    def get_surface(self):
        global d, size, mods
        sr = int(size // 500)
        sc = pygame.Surface((size, size))
        a = size / 4 * 3
        med = (a * a - a * a / 4) ** 0.5
        sc.fill((255, 255, 255))
        #############################
        fs = d['side_size']
        f = pygame.font.SysFont('arial', fs)
        t1 = f.render(d['sides'][1], 1, (0, 0, 0))
        x = min(size / 2 + a / 2 - t1.get_width() / 2, size - t1.get_width() - 10)
        y = size / 2 + med / 3 + t1.get_height() / 3
        sc.blit(t1, (round(x), round(y)))
        #
        t2 = f.render(d['sides'][0], 1, (0, 0, 0))
        x = max(size / 2 - a / 2 - t2.get_width() / 2, 10)
        y = size / 2 + med / 3 + t2.get_height() / 3
        sc.blit(t2, (round(x), round(y)))
        #
        t3 = f.render(d['sides'][2], 1, (0, 0, 0))
        x = size / 2 + t3.get_height() / 2
        y = size / 2 - med / 3 * 2 - t3.get_height() / 2
        sc.blit(t3, (round(x), round(y)))
        ############################
        if d['procents']:
            f = pygame.font.SysFont('arial', d['procent_size'])
            for i in range(11):
                t = f.render(str((10 - i) * 10), 1, (0, 0, 0))
                w = t.get_width()
                h = t.get_height()
                x = size / 2 + a * (-i + 5) / 10 - w / 2
                y = size / 2 + med / 3 + h / 10
                sc.blit(t, (x, y))
            for i in range(11):
                t = f.render(str((10 - i) * 10), 1, (0, 0, 0))
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
                t = f.render(str((i) * 10), 1, (0, 0, 0))
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
        if sr > 1:
            1 == 1
        pygame.draw.line(sc, (0, 0, 0), pointa, pointb, sr)
        pygame.draw.line(sc, (0, 0, 0), pointa, pointc, sr)
        pygame.draw.line(sc, (0, 0, 0), pointc, pointb, sr)
        if d['net']:
            net_col = (200, 200, 200)
            for i in range(9):
                pygame.draw.line(sc, net_col, (size / 2 - a / 2 + (1 + i) * a / 10, size / 2 + med / 3),
                                 (size / 2 + a / 2 - 1 / 2 * (9 - i) * a / 10,
                                  size / 2 + med / 3 - (9 - i) / 10 * a * (3 ** 0.5 / 2)), sr)
                pygame.draw.line(sc, net_col, (size / 2 - a / 2 + (1 + i) * a / 10, size / 2 + med / 3),
                                 (size / 2 - a / 2 + 1 / 2 * (1 + i) * a / 10,
                                  size / 2 + med / 3 - (i + 1) / 10 * a * (3 ** 0.5 / 2)), sr)
                pygame.draw.line(sc, net_col, (
                size / 2 - 1 / 2 * a * (i + 1) / 10, size / 2 - med / 3 * 2 + (3 ** 0.5 / 2) * a * (i + 1) / 10),
                                 (size / 2 + 1 / 2 * a * (i + 1) / 10,
                                  size / 2 - med / 3 * 2 + (3 ** 0.5 / 2) * a * (i + 1) / 10), sr)
        if mods[0]:
            pygame.draw.line(sc, (0, 0, 0), (size / 2, size / 2), (size / 2, size / 2 + med / 3), sr * 3)
            pygame.draw.line(sc, (0, 0, 0), (size / 2, size / 2), (size / 2 - a / 4, size / 2 - med / 6), sr * 3)
            pygame.draw.line(sc, (0, 0, 0), (size / 2, size / 2), (size / 2 + a / 4, size / 2 - med / 6), sr * 3)
        if mods[1]:
            pygame.draw.line(sc, (0, 0, 0), (size / 2, size / 2 - med / 3 * 2), (size / 2, size / 2 + med / 3), sr * 3)
            pygame.draw.line(sc, (0, 0, 0), (size / 2 - a / 4, size / 2 - med / 6), (size / 2 + a / 4, size / 2 - med / 6), sr * 3)
        if mods[2]:
            pygame.draw.line(sc, (0, 0, 0), (size / 2 - a / 4, size / 2 - med / 6), (size / 2 + a / 4, size / 2 - med / 6), sr * 3)
            pygame.draw.line(sc, (0, 0, 0), (size / 2, size / 2 - med / 6), (size / 2, size / 2 + med / 3), sr * 3)
            pygame.draw.line(sc, (0, 0, 0), (size / 2 - a / 8 * 3, size / 2 + med / 12), (size / 2 + a / 8 * 3, size / 2 + med / 12), sr * 3)
            pygame.draw.line(sc, (0, 0, 0), (size / 2 - a / 4, size / 2 + med / 3), (size / 2 - a / 8, size / 2 + med / 12), sr * 3)
            pygame.draw.line(sc, (0, 0, 0), (size / 2 + a / 4, size / 2 + med / 3), (size / 2 + a / 8, size / 2 + med / 12), sr * 3)
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
                if c1 < 0:
                    continue
            else:
                try:
                    c1 = float(point[2])
                except:
                    continue
                if a1 + b1 + c1 == 0:
                    continue
                a1, b1, c1 = a1 * 100 / (a1 + b1 + c1), b1 * 100 / (a1 + b1 + c1), c1 * 100 / (a1 + b1 + c1)
            # координаты точки
            #k1 = b1 / a1
            #k2 = b1 / c1
            if b1 == 0:
                b1 = 0.001
            if a1 == 0:
                a1 = 0.001
            y = size / 2 + med / 3
            x = size / 2 - a / 2 + a / 100 * b1
            if c1 != 0:
                k1 = c1 / a1
                k2 = c1 / b1
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