import ipaddress

from random import randint, choice


def getRandomNames(num):
    if num <= 0:
        raise ValueError
    elif num > 26:
        return ["RT" + str(i) for i in [j for j in range(0, num)]]
    elif num <= 26:
        return ["RT" + elem for elem in ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
               "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]]


def getUniqueIP(list_ip, start_cidr, end_cidr, simple_cidr, two_ip=False):
    getRandomIP = lambda num=255: "{0!s}.{1!s}.{2!s}.{3!s}".format(randint(1, 255), randint(0, 255), randint(0, 255),
                                                                   randint(0, num))
    getRandomCIDR = lambda start, end, simple: choice(["8", "16", "24"]) if simple else str(randint(start, end))

    def ip_is_correct(address):
        net = ipaddress.IPv4Network(address, False)
        if str(net.broadcast_address) + "/" + address.split("/")[1] == address:
            return False
        try:
            ipaddress.ip_network(address)
            return False
        except ValueError:
            return True

    if not two_ip:
        while True:
            ip, cidr = getRandomIP(), getRandomCIDR(start_cidr, end_cidr, simple_cidr)
            s = ip + "/" + cidr

            if list_ip.count(ip) == 0 and ip_is_correct(s):
                list_ip.append(ip)
                return s
    else:
        while True:
            ip1, cidr = getRandomIP(254), getRandomCIDR(start_cidr, end_cidr, simple_cidr)
            arr = ip1.split('.')
            arr[len(arr) - 1] = str(int(arr[len(arr) - 1]) + 1)
            ip2 = '.'.join(arr)

            s1, s2 = ip1 + "/" + cidr, ip2 + "/" + cidr
            if list_ip.count(ip1) == 0 and list_ip.count(ip2) == 0 and ip_is_correct(s1) and ip_is_correct(s2):
                list_ip.append(ip1)
                list_ip.append(ip2)
                return s1, s2
