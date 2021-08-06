from abc import ABCMeta,abstractmethod
from av.frame import Frame
from threading import Thread,Lock
from queue import Queue
from videoCodec.VideoProtocol import DRXH264Protocol,DRXH264ProtocolHandler
from videoCodec.h264 import *
import time
import av
from av.frame import Frame
from videoCodec.VideoSink import VideoRender
from videoCodec.VideoTransporter import VideoPacket
from videoCodec.VideoTransporter import VideoTransporter
import random
import traceback

'''
Stream : srouce -> sink
local: src: camera, sink: sendQueue
remote: src: decoder_buffer, sink: render_buffer: async render
'''

class Stream(metaclass=ABCMeta):

    def set_render(self,videoSink):
        pass


    @abstractmethod
    def stream_worker_target(self):
        pass

    def start(self):
        self._stream_worker = Thread(target=self.stream_worker_target,
                                     args=())

        self._stream_worker.start()

    @abstractmethod
    def stop(self):
        pass


class LocalVideoStream(Stream):
    def __init__(self):
        self.transporter = VideoTransporter.instance()
        self._protocol = DRXH264Protocol()
        self._protocol_handler = DRXH264ProtocolHandler()
        self._encoder = H264Encoder()
        self._running = True
        self.cam = None
        self.fec_level = 8

    def stream_worker_target(self):
        while self._running:
            if self.cam:
                frame = self.cam.get_next_frame()
                if not frame:
                    time.sleep(0.0001)
                    continue
                packets, ets = self._encoder.encode(frame)
                enclosure_packets = self._protocol_handler.enclosure_packets(packets,fec_level=8)

                for packet in enclosure_packets:
                    self.transporter.send(VideoPacket(packet))


    def open_camera(self):
        if not self.cam:
            self.cam = Camera()
            self.cam.open()

    def close_camera(self):
        if self.cam:
            self.cam.close()
            self.cam = None

    def start(self):
        self.open_camera()
        super().start()

    def stop(self):
        self._running = False

class RemoteVideoStream(Stream):
    def __init__(self,packet_buffer:Queue):
        self._packet_buffer = packet_buffer
        self._frame_buffer = Queue()
        self._protocol = DRXH264Protocol()
        self._protocol_handler = DRXH264ProtocolHandler()
        self._decoder = H264Decoder()
        self._video_descriptor = H264PayloadDescriptor(first_fragment="")
        self.render_lock = Lock()
        self._video_sink = None
        self._running = True

    def stream_worker_target(self):
        while self._running:
            try:
                packet = self._packet_buffer.get_nowait()
            except Exception:
                time.sleep(0.0001)
                continue
            # print("get packet")
            parsed_packets = self._protocol.handle_recved_packet(packet.data())
            h264packets = []
            for ets, _parsed_packets in parsed_packets:
                _parsed_packets = [self._video_descriptor.parse(_parsed_packet)[1] for _parsed_packet in _parsed_packets]
                h264packets.append((ets, _parsed_packets))
            for ets, h264packet in h264packets:
                parsed_packet = b''.join(h264packet)
                # print(len(parsed_packet))
                if parsed_packet == b'':
                    continue
                _frames = self._decoder.decode(JitterFrame(parsed_packet, ets))
                if len(_frames) > 0:
                    for _frame in _frames:
                        with self.render_lock:
                            if self._video_sink:
                                self._video_sink.onFrame(_frame)

    def set_render(self,render:VideoRender):
        with self.render_lock:
            self._video_sink = render

    def stop(self):
        self._running = False

class Camera():
    def __init__(self):
        self.device_name = 'USB Camera'
        self.container = None

    def open(self)->bool:
        if not self.container:
            options = {"framerate": "5", "video_size": "640x480", "b": "900000"}
            try:
                self.container = av.open("video=USB Camera", format="dshow", options=options)
                return True
            except Exception:
                print(traceback.print_exc())
                print(Exception)
                return False
        return False
    def get_next_frame(self)->Frame:
        if self.container is not None:
            return next(self.container.decode())
        else:
            return None

    def close(self):
        if self.container is not None:
            self.container.close()
            self.container = None



