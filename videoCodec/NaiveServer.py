import socket

"""
NAIVE TRANSMISSION PROTOCOL: UDP
HEADER: 1 byte
0 :1 bit CAMERA: 0 monitor,1 camera
1 :1 bit CTRL: 0 data pack, 1 CTRL pack
2-3: 2bit TYPE: 0 Connect 1 Disconnect 2 HeartBeat 3 <NOT DEFINED>
....



"""

PORT = 12360
LOCALHOST = ""
LISTEN_NUM = 5
MAX_PACKET = 1500

PACK_TYPE_CONNECT = 0
PACK_TYPE_DISCONNECT = 1
PACK_TYPE_HEARTBEAT = 2
PACK_TYPE_DATACHANNEL = 3


class NaiveServer():
    def __init__(self):
        self.src = None
        self.dst = None

    def start(self):
        print("Start Listening at Port : {} ...".format(PORT))
        self.listenSocket = self.init_socket()
        while True:
            try:
                packet,pack_src = self.listenSocket.recvfrom(MAX_PACKET)
            except:
                continue
            if is_from_camera(packet):
                # print("get camera packet from {}".format(pack_src))
                if is_ctrl_pack(packet):
                    pack_type = get_packet_type(packet)
                    print("get control packet from camera from {},now src {},dst {}".format(pack_src,self.src,self.dst))
                    if pack_type == PACK_TYPE_CONNECT:
                        self.src = pack_src
                        self.listenSocket.sendto(b'\x80',pack_src)
                        continue
                    if pack_type == PACK_TYPE_DISCONNECT:
                        self.src = None
                        continue
                    if pack_type == PACK_TYPE_HEARTBEAT:
                        self.src = pack_src
                        continue
                    if pack_type == PACK_TYPE_DATACHANNEL:
                        if self.dst:
                            self.listenSocket.sendto(packet,self.dst)
                    else:
                        continue
                else:
                    # print("get data packet from camera")
                    #not ctrl packet
                    self.src = pack_src
                    if self.dst is not None:
                        # print("{} send to {}".format(self.src,self.dst))
                        self.listenSocket.sendto(packet,self.dst)
            else:
                # from monitor
                if is_ctrl_pack(packet):
                    #is ctrl pack
                    print("get control packet from monitor from {} now src {},dst {}".format(pack_src,self.src,self.dst))
                    pack_type = get_packet_type(packet)
                    if pack_type == PACK_TYPE_CONNECT:
                        self.dst = pack_src
                        self.listenSocket.sendto(b'\x80',pack_src)
                        continue
                    if pack_type == PACK_TYPE_DISCONNECT:
                        self.dst = None
                        continue
                    if pack_type == PACK_TYPE_HEARTBEAT:
                        continue
                    if pack_type == PACK_TYPE_DATACHANNEL:
                        print("get monitor dc")
                        if self.src:
                            self.listenSocket.sendto(packet,self.src)
                    else:
                        continue
                else:
                    #not ctrl pack
                    continue


    def init_socket(self)->socket.socket:
        udp_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp_socket.bind((LOCALHOST,PORT))
        return udp_socket

def is_ctrl_pack(packet:bytes):
    header = packet[0]
    ctrl_flag = bool((header & 0x40)>>6)
    return ctrl_flag

def is_from_camera(packet:bytes):
    header = packet[0]
    cam_flag = bool((header & 0x80)>>7)
    return cam_flag

def get_packet_type(packet:bytes):
    header = packet[0]
    type_flag = int((header & 0x30)>>4)
    return type_flag



if __name__ == "__main__":
    server = NaiveServer()
    server.start()
