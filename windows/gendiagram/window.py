import resources

from PyQt5.QtGui import QPainter, QPen, QPixmap, QPalette, QColor, QFont
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QGridLayout, QScrollArea, QVBoxLayout, QFileDialog, \
    QCheckBox, QSpinBox, QApplication, QMessageBox, QHBoxLayout, QFontDialog
from PyQt5.QtCore import Qt, QLine, pyqtSignal
from config import *
from supporting.graph import *
from supporting.generate import *
from windows.gendiagram.config import *


class ModalWindow(QWidget):
    def __init__(self, n_routers, n_clouds, n_servers, n, m, start_cidr, end_cidr,
                 font, simple_cidr, cisco_icons, parent=None):
        QWidget.__init__(self, parent)
        palette = QPalette()
        palette.setColor(QPalette.Background, QColor("#fff"))
        self.setPalette(palette)
        self.font = font

        n_objects = n_routers + n_clouds + n_servers
        if n_objects == 0:
            return
        elif n_routers == 0:
            QMessageBox.critical(None, TITLE_MESSAGE_ERROR, MESSAGE_ERROR_NOT_POSSIBLE_BUILD_DIAGRAM, QMessageBox.Ok)
            return

        x, y = START_POINT
        points = list()
        for i in range(1, n_objects + 1):
            points.append(QPoint(x, y))
            if i % m == 0:
                x += LENGTH_LINE
                y = START_POINT[1]
            else:
                y += LENGTH_LINE

        list_nodes, list_routes, list_points_routes, self.list_edges_routers, self.list_edges_clouds = (
            [] for _ in range(0, 5))

        flag = False
        num_iterations = NUM_ITERATIONS
        while num_iterations != 0 and (len(self.list_edges_routers) == 0 or not flag):
            list_nodes = [Node(points[i], obj) for i, obj in enumerate(
                getObjects(n_routers, n_clouds, n_servers))]

            list_routes = [node for node in list_nodes if node.obj == 0]

            list_points_routes = [(elem.position.x(), elem.position.y()) for elem in list_routes]

            flag = isCloudsHaveRouter([node for node in list_nodes if node not in list_routes],
                                      list_points_routes, LENGTH_LINE)

            self.list_edges_routers = getRouterConnections(list_points_routes, LENGTH_LINE)

            if len(self.list_edges_routers) == 0 and n_routers == 1 and flag:
                break

            num_iterations -= 1

        if num_iterations == 0 and not flag:
            QMessageBox.critical(None, TITLE_MESSAGE_ERROR, MESSAGE_ERROR_NOT_POSSIBLE_BUILD_DIAGRAM, QMessageBox.Ok)
            return

        for node in list_nodes:
            point = (node.position.x(), node.position.y())
            if node.obj == 0:
                list_tmp = [elem for elem in list_points_routes if [elem, point] not in self.list_edges_routers
                            and [point, elem] not in self.list_edges_routers and elem
                            in get_arr_valid_points(point[0], point[1], LENGTH_LINE)]
                for elem in list_tmp:
                    if isConnect():
                        self.list_edges_routers.append([point, elem])
            else:
                list_tmp = [elem for elem in list_routes if (elem.position.x(), elem.position.y()) in
                            get_arr_valid_points(point[0], point[1], LENGTH_LINE)]

                list_connection = [getNumCloudConnections(elem, self.list_edges_clouds) for elem in list_tmp]
                min_num_connections = min(list_connection)
                i = random.choice([list_connection.index(elem) for elem in list_connection
                                   if elem == min_num_connections])

                self.list_edges_clouds.append([point, (list_tmp[i].position.x(), list_tmp[i].position.y())])

        pixmap_router, pixmap_cloud, pixmap_server = (QPixmap(ICON_ROUTER), QPixmap(ICON_CLOUD),
            QPixmap(ICON_FILE_SERVER)) if not cisco_icons else (QPixmap(CISCO_ICON_ROUTER), QPixmap(CISCO_ICON_CLOUD),
                                                            QPixmap(CISCO_ICON_FILE_SERVER))

        labels = [QLabel(self) for _ in list_nodes]

        for i, node in enumerate(list_nodes):
            if node.obj == 0:
                labels[i].setPixmap(pixmap_router)
            elif node.obj == 1:
                labels[i].setPixmap(pixmap_cloud)
            else:
                labels[i].setPixmap(pixmap_server)
            labels[i].move(node.position)

        self.list_edges_routers, self.list_edges_clouds = conversion_edges_to_QPoint(self.list_edges_routers,
                                DEV_START_POINT), conversion_edges_to_QPoint(self.list_edges_clouds, DEV_START_POINT)

        self.list_lines, self.list_str_placement, list_ip = (list() for _ in range(0, 3))
        for edge in self.list_edges_clouds:
            point1, point2 = edge[0], edge[1]
            line = QLine(point2, point1)
            ip = getUniqueIP(list_ip, start_cidr, end_cidr, simple_cidr)

            if point1.y() == point2.y():
                label = QLabel(ip, self)
                label.setFont(font)
                point = getPointDist(QLine(point2, point1), DEV_START_POINT)

                if point1.x() > point2.x():
                    point = QPoint(point.x() + 10, point.y() - 28)
                else:
                    point = QPoint(point.x() - 230, point.y() - 28)

                label.move(point)
            elif point1.x() == point2.x():
                if point2.y() > point1.y():
                    point = getPointDist(QLine(point2, point1), DEV_START_POINT + 250)
                    self.list_str_placement.append((QPoint(point.x() - 24, point.y()), ip, 90))
                else:
                    point = getPointDist(QLine(point2, point1), DEV_START_POINT)
                    self.list_str_placement.append((QPoint(point.x() + 9, point.y()), ip, 90))
            elif abs(line.dx()) == LENGTH_LINE and abs(line.dy()) == LENGTH_LINE:
                if line.dx() == LENGTH_LINE:
                    point = getPointDist(line, DEV_START_POINT + 5)
                    self.list_str_placement.append((QPoint(point.x() if line.dy() == LENGTH_LINE else point.x() + 15,
                        point.y() - 10 if line.dy() == LENGTH_LINE else point.y() + 15), ip, 45 if
                        line.dy() == LENGTH_LINE else -45))
                else:
                    point = getPointDist(line, DEV_START_POINT + 240)
                    self.list_str_placement.append((QPoint(point.x(), point.y() - 10), ip,
                                                    45 if line.dy() == -LENGTH_LINE else -45))

        for edge in self.list_edges_routers:
            point1, point2 = edge[0], edge[1]
            line = QLine(point1, point2)

            ip1, ip2 = getUniqueIP(list_ip, start_cidr, end_cidr, simple_cidr, True)

            if point1.y() == point2.y():
                label1 = QLabel(ip1, self)
                label1.setFont(font)
                label2 = QLabel(ip2, self)
                label2.setFont(font)

                if point1.x() > point2.x():
                    point1, point2 = point2, point1

                point = getPointDist(QLine(point1, point2), DEV_START_POINT)
                label1.move(point.x() + 10, point.y() - 28)
                point = getPointDist(QLine(point2, point1), DEV_START_POINT)
                label2.move(point.x() - 240, point.y() + 2)
            elif point1.x() == point2.x():
                if point1.y() > point2.y():
                    point1, point2 = point2, point1

                point = getPointDist(QLine(point1, point2), DEV_START_POINT)
                self.list_str_placement.append((QPoint(point.x() + 9, point.y()), ip1, 90))
                point = getPointDist(QLine(point2, point1), DEV_START_POINT + 250)
                self.list_str_placement.append((QPoint(point.x() - 24, point.y()), ip2, 90))
            elif abs(line.dx()) == LENGTH_LINE and abs(line.dy()) == LENGTH_LINE:
                if (line.dx() == LENGTH_LINE and line.dy() == LENGTH_LINE) or (line.dx() == -LENGTH_LINE
                                                                               and line.dy() == -LENGTH_LINE):
                    if point1.y() > point2.y():
                        point1, point2 = point2, point1

                    point = getPointDist(QLine(point1, point2), DEV_START_POINT)
                    self.list_str_placement.append((QPoint(point.x() + 3, point.y() - 10), ip1, 45))
                    point = getPointDist(QLine(point2, point1), DEV_START_POINT + 240)
                    self.list_str_placement.append((QPoint(point.x() - 15, point.y() + 15), ip2, 45))
                else:
                    if point1.y() < point2.y():
                        point1, point2 = point2, point1
                    point = getPointDist(QLine(point1, point2), DEV_START_POINT + 10)
                    self.list_str_placement.append((QPoint(point.x() + 15, point.y() + 15), ip1, -45))
                    point = getPointDist(QLine(point2, point1), DEV_START_POINT + 230)
                    self.list_str_placement.append((QPoint(point.x() - 5, point.y() - 8), ip2, -45))

        names = getRandomNames(len(list_routes))
        for i, router in enumerate(list_routes):
            label = QLabel("<b>{0}</b>".format(names[i]), self)
            label.setFont(self.font)
            point_start = QPoint(router.position.x() + DEV_START_POINT, router.position.y() + DEV_START_POINT)
            point_end = QPoint(point_start.x() + 15, point_start.y() + DEV_START_POINT - 135)
            label.move(point_end.x(), point_end.y() - 20)
            self.list_lines.append(QLine(point_start, point_end))

        self.setGeometry(0, 0, (n - 1) * LENGTH_LINE + 300 + START_POINT[0],
                         (m - 1) * LENGTH_LINE + 150 + START_POINT[1])

    def paintEvent(self, event):
        painter = QPainter(self)

        pen = QPen(Qt.black, LINE_WIDTH)
        painter.setPen(pen)

        for edge in self.list_edges_routers + self.list_edges_clouds:
            painter.drawLine(QLine(edge[0], edge[1]))

        for arr in self.list_str_placement:
            painter.save()
            painter.setFont(self.font)
            painter.translate(arr[0])
            painter.rotate(arr[2])
            painter.drawText(QPoint(0, 0), arr[1])
            painter.restore()

        pen = QPen(Qt.DashLine)
        pen.setWidth(DASHED_LINE_WIDTH)
        painter.setPen(pen)
        for line in self.list_lines:
            painter.drawLine(line)


class GenerateDiagramWindow(QWidget):
    switch_window = pyqtSignal(str)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent, Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle(APP_NAME)
        self.resize(*GEOMETRY)
        desktop = QApplication.desktop()
        self.move((desktop.width() - self.width()) // 2, (desktop.height() - self.height()) // 2)

        btn_back = QPushButton(NAME_BTN_BACK)
        btn_back.clicked.connect(self.back)

        btn_generate = QPushButton(NAME_BTN_GENERATE)
        btn_generate.clicked.connect(self.generate_diagram)

        btn_choose_font = QPushButton(NAME_BTN_CHOOSE_FONT)
        btn_choose_font.clicked.connect(self.choose_font)
        self.font = QFont(NAME_FONT, pointSize=SIZE_FONT, weight=99)

        labels = [QLabel(name) for name in LABELS_NAMES]

        self.edits = [QSpinBox() for _ in range(0, 7)]
        self.edits.append(QCheckBox())
        self.edits.append(QCheckBox())

        self.grid = QGridLayout()
        for i in range(0, 3):
            self.grid.addWidget(labels[i], i, 0)
            self.grid.addWidget(self.edits[i], i, 1)

        self.grid.addWidget(labels[3], 3, 0)
        layout = QHBoxLayout()
        layout.addWidget(self.edits[3])
        layout.addWidget(self.edits[4])
        self.grid.addLayout(layout, 3, 1)

        self.grid.addWidget(labels[4], 4, 0)
        layouts = QHBoxLayout()
        layouts.addWidget(self.edits[5])
        layouts.addWidget(self.edits[6])
        self.grid.addLayout(layouts, 4, 1)

        for i, widgets in enumerate([(labels[5], self.edits[7]), (labels[6], self.edits[8]),
                                     (labels[7], btn_choose_font), (btn_back, btn_generate)], 5):
            self.grid.addWidget(widgets[0], i, 0)
            self.grid.addWidget(widgets[1], i, 1)
        self.setLayout(self.grid)

    def generate_diagram(self):
        func = lambda check_box: False if check_box.checkState() == 0 else True
        n_routers, n_clouds, n_servers, n, m, start_cidr, end_cidr = [self.edits[i].value() for i in range(0, 7)]
        simple_cidr, cisco_icons = func(self.edits[7]), func(self.edits[8])

        if n_clouds + n_servers + n_routers > (n * m):
            QMessageBox.critical(None, TITLE_MESSAGE_ERROR, MESSAGE_ERROR_BIG_NUM_OBJECT, QMessageBox.Ok)
            return

        if not simple_cidr and (start_cidr >= end_cidr or end_cidr > 32):
            QMessageBox.critical(None, TITLE_MESSAGE_ERROR, MESSAGE_ERROR_INVALID_MASK, QMessageBox.Ok)
            return

        modal_window = ModalWindow(n_routers, n_clouds, n_servers, n, m, start_cidr, end_cidr, self.font, simple_cidr,
                                   cisco_icons)

        window = QWidget(self, Qt.Window)
        window.setWindowTitle(APP_NAME)
        window.resize(*GEOMETRY_WINDOW_MODAL)
        window.setWindowModality(Qt.WindowModal)
        desktop = QApplication.desktop()
        window.move((desktop.width() - window.width()) // 2, (desktop.height() - window.height()) // 2)

        scroll = QScrollArea(window)
        palette = QPalette()
        palette.setColor(QPalette.Background, QColor("#fff"))
        scroll.setPalette(palette)
        scroll.setWidget(modal_window)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        btn_save = QPushButton(NAME_BTN_SAVE)
        btn_save.clicked.connect(lambda: self.save_image(modal_window))

        vbox = QVBoxLayout()
        vbox.addWidget(btn_save, alignment=Qt.AlignLeft)
        vbox.addWidget(scroll)

        window.setLayout(vbox)
        window.show()

    def back(self):
        self.switch_window.emit("main<generate_diagram")

    def choose_font(self):
        font, ok = QFontDialog.getFont(self.font)
        if ok:
            self.font = font
            QMessageBox.information(self, TITLE_MESSAGE_INFORMATION, MESSAGE_INFORMATION_FONT_INSTALLED, QMessageBox.Ok)

    def save_image(self, widget):
        arr = QFileDialog.getSaveFileName(filter="Images (*.png *.jpg)")

        if arr[0] == "":
            return

        extension = arr[0][arr[0].rfind(".") + 1:]
        if extension in ["png", "jpg"]:
            widget.grab().save(arr[0], extension)
        else:
            QMessageBox.critical(self, TITLE_MESSAGE_ERROR, MESSAGE_ERROR_CANNOT_SAVE_FILE + extension,
                                 QMessageBox.Ok)
