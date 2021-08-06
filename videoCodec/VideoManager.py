from queue import Queue
from threading import Thread,Lock
from videoCodec.VideoTransporter import VideoTransporter,VideoConnection,CONNECTION_MODE_FPV,CONNECTION_MODE_CONTROLLER
from videoCodec.VideoSink import VideoRender
from videoCodec.VideoStream import LocalVideoStream,RemoteVideoStream
from videoCodec.FPVCTRLSink import CtrlSink,CtrlSinkInterface
from videoCodec.SerializableData import FPVSerializeControlData,FPVStatusData
import traceback

"""
Singleton

Maintain video resources and procedures besides ctrl data channel sinker 
Include　packet queue, videoframe queue, encoder queue, decoder queue
Include  Local Stream, Remote Stream
Include local_worker,remote_worker


connection -includes-> worker_thread 
stream -includes-> Encoder/decoder & include render
      |- render -includes-> worker_thread,

"""

CONNECTION_MODE_FPV = CONNECTION_MODE_FPV
CONNECTION_MODE_CONTROLLER = CONNECTION_MODE_CONTROLLER

class VideoManager():
    _instance_lock = Lock()

    def __init__(self,mode):
        self.recv_video_packet_buffer = Queue()
        self.recv_ctrl_packet_buffer = Queue()
        self.mode = mode

    @classmethod
    def instance(cls ,*args ,**kwargs):
        with cls._instance_lock:
            if not hasattr(cls ,"_instance"):
                cls._instance = VideoManager(*args ,**kwargs)

        return cls._instance

    def init_all_resources(self,render:VideoRender,ctrl_sink_interface:CtrlSinkInterface):
        self.init_transporter()
        self.init_stream()
        self.init_ctrl_sink()
        self.set_render(render)

        self.set_ctrl_sink_interface(ctrl_sink_interface)


    def init_transporter(self):
        try:
            self.video_transporter = VideoTransporter.instance(self.recv_video_packet_buffer,
                                                               self.recv_ctrl_packet_buffer,
                                                               self.mode)
            self.video_transporter.start()
            return True
        except:
            print("Error: Unable to connect server")
            print(traceback.print_exc())
            return False


    def init_stream(self):
        if self.mode == CONNECTION_MODE_CONTROLLER:
            self._stream = RemoteVideoStream(self.recv_video_packet_buffer)
            self._stream.start()

        elif self.mode == CONNECTION_MODE_FPV:
            self._stream = LocalVideoStream()
            self._stream.start()

    def init_ctrl_sink(self):
        self.serializable_data = FPVSerializeControlData if self.mode == CONNECTION_MODE_FPV else FPVStatusData
        self._ctrl_sink = CtrlSink(self.serializable_data,self.recv_ctrl_packet_buffer,0.001)
        self._ctrl_sink.start()

    def set_render(self,render):
        self._stream.set_render(render)

    def set_ctrl_sink_interface(self,ctrl_sink_interface):
        self._ctrl_sink.set_sink_interface(ctrl_sink_interface)

    def stop_all(self):
        self._stream.stop()
        self._ctrl_sink.stop()
        self.video_transporter.start()
        self.video_transporter.stop()








