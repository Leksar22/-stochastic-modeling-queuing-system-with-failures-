import sys
from PyQt5 import uic, QtCore, QtGui, QtWidgets
import numpy as np


class MyApp(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        # super().__init__()
        self.ui = uic.loadUi('smo1.ui', self)
        self.stations = [self.ui.label_1, self.ui.label_2, self.ui.label_3, self.ui.label_4, self.ui.label_5,
                         self.ui.label_6, self.ui.label_7, self.ui.label_8, self.ui.label_9, self.ui.label_10,
                         self.ui.label_11, self.ui.label_12, self.ui.label_13, self.ui.label_14, self.ui.label_15,
                         self.ui.label_16, self.ui.label_17, self.ui.label_18, self.ui.label_19, self.ui.label_20]

        self.ui.verticalSlider.valueChanged.connect(self.change_speed)
        self.ui.label_speed.setText('Скорость: 1000')
        self.ui.verticalSlider.setEnabled(False)


        self.ui.pushButton_reset.clicked.connect(self.start)
        self.L = 10  # плотность, заявок/мин
        self.n = len(self.stations)  # число каналов
        
        self.curr_time = None  # время работы системы (сумма всех dt)
        self.dt = None  # интервал поступления заявки
        self.w = None  # счетчик отклоненных заявок
        self.timer = None  # вызывает функцию с определенной периодичностью

    def change_speed(self):
        self.timer.setInterval(self.ui.verticalSlider.value())
        self.ui.label_speed.setText('Скорость: ' + str(self.ui.verticalSlider.value()))

    def start(self):
        if self.timer:
            self.timer.stop()
            self.timer.deleteLater()
        
        self.ui.verticalSlider.setEnabled(True)

        self.w = 0
        self.dt = -np.log(1 - np.random.rand()) / self.L
        self.curr_time = QtCore.QTime(0, 0, 0)
        
        for i in self.stations:  # инициализация каналов, изначально все свободные
            i.busy_time = 0
            i.color = 'green'  # green ~ свободно
            i.setStyleSheet(f"background-color: green")


        self.timer = QtCore.QTimer()  # вызывает функцию с определенной периодичностью
        self.timer.start(1000)
        self.timer.setInterval(self.ui.verticalSlider.value())
        self.timer.timeout.connect(self.simulate)

        self.ui.label_cnt_rej_app.setText('0')
        self.ui.label_cnt_timestamp.setText(self.curr_time.toString("hh:mm:ss"))
        self.ui.label_cnt_active_app.setText('0')




    def simulate(self):
        self.ui.label_cnt_rej_app.setText(str(self.w))

        free_channels = [i for i in range(self.n) if self.stations[i].busy_time <= self.dt]  # номера свободных каналов
        busy_channels = [i for i in range(self.n) if self.stations[i].busy_time > self.dt]  # номера занятых каналов
        for i in free_channels:  # меняем цвет свободных каналов на зеленый
            self.ui.stations[i].color = 'green'
        for i in busy_channels:  # меняем цвет занятых каналов на красный
            self.ui.stations[i].color = 'red'

        if len(free_channels) == 0:  # если нет свободных каналов осуществляем отказ
            self.w += 1
        else:  # если свободные каналы есть обрабатываем заявку


            for i in busy_channels:  # вычитаем время обслуживания следующей заявки из всех активных
                self.ui.stations[i].busy_time -= self.dt
                self.ui.stations[i].color = 'red'

            ind = free_channels.pop(0)  # удаляем первый свободный канал, храним номер этого канала в ind
            self.ui.stations[ind].busy_time = np.random.uniform(0.01, 2)  # создание новой заявки
            self.ui.stations[ind].color = 'red'  # канал занят, ставим красный цвет
            busy_channels.append(ind)

            for i in range(self.n):  # выставляем цвета в ui согласно атрибуту .color
                self.ui.stations[i].setStyleSheet(f"background-color: {self.ui.stations[i].color}")

            self.curr_time = self.curr_time.addSecs(self.dt * 60)
            self.ui.label_cnt_timestamp.setText(self.curr_time.toString("hh:mm:ss"))
            self.ui.label_cnt_active_app.setText(str(len(busy_channels)))

            print('Такт!')
            print('Занято каналов:', len(busy_channels), 'Номера этих каналов:', end=' ')
            print(*[i + 1 for i in busy_channels], end='\n\n')

        self.dt = -np.log(1 - np.random.rand()) / self.L  # каждый такт таймера генерируем время следующей заявки


if __name__ == "__main__":
    # create app
    app = QtWidgets.QApplication(sys.argv)

    # init
    MainWindow = MyApp()
    MainWindow.show()

    #mainloop
    sys.exit(app.exec_())


