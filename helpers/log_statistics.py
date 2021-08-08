from abc import ABCMeta,abstractmethod
from threading import Thread,Lock
import time
import datetime
import traceback

class LogStatisticBase(metaclass=ABCMeta):
    def __init__(self,report_time_s = 1):
        self._running = True
        self._report_time = report_time_s
        self._thread = Thread(target=self.log_report_target,args=[])
        self._thread.start()

    def stop(self):
        self._running = False

    def log_report_target(self):
        while self._running:
            self.log_report()
            time.sleep(self._report_time)

    @abstractmethod
    def log_report(self):
        pass


class FpvLogStatistic(LogStatisticBase):
    _instance_lock = Lock()

    @classmethod
    def instance(cls, *args, **kwargs):
        with cls._instance_lock:
            if not hasattr(cls, "_instance"):
                cls._instance = FpvLogStatistic(*args, **kwargs)
        return cls._instance

    @classmethod
    def on_recv_packet(cls,recv_nums):
        cls.instance().recv_pack_num += recv_nums

    @classmethod
    def on_recv_dc_packet(cls,dc_packet_num):
        cls.instance().dc_pack_count += dc_packet_num

    @classmethod
    def on_recv_ctrl_packet(cls):
        cls.instance().control_pack += 1

    @classmethod
    def on_ctrl_packet_parsed(cls,ctrl_data):
        cls.instance().control_data = ctrl_data

    @classmethod
    def on_req_send_packets(cls,req_send_pack_num):
        cls.instance().gen_packets_count += req_send_pack_num

    @classmethod
    def on_req_send_video_pack(cls,req_send_vi_pack_num,tot_len):
        cls.instance().gen_packets_count += req_send_vi_pack_num
        cls.instance().gen_bytes_num += tot_len
        cls.instance().gen_video_packet_num += req_send_vi_pack_num

    @classmethod
    def on_req_send_st_pack(cls,gen_st_pack_num,tot_len):
        cls.instance().gen_status_packet_num += gen_st_pack_num
        cls.instance().gen_packets_count += gen_st_pack_num
        cls.instance().gen_bytes_num += tot_len

    @classmethod
    def on_send_st_packet(cls,pack_len,q_len):
        cls.instance().send_bytes_num += pack_len
        cls.instance().send_st_packet_num += 1
        cls.instance().send_queue_length = q_len

    @classmethod
    def on_send_vi_packet(cls,pack_len,q_len):
        cls.instance().send_bytes_num += pack_len
        cls.instance().send_vi_packet_num += 1
        cls.instance().send_queue_length = q_len

    def __init__(self,report_time_s = 1):
        # control
        self.recv_pack_num = 0
        self.control_pack = 0
        self.dc_pack_count = 0
        self.control_data = dict()
        self.gen_packets_count = 0
        self.gen_status_packet_num = 0
        self.gen_video_packet_num = 0
        self.gen_bytes_num = 0
        self.send_vi_packet_num = 0
        self.send_st_packet_num = 0
        self.send_bytes_num = 0
        self.send_queue_length = 0
        self.cap_frames_num = 0
        self.dec_frames_num = 0
        super(FpvLogStatistic,self).__init__(report_time_s)


    def reset_counts(self):
        self.recv_pack_num = 0
        self.control_pack = 0
        self.dc_pack_count = 0
        self.control_data = dict()
        self.gen_packets_count = 0
        self.gen_status_packet_num = 0
        self.gen_video_packet_num = 0
        self.gen_bytes_num = 0
        self.send_vi_packet_num = 0
        self.send_st_packet_num = 0
        self.send_bytes_num = 0
        self.send_queue_length = 0
        self.cap_frames_num = 0
        self.dec_frames_num = 0

    def log_report(self):
        strftime = datetime.datetime.fromtimestamp(time.time()).isoformat()
        vtx_log_to_report = strftime + ": FPV_VTX: "\
            + "packet_gen/vi/st/tot_bytes: %s/%s/%s/%s"%(self.gen_packets_count,self.gen_video_packet_num,self.gen_status_packet_num,self.gen_bytes_num) \
            + " ,packet_send_vi/st/bytes/q_len: %s/%s/%s/%s"%(self.send_vi_packet_num,self.send_st_packet_num,self.send_bytes_num,self.send_queue_length) \

        vrx_log_to_report = strftime + ": FPV_VRX: " \
            + "packet_recv/dc/ctrl/: %s/%s/%s"%(self.recv_pack_num,self.dc_pack_count,self.control_pack) \
            + " ,ctrl_data: %s"%self.control_data

        self.reset_counts()
        print(vtx_log_to_report)
        print(vrx_log_to_report)

