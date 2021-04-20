import random
import math

from PyQt5.QtCore import QPoint


class Node:
    def __init__(self, point, obj):  # 0 - маршрутизатор 1 - облако 2 - сервер
        self.position = point
        self.obj = obj


def conversion_edges_to_QPoint(edges, dev):
    return [(QPoint(edge[0][0] + dev, edge[0][1] + dev), QPoint(edge[1][0] + dev, edge[1][1] + dev)) for edge in edges]


def factorization(num):
    i = 2
    prime_factors = []
    while num != 1:
        if num % i == 0:
            num = num // i
            prime_factors.append(i)
            i = 1
        i += 1
    return prime_factors


def getPointDist(line, distance):
    len_vector = math.sqrt(line.dx() ** 2 + line.dy() ** 2)
    return QPoint(line.p1().x() + distance * line.dx() / len_vector, line.p1().y() + distance * line.dy() / len_vector)


def get_arr_valid_points(x, y, length):
    return [(x - length, y), (x, y - length), (x - length, y - length), (x + length, y), (x, y + length),
            (x + length, y + length), (x + length, y - length), (x - length, y + length)]


def isCloudsHaveRouter(list_clouds, list_points_routers, length):
    list_tmp = list(list_clouds)
    for cloud in list_clouds:
        for elem in get_arr_valid_points(cloud.position.x(), cloud.position.y(), length):
            if elem in list_points_routers:
                list_tmp.remove(cloud)
                break
            else:
                continue
    return True if len(list_tmp) == 0 else False


def getRouterConnections(list_points_routes, length):
    list_edges = list()
    list_tmp = list(list_points_routes)
    stack = [list_points_routes[0]]

    for point in stack:
        list_tmp.remove(point)
        for elem in get_arr_valid_points(point[0], point[1], length):
            if elem in list_tmp:
                list_edges.append([point, elem])
                stack.append(elem)
                break
            else:
                continue

    if len(list_tmp) == 0:
        return list_edges

    while len(list_tmp) != 0 and len(stack) != 0:
        x, y = stack.pop()
        for elem in get_arr_valid_points(x, y, length):
            if elem in list_tmp:
                list_edges.append([(x, y), elem])
                list_tmp.remove(elem)
                stack.append(elem)
            else:
                continue

    return list() if len(list_tmp) != 0 else list_edges


def getObjects(n_routers, n_clouds, n_server):
    list_objects = []
    n_objects = n_routers + n_clouds + n_server
    while len(list_objects) != n_objects:
        i = random.randint(0, 2)
        if (i == 0 and n_routers == 0) or (i == 1 and n_clouds == 0) or (i == 2 and n_server == 0):
            continue
        if i == 0:
            n_routers -= 1
        elif i == 1:
            n_clouds -= 1
        else:
            n_server -= 1
        list_objects.append(i)
    return list_objects


def getNumCloudConnections(router, list_edges_clouds):
    num = 0
    for edge in list_edges_clouds:
        if router in edge:
            num += 1
    return num


isConnect = lambda: True if random.randint(0, 1) == 1 else False
