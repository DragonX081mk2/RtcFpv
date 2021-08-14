from videoCodec.h264 import H264Decoder,H264Encoder
from queue import Queue
from videoCodec.connection import Connection,Packet,MAX_UDP_PACKET
import socket
from threading import Thread,Lock
import time
import videoCodec.NaiveVideoTransmissionProtocol as trans_protocol
from videoCodec import configs
import traceback
from helpers.log_statistics import FpvLogStatistic
from multiprocessing import Array,Process,Value
from multiprocessing import Queue as MpQueue

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


def mp_sender_target(mp_running: Value, mp_queue: MpQueue, socket_queue: MpQueue, sent_count: Value,
                     socket_changed: Value):
    socket = None
    while mp_running.value != 0:
        if socket_changed.value != 0:
            socket = socket_queue.get()
            socket_changed.value = 0
        try:
            packets = mp_queue.get_nowait()
        except:
            continue
        # print("mp_packets_len: ",len(packets))
        for packet in packets:
            if socket is not None:
                socket.sendto(packet, (configs.SERVER_IP, configs.SERVER_VIDEO_PORT))
            sent_count.value += 1


class MpUdpSender():
    def __init__(self):
        super(MpUdpSender, self).__init__()
        self.mt_send_queue = Queue()
        self.mp_queue = MpQueue()
        self.log_msg_arr = None
        self.socket_queue = MpQueue()
        self.socket_changed = Value('i', 0)
        self.mp_running = Value('i', 1)
        self.sent_count = Value('i', 1)
        self.thread_running = True
        self.min_sender_time_ms = 15
        self.max_sender_time_ms = 30
        self.mp_worker = Process(target=mp_sender_target, args=(
        self.mp_running, self.mp_queue, self.socket_queue, self.sent_count, self.socket_changed))
        self.mt_sender_worker = Thread(target=self.sender_thread_target, args=[])

    def start(self):
        self.mp_worker.start()
        self.mt_sender_worker.start()

    def stop(self):
        self.mp_running.value = 0
        self.thread_running = False

    def reset_socket(self, socket: socket.socket):
        self.socket_queue.put(socket)
        self.socket_changed.value = 1

    def sender_thread_target(self):
        prev_time = time.time() * 1000
        packets = []
        while self.thread_running:
            try:
                packet = self.mt_send_queue.get_nowait()
            except:
                crt_time = time.time() * 1000
                if crt_time - prev_time < self.min_sender_time_ms:
                    continue
                else:
                    prev_time = crt_time
                    if len(packets) > 0:
                        self.mp_queue.put(packets)
                        # print('mp_queue_size: ',self.mp_queue.qsize())
                    packets = []
                    continue

            crt_time = time.time() * 1000
            packets.append(packet)
            if crt_time - prev_time >= self.max_sender_time_ms:
                if len(packets) > 0:
                    self.mp_queue.put(packets)
                prev_time = crt_time
                packets = []

    def send(self, packet):
        self.mt_send_queue.put(packet)
        # print('mt_queue_len: %s'%self.mt_send_queue.qsize())

    def count_sent(self):
        sent_count = self.sent_count.value
        self.sent_count.value = 0
        return sent_count


'''
VideoConnection:
send/recv video packet / ctrl packet

'''
class VideoConnection(Connection):
    def __init__(self,udp_socket:socket.socket = None,
                 recv_video_packet_buffer:Queue = Queue(),
                 recv_ctrl_packet_buffer:Queue = Queue(),
                 mode:str=CONNECTION_MODE_CONTROLLER,
                 mp_sender:MpUdpSender=None):
        self._udpSocket = udp_socket
        self._recv_ctrl_packet_buffer = recv_ctrl_packet_buffer
        self._recv_video_buffer = recv_video_packet_buffer
        self._send_packet_buffer = Queue()
        self._running = True
        assert mode in [CONNECTION_MODE_CONTROLLER,CONNECTION_MODE_FPV],"Mode:{} not available".format(mode)
        self.mode = mode
        self.mp_sender = mp_sender

    def start(self) -> None:
        recv_target = self.videoConnectionClientReceiveWorker
        send_target = self.videoConnectionClientSendWorker
        if self.mode == CONNECTION_MODE_FPV:
            if self.mp_sender is not None:
                self.mp_sender.reset_socket(self._udpSocket)
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
                # time.sleep(0.001)
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
            time0 = time.time()*1000
            try:
                packet = self._send_packet_buffer.get_nowait()
            except:
                # time.sleep(0.0001)
                continue
            time1 = time.time()*1000

            try:
                if packet.get_type() == Packet.TYPE_CTRL:
                    packet = trans_protocol.gen_ctrl_data_channel_pack(packet.data())
                    FpvLogStatistic.on_send_st_packet(len(packet),self._send_packet_buffer.qsize())
                elif packet.get_type() == Packet.TYPE_VIDEO:
                    packet = trans_protocol.gen_video_data_pack(packet.data())
                    FpvLogStatistic.on_send_vi_packet(len(packet),self._send_packet_buffer.qsize())
            except:
                print(traceback.print_exc())
                continue
            time2 = time.time()*1000

            # self._udpSocket.sendto(packet,(configs.SERVER_IP,configs.SERVER_VIDEO_PORT))
            self.mp_sender.send(packet)
            time3 = time.time()*1000
            # print("Send_ms: tot/pop/encl/send/len: %s/%s/%s/%s/%s"%(time3-time0,time1-time0,time2-time1,time3-time2,len(packet)))

    def videoConnectionFPVReceiveWorker(self) -> None:
        while self._running:
            try:
                packet, recv_addr = self._udpSocket.recvfrom(MAX_UDP_PACKET)
            except:
                continue
            # print("receiver worker get data")
            # print("packet len: ",len(packet))
            if trans_protocol.is_ctrl_pack(packet):
                FpvLogStatistic.on_recv_ctrl_packet()
                if trans_protocol.is_data_channel_pack(packet):
                    FpvLogStatistic.on_recv_dc_packet(1)
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
                 mode:str=CONNECTION_MODE_CONTROLLER,
                 mp_sender:MpUdpSender = None):
        self._recv_video_packet_buffer = recv_video_packet_buffer
        self._recv_ctrl_packet_buffer = recv_ctrl_packet_buffer
        self.video_connection = None
        self._status = self.Status(self)
        self.mode = mode
        self.mp_sender = mp_sender


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
                                                recv_ctrl_packet_buffer=self._recv_ctrl_packet_buffer,mode=self.mode,
                                                mp_sender=self.mp_sender)
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







