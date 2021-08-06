from videoCodec.h264 import H264Decoder,H264Encoder
from queue import Queue
from videoCodec.connection import Connection,Packet,MAX_UDP_PACKET
import socket
from threading import Thread,Lock
import time
import videoCodec.NaiveVideoTransmissionProtocol as trans_protocol
from videoCodec import configs
import traceback

CONNECTION_MODE_CONTROLLER = 0
CONNECTION_MODE_FPV = 1

class VideoPacket(Packet):
    def __init__(self,data:bytes):
        self._data = data
        self._type = Packet.TYPE_VIDEO

    def data(self) -> bytes:
        return self._data

    def get_type(self):
        return self._type

class CTRLPacket(Packet):
    def __init__(self,data:bytes):
        self._data = data
        self._type = Packet.TYPE_CTRL

    def data(self) -> bytes:
        return self._data

    def get_type(self):
        return self._type

'''
VideoConnection:
send/recv video packet / ctrl packet

'''
class VideoConnection(Connection):
    def __init__(self,udp_socket:socket.socket = None,
                 recv_video_packet_buffer:Queue = Queue(),
                 recv_ctrl_packet_buffer:Queue = Queue(),
                 mode:str=CONNECTION_MODE_CONTROLLER):
        self._udpSocket = udp_socket
        self._recv_ctrl_packet_buffer = recv_ctrl_packet_buffer
        self._recv_video_buffer = recv_video_packet_buffer
        self._send_packet_buffer = Queue()
        self._running = True
        assert mode in [CONNECTION_MODE_CONTROLLER,CONNECTION_MODE_FPV],"Mode:{} not available".format(mode)
        self.mode = mode

    def start(self) -> None:
        recv_target = self.videoConnectionClientReceiveWorker
        send_target = self.videoConnectionClientSendWorker
        if self.mode == CONNECTION_MODE_FPV:
            send_target = self.videoConnectionFPVSendWorker
            recv_target = self.videoConnectionFPVReceiveWorker
        self._thread_recv_conn = Thread(target=recv_target,
                              args= [])

        self._thread_send_conn = Thread(target=send_target,
                                        args = [])

        self._thread_hb = Thread(target=self.heartbeat_worker,
                              args= ())

        self._thread_recv_conn.start()
        self._thread_send_conn.start()
        self._thread_hb.start()

    def stop(self):
        self._running = False
        self._recv_ctrl_packet_buffer.put(CTRLPacket(b''))
        self._recv_video_buffer.put(VideoPacket(b''))

    def send(self,packet:Packet):
        self._send_packet_buffer.put(packet)

    def videoConnectionClientReceiveWorker(self)->None:
        while self._running:
            try:
                packet,recv_addr = self._udpSocket.recvfrom(MAX_UDP_PACKET)
            except:
                continue
            # print("receiver worker get data")
            # print("packet len: ",len(packet))
            if trans_protocol.is_ctrl_pack(packet):
                if trans_protocol.is_data_channel_pack(packet):
                    packet = trans_protocol.parse_packet(packet)
                    self._recv_ctrl_packet_buffer.put(CTRLPacket(packet))
            else:
                packet = trans_protocol.parse_packet(packet)
                self._recv_video_buffer.put(VideoPacket(packet))

    def videoConnectionClientSendWorker(self)->None:
        while self._running:
            try:
                packet = self._send_packet_buffer.get_nowait()
            except:
                time.sleep(0.001)
                continue

            try:
                if packet.get_type() == Packet.TYPE_CTRL:
                    packet = trans_protocol.gen_ctrl_data_channel_pack(packet.data(),False)
                elif packet.get_type == Packet.TYPE_VIDEO:
                    packet = trans_protocol.gen_video_data_pack(packet.data(),False)
            except:
                print(traceback.print_exc())
                continue

            self._udpSocket.sendto(packet, (configs.SERVER_IP, configs.SERVER_VIDEO_PORT))

    def videoConnectionFPVSendWorker(self)->None:
        while self._running:
            try:
                packet = self._send_packet_buffer.get_nowait()
            except:
                time.sleep(0.001)
                continue

            try:
                if packet.get_type() == Packet.TYPE_CTRL:
                    packet = trans_protocol.gen_ctrl_data_channel_pack(packet.data())
                elif packet.get_type() == Packet.TYPE_VIDEO:
                    packet = trans_protocol.gen_video_data_pack(packet.data())
            except:
                print(traceback.print_exc())
                continue

            self._udpSocket.sendto(packet,(configs.SERVER_IP,configs.SERVER_VIDEO_PORT))

    def videoConnectionFPVReceiveWorker(self) -> None:
        while self._running:
            try:
                packet, recv_addr = self._udpSocket.recvfrom(MAX_UDP_PACKET)
            except:
                continue
            # print("receiver worker get data")
            # print("packet len: ",len(packet))
            if trans_protocol.is_ctrl_pack(packet):
                print("get ctrl pack")
                if trans_protocol.is_data_channel_pack(packet):
                    print("get dc pack")
                    packet = trans_protocol.parse_packet(packet)
                    self._recv_ctrl_packet_buffer.put(CTRLPacket(packet))
            else:
                packet = trans_protocol.parse_packet(packet)
                self._recv_video_buffer.put(VideoPacket(packet))

    def heartbeat_worker(self)->None:
        while self._running:
            self._udpSocket.sendto(trans_protocol.gen_heartbeat_pack(self.mode==CONNECTION_MODE_FPV),(configs.SERVER_IP,configs.SERVER_VIDEO_PORT))
            time.sleep(1)
"""
Singleton: make sure there is only one video related socket
"""
class VideoTransporter():
    # Status1: Root

    # Status2 Resource Ready
    # Enter: init udp socket and resources
    # Quit: Destroy socket and resources 2.close udp port

    # 3. Video Standby: to receive Video
    # Entre: 1. open socket 2. Connect server and check connection
    # Quit:  2. try disconnect server
    class Status():
        STATUS_ROOT = 0
        STATUS_RESC_READY = 1
        STATUS_STANDBY = 2
        STATUS_NEXT = 'next'
        STATUS_PREV = 'prev'
        def __init__(self,transporter):
            self._status = self.STATUS_ROOT
            self.root_status = self.STATUS_ROOT
            self.final_status = self.STATUS_STANDBY
            self._transporter = transporter

        def enter(self,status):
            if status == self.STATUS_ROOT:
                pass
            elif status == self.STATUS_RESC_READY:
                self._transporter.init_resources()

            elif status == self.STATUS_STANDBY:
                self._transporter.connect()

        def quit(self,status):
            if status == self.STATUS_ROOT:
                pass
            elif status == self.STATUS_RESC_READY:
                self._transporter.destroy_resources()

            elif status == self.STATUS_STANDBY:
                self._transporter.disconnect()

        def go_next(self):
            self.enter(self._status+1)
            self._status = self._status+1

        def go_prev(self):
            self.quit(self._status)
            self._status = self._status - 1

        def to_status(self,dst_status):
            while self._status != dst_status:
                try:
                    if dst_status > self._status:
                        self.go_next()
                    elif dst_status < self._status:
                        self.go_prev()
                except Exception:
                    print(traceback.print_exc())
                    raise Exception


    _instance_lock = Lock()
    def __init__(self,recv_video_packet_buffer:Queue=Queue(),
                 recv_ctrl_packet_buffer:Queue=Queue(),
                 mode:str=CONNECTION_MODE_CONTROLLER):
        self._recv_video_packet_buffer = recv_video_packet_buffer
        self._recv_ctrl_packet_buffer = recv_ctrl_packet_buffer
        self.video_connection = None
        self._status = self.Status(self)
        self.mode = mode


    @classmethod
    def instance(cls,*args,**kwargs):
        with cls._instance_lock:
            if not hasattr(VideoTransporter,"_instance"):
                VideoTransporter._instance = VideoTransporter(*args,**kwargs)
        return VideoTransporter._instance

    def start(self) -> None:
        self._status.to_status(self.Status.STATUS_STANDBY)

    def stop(self):
        self._status.to_status(self.Status.STATUS_ROOT)

    def connect(self)->VideoConnection:
        print("transporter connecting...")
        try:
            self.connect_to_server()
        except:
            raise TimeoutError
        self.video_connection = VideoConnection(self._udp_socket,
                                                recv_video_packet_buffer=self._recv_video_packet_buffer,
                                                recv_ctrl_packet_buffer=self._recv_ctrl_packet_buffer,mode=self.mode)
        self.video_connection.start()
        return self.video_connection

    def disconnect(self)->None:
        if self.video_connection is not None:
            self.video_connection.stop()
            self.video_connection = None

    def send(self,packet:Packet)->None:
        if self.video_connection is not None:
            self.video_connection.send(packet)



    def init_resources(self):
        print("transporter init resources")
        self._udp_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        while not self._recv_ctrl_packet_buffer.empty():
            print(self._recv_ctrl_packet_buffer.empty())
            try:
                self._recv_ctrl_packet_buffer.get_nowait()
            except:
                time.sleep(0.001)

        while not self._recv_video_packet_buffer.empty():
            print(self._recv_video_packet_buffer.empty())
            try:
                self._recv_video_packet_buffer.get_nowait()
            except:
                time.sleep(0.001)

    def destroy_resources(self):
        if self._udp_socket is not None:
            self._udp_socket.close()

        while not self._recv_ctrl_packet_buffer.empty():
            print(self._recv_ctrl_packet_buffer.empty())
            try:
                self._recv_ctrl_packet_buffer.get_nowait()
            except:
                time.sleep(0.001)

        while not self._recv_video_packet_buffer.empty():
            print(self._recv_video_packet_buffer.empty())
            try:
                self._recv_video_packet_buffer.get_nowait()
            except:
                time.sleep(0.001)

    def connect_to_server(self):
        print("transporter connection to server...")
        retry = 5
        self._udp_socket.settimeout(1.5)
        while retry > 0:
            self._udp_socket.sendto(trans_protocol.gen_connect_pack(self.mode==CONNECTION_MODE_FPV),\
                                    (configs.SERVER_IP,configs.SERVER_VIDEO_PORT))
            try:
                ack_packet,ack_from = self._udp_socket.recvfrom(MAX_UDP_PACKET)
                break
            except TimeoutError:
                retry = retry - 1
                print("FAILED TO START VIDEO CONNECTION! RETRY LEFT: {}" .format(retry))
                if retry<=0:
                    print("ERROR: FAILED TO START VIDEO CONNECTION! ")
                    raise  TimeoutError

        self._udp_socket.settimeout(0.01)









