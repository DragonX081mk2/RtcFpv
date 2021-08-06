from socket import socket
from abc import ABCMeta,abstractmethod

MAX_UDP_PACKET = 1500

class Packet(metaclass=ABCMeta):
    TYPE_CTRL = 0
    TYPE_VIDEO = 1

    @abstractmethod
    def data(self) -> bytes:
        pass

    @abstractmethod
    def get_type(self):
        pass

class Connection(metaclass=ABCMeta):
    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def send(self,packet:Packet):
        pass

