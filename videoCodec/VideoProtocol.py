from abc import ABCMeta,abstractmethod
import numpy as np
from videoCodec.h264 import PACKET_MAX
import collections
from queue import PriorityQueue
import bisect
from typing import List,Tuple
import time
from videoCodec.h264 import H264PayloadDescriptor

MAX_PACKET_CACHE_TIME = 200 #ms

class VideoProtocol(metaclass=ABCMeta):
    @abstractmethod
    def handle_recved_packet(self,packet:bytes)->List[bytes]:
        '''
        :param packet: received UDP/TCP packet
        :return list of raw videoCodec packet
        '''
        pass


class VideoProtocolHandler(metaclass=ABCMeta):

    @abstractmethod
    def enclosure_packets(self,packets:List[bytes])->List[bytes]:
        pass

    @abstractmethod
    def get_packet_size(self,packet:bytes):
        pass

    @abstractmethod
    def get_total_packets_num(self,packet:bytes):
        pass

    @abstractmethod
    def get_packet_seq_num(self,packet:bytes):
        pass

    @abstractmethod
    def get_header(self,packet:bytes):
        pass

    @abstractmethod
    def get_data(self,packet:bytes):
        pass

    @abstractmethod
    def pad_packet(self,packet:bytes):
        pass

    @abstractmethod
    def pad_packet_to_ndarray(self, packet: bytes):
        pass

    '''
    method: parse_packet
    args: packet
    return parsed header and data
    '''
    @abstractmethod
    def parse_packet(self,packet:bytes):
        pass

    @abstractmethod
    def is_fec(self,packet:bytes):
        pass

    @abstractmethod
    def enclosure_packets(self,packets:List[bytes])->List[bytes]:
        pass

    @abstractmethod
    def get_ets(self,packet:bytes)->int:
        pass

    @abstractmethod
    def get_fec_ts(self,packet:bytes)->int:
        pass

    @abstractmethod
    def get_fec_lv(self,packet:bytes)->int:
        pass

"""
DRXH264Protocol:

This protocol is designed for 1 vs 1 FPV video transport.
To show frames as quickly as possible.

this protocol is to enclosure packets encoded from encoder or parse packets for decoder to decode

Need to be improved!

    HEADER: 17 bytes
        0~1 bytes: total packet num: :Big Order
        2~3 bytes: current packet num : :Big Order
        4~5 bytes：packet size:Big Order
        6~7 bytes：fec_lv: Big Order
        8~11 bytes: fec_timestamp fec_ts : Big Order
        12-15 bytes: encode timestamp ets: Big Order
        16 byte : 1 bit Fec Flag | 
        
FEC_PACKET: 
    HEADER:ETS RETURNED 
"""

DRX_HEADER_TOTAL_PACKET_NUM_LEN = 2
DRX_HEADER_CRT_PACKET_NUM_LEN = 2
DRX_HEADER_PACKET_SIZE_LEN = 2
DRX_HEADER_PACKET_FEC_LV_LEN = 2
DRX_HEADER_ETS_LEN = 4
DRX_HEADER_FEC_TS_LEN = 4
DRX_HEADER_FLAGS_LEN = 1
DRX_HEADER_SIZE = DRX_HEADER_TOTAL_PACKET_NUM_LEN \
                  + DRX_HEADER_CRT_PACKET_NUM_LEN \
                  + DRX_HEADER_PACKET_SIZE_LEN \
                  + DRX_HEADER_PACKET_FEC_LV_LEN \
                  + DRX_HEADER_ETS_LEN \
                  + DRX_HEADER_FEC_TS_LEN \
                  + DRX_HEADER_FLAGS_LEN

DRX_HEADER_TOTAL_PACKET_NUM_ST = 0
DRX_HEADER_TOTAL_PACKET_NUM_ED = DRX_HEADER_TOTAL_PACKET_NUM_ST + DRX_HEADER_TOTAL_PACKET_NUM_LEN
DRX_HEADER_CRT_PACKET_NUM_ST = DRX_HEADER_TOTAL_PACKET_NUM_ED
DRX_HEADER_CRT_PACKET_NUM_ED = DRX_HEADER_CRT_PACKET_NUM_ST + DRX_HEADER_CRT_PACKET_NUM_LEN
DRX_HEADER_PACKET_SIZE_ST = DRX_HEADER_CRT_PACKET_NUM_ED
DRX_HEADER_PACKET_SIZE_ED = DRX_HEADER_PACKET_SIZE_ST + DRX_HEADER_PACKET_SIZE_LEN
DRX_HEADER_PACKET_FEC_LV_ST = DRX_HEADER_PACKET_SIZE_ED
DRX_HEADER_PACKET_FEC_LV_ED = DRX_HEADER_PACKET_FEC_LV_ST + DRX_HEADER_PACKET_FEC_LV_LEN
DRX_HEADER_FEC_TS_ST = DRX_HEADER_PACKET_FEC_LV_ED
DRX_HEADER_FEC_TS_ED = DRX_HEADER_FEC_TS_ST + DRX_HEADER_FEC_TS_LEN
DRX_HEADER_ETS_ST = DRX_HEADER_FEC_TS_ED
DRX_HEADER_ETS_ED = DRX_HEADER_ETS_ST + DRX_HEADER_ETS_LEN
DRX_HEADER_FLAGS = DRX_HEADER_ETS_ED
DRX_PACKET_MAX = PACKET_MAX + DRX_HEADER_SIZE


class Drx_Packets_Unit():
    def __init__(self,ets:int,protocol:VideoProtocolHandler):
        self._size = 0
        self._total_num = 0
        self._packets = [None]
        self._ets = ets # encoding timestamp
        self.protocol = protocol
        self._activated = False

    def can_get_packets(self) -> bool:
        return self.is_activated() and self._is_full()

    def _is_full(self) -> bool:
        return self._size == self._total_num

    def get_size(self) -> int:
        return self._size

    def is_activated(self):
        return self._activated

    '''
    add_packet: add raw data packet or fec packet 
    args:
    
        
    '''
    def add_packet(self,packet:bytes,protocol:VideoProtocolHandler)->None:

        if packet is None:
            return

        seq_num = protocol.get_packet_seq_num(packet)
        _header,_parsed_packet = self.protocol.parse_packet(packet)

        if not self.is_activated():
            self._total_num = self.protocol.get_total_packets_num(packet)
            self._packets = [None] * self._total_num
            self._activated = True

        if not self.protocol.is_fec(packet):
            self._packets[seq_num] = _parsed_packet
            self._size += 1
        else:
            #is fec packet
            self._fec = _parsed_packet


    def get_packets(self,is_force = False)->List[bytes]:
        if not self.can_get_packets():
            return []

        else:
            parsed_packets = self._packets
            return parsed_packets

        # else:
        #     # not full
        #     if self.can_get_packets():
        #         loss_pack = self.protocol.pad_packet_to_ndarray(bytearray(self._fec))
        #         for pack_idx,packet in enumerate(self._packets):
        #             header = self._headers[pack_idx]
        #             if packet and header:
        #                 loss_pack = loss_pack ^ self.protocol.pad_packet_to_ndarray(bytearray(header + packet))
        #
        #         loss_pack_size = self.protocol.get_packet_size(loss_pack)
        #         self.add_packet(bytes(loss_pack)[:loss_pack_size],self.protocol)
        #         parsed_packet = self._packets
        #         return parsed_packet
        #     if not is_force:
        #         return []
        #     else:
        #         # forced return to return packet received whatever it's complete or not
        #         parsed_packet = [self.protocol.get_data(packet) for packet in self._packets if packet is not None]
        #         return parsed_packet


class Drx_Fec_Packets_Unit():
    def __init__(self, fec_ts: int, protocol: VideoProtocolHandler):
        self._fec = None
        self._size = 0
        self._fec_lv = 0
        self._packets = [None]
        self._fec_ts = fec_ts  # fec gen timestamp
        self._headers = [None]
        self.protocol = protocol
        self._activated = False


    def can_get_packets(self) -> bool:
        return self.is_activated() and (self._is_full() or (self.get_size() == self._fec_lv - 1 and self._fec))

    def _is_full(self) -> bool:
        return self._size == self._fec_lv

    def get_size(self) -> int:
        return self._size

    def is_activated(self):
        return self._activated

    '''
    add_packet: add raw data packet or fec packet 
    args:


    '''

    def on_add_packet(self, packet: bytes) -> List[bytes]:

        if packet is None:
            return []

        _header, _parsed_packet = self.protocol.parse_packet(packet)

        if not self.is_activated():
            self._fec_lv = self.protocol.get_fec_lv(packet)
            self._packets = [None] * self._fec_lv
            self._headers = [None] * self._fec_lv
            self._activated = True

        if not self.protocol.is_fec(packet):
            self._packets[self._size] = packet
            self._headers[self._size] = _header

            self._size += 1
            return [packet]
        else:
            # is fec packet
            self._fec = _parsed_packet
            return []

    def get_packets(self) -> List[bytes]:
        if not self.can_get_packets():
            return []

        if self._is_full():
            parsed_packets = self._packets
            return []
        else:
            # not full
            if self.can_get_packets():
                loss_pack = self.protocol.pad_packet_to_ndarray(bytearray(self._fec))
                for pack_idx, packet in enumerate(self._packets):
                    header = self._headers[pack_idx]
                    if packet and header:
                        loss_pack = loss_pack ^ self.protocol.pad_packet_to_ndarray(bytearray(packet))
                loss_pack_size = self.protocol.get_packet_size(loss_pack)
                loss_packet = bytes(loss_pack)[:loss_pack_size]
                return [loss_packet]
        return []

class DRXH264Protocol(VideoProtocol):
    def __init__(self):
        self.protocol = DRXH264ProtocolHandler()
        self._packet_map = collections.OrderedDict()
        self._fec_map = collections.OrderedDict()
        self.ets_array = []
        self.fec_ts_array = []
        self.rets = 0  #last packets encoding timestamp of received packet
        self.ets = 0 # last full packet encoding timestamp
        self.first_fec_ts = 0 # first fec packet timestamp

    def handle_recved_packet(self,packet:bytes) ->List[Tuple[int,List[bytes]]]:
        #todo: handle the case when timestamp jump from 0xffffffff to 0
        _fec_ts = self.protocol.get_fec_ts(packet)
        fec_buffer_unit = self._fec_map.setdefault(_fec_ts,Drx_Fec_Packets_Unit(_fec_ts,self.protocol))
        if not fec_buffer_unit.is_activated():
            # first incoming packet of this fec_ts
            bisect.insort(self.fec_ts_array, _fec_ts)

        prev_recovery_packets = []
        pop_fec_unit_tss = []
        for stack_fec_ts in self.fec_ts_array:
            if stack_fec_ts >= _fec_ts:
                break
            if stack_fec_ts in self._fec_map:
                stack_fec_buffer_unit = self._fec_map[stack_fec_ts]
                if stack_fec_buffer_unit.can_get_packets():
                    prev_recovery_packets.extend(stack_fec_buffer_unit.get_packets())
                    pop_fec_unit_tss.append(stack_fec_ts)

        # pop full fec buffer unit
        for pop_fec_ts in pop_fec_unit_tss:
            self.fec_ts_array.remove(pop_fec_ts)
            self._fec_map.pop(pop_fec_ts)

        fec_ret_packets = fec_buffer_unit.on_add_packet(packet)
        fec_ret_packets = prev_recovery_packets + fec_ret_packets
        h264_packets = []
        for fec_ret_packet in fec_ret_packets:
            _ets = self.protocol.get_ets(fec_ret_packet)
            if _ets <= self.ets:
                # refuse handle packet arrives too lately
                return []

            if _ets > self.rets:
                self.rets = _ets

            buffer_unit = self._packet_map.setdefault(_ets,Drx_Packets_Unit(_ets,self.protocol))


            if not buffer_unit.is_activated():
                # first incoming packet of this ets
                bisect.insort(self.ets_array,_ets)

            buffer_unit.add_packet(fec_ret_packet,self.protocol)
            last_pop_idx = -1

            if buffer_unit.can_get_packets():
                for idx,packet_ets in enumerate(self.ets_array):
                    if packet_ets > _ets:
                        break
                    if packet_ets <= _ets:
                        #force drop lated packet
                        last_pop_idx = idx
                        h264_packets.append((packet_ets,self._packet_map.pop(packet_ets).get_packets(is_force=False)))

            else:
                for idx, packet_ets in enumerate(self.ets_array):
                    if self.rets - packet_ets > MAX_PACKET_CACHE_TIME:
                        #timeout to force update
                        last_pop_idx = idx
                        h264_packets.append((packet_ets,self._packet_map.pop(packet_ets).get_packets(is_force=False)))
                    else:
                        break
            if last_pop_idx >= 0:
                self.ets = self.ets_array[last_pop_idx]
                self.ets_array = self.ets_array[last_pop_idx+1:]

            # pop useless fec buffer unit
            last_pop_idx = -1
            for last_pop_idx,stack_fec_ts in enumerate(self.fec_ts_array):
                if stack_fec_ts >= self.ets:
                    break
            if last_pop_idx >=0:
                self.first_fec_ts = self.fec_ts_array[last_pop_idx]
                self.fec_ts_array = self.fec_ts_array[last_pop_idx:]

        return h264_packets

    def enclosure_packets(self,packets:List[bytes],fec_lv=8)->List[bytes]:
        return self.protocol.enclosure_packets(packets,fec_lv)


class DRXH264ProtocolHandler(VideoProtocolHandler):
    def __init__(self):
        self.fec_stack_packets = []
        self.prev_fec_timestamp = 0
        self.prev_fec_lv = 8

        self.prev_fec_ts_for_count = 0
        self.prev_fec_count = 0

    def parse_packet(self,packet:bytes):
        try:
            header = self.get_header(packet)
            data = self.get_data(packet)
            return header,data
        except Exception:
            print(Exception)

    def get_header(self,packet:bytes):
        header = packet[:DRX_HEADER_SIZE]
        return header


    def get_data(self,packet:bytes):
        return packet[DRX_HEADER_SIZE:]

    def get_packet_size(self,packet:bytes):
        size_bytes = packet[DRX_HEADER_PACKET_SIZE_ST:DRX_HEADER_PACKET_SIZE_ED]
        return int.from_bytes(size_bytes,'big')

    def pad_packet(self,packet:bytes):
        return bytes(self.pad_packet_to_ndarray(packet))

    def pad_packet_to_ndarray(self,packet:bytes):
        pad_length = DRX_PACKET_MAX - len(packet)
        return np.pad(bytearray(packet), (0, pad_length))

    def get_ets(self,packet:bytes):
        ets_bytes = packet[DRX_HEADER_ETS_ST:DRX_HEADER_ETS_ED]
        return int.from_bytes(ets_bytes,'big')

    def get_fec_ts(self,packet:bytes):
        fec_ts_bytes = packet[DRX_HEADER_FEC_TS_ST:DRX_HEADER_FEC_TS_ED]
        return int.from_bytes(fec_ts_bytes,'big')

    def get_fec_lv(self,packet:bytes):
        fec_ts_bytes = packet[DRX_HEADER_PACKET_FEC_LV_ST:DRX_HEADER_PACKET_FEC_LV_ED]
        return int.from_bytes(fec_ts_bytes,'big')

    def get_packet_seq_num(self,packet:bytes):
        seq_num_bytes = packet[DRX_HEADER_CRT_PACKET_NUM_ST:DRX_HEADER_CRT_PACKET_NUM_ED]
        return int.from_bytes(seq_num_bytes,'big')

    def get_total_packets_num(self,packet:bytes):
        total_num_bytes = packet[DRX_HEADER_TOTAL_PACKET_NUM_ST:DRX_HEADER_TOTAL_PACKET_NUM_ED]
        return int.from_bytes(total_num_bytes,'big')

    def is_fec(self,packet:bytes):
        return bool((packet[DRX_HEADER_FLAGS]&0x80)>>7)

    """
    DRXH264Protocol:

    This protocol is designed for 1 vs 1 FPV video transport.
    To show frames as quickly as possible.

    this protocol is to enclosure packets encoded from encoder or parse packets for decoder to decode

    Need to be improved!

    HEADER: 17 bytes
        0~1 bytes: total packet num: :Big Order
        2~3 bytes: current packet num : :Big Order
        4~5 bytes：packet size:Big Order
        6~7 bytes：fec_lv: Big Order
        8~11 bytes: fec_timestamp fec_ts : Big Order
        12-15 bytes: encode timestamp ets: Big Order
        16 byte : 1 bit Fec Flag | 
    """

    def enclosure_packets(self,packets:List[bytes],fec_level=8) ->List[bytes]:
        total_packet_num = len(packets)
        enclosured_packets = []
        if self.prev_fec_lv != fec_level:
            self.fec_stack_packets = []
        ets = self.gen_ets()
        rest_packets = packets
        crt_packet_num = 0
        while len(rest_packets) > 0:
            fec_packet = self.pad_packet_to_ndarray(b'')
            stack_packet_number = len(self.fec_stack_packets)
            rest_packets_num = len(rest_packets)
            if stack_packet_number <= 0:
                _new_fec_ts = self.gen_ets()
                self.prev_fec_timestamp = _new_fec_ts if _new_fec_ts > self.prev_fec_timestamp else self.prev_fec_timestamp+1
                # print("prev_fec_send_ts_update:%s"%self.prev_fec_timestamp)
            if stack_packet_number + rest_packets_num >= fec_level:
                pop_packets_num = fec_level - stack_packet_number
                _pop_packets = rest_packets[:pop_packets_num]
                rest_packets = rest_packets[pop_packets_num:]
                max_len = 0
                for enclosured_stack_packet in self.fec_stack_packets:
                    fec_packet = fec_packet ^ self.pad_packet_to_ndarray(enclosured_stack_packet)
                    if len(enclosured_stack_packet) > max_len:
                        max_len = len(enclosured_stack_packet)
                for pop_packet in _pop_packets:
                    header = self.gen_header(total_packet_num, crt_packet_num, len(pop_packet) + DRX_HEADER_SIZE, fec_level,self.prev_fec_timestamp,ets,
                                             False)
                    enclosured_packet = header + pop_packet
                    if len(enclosured_packet) > max_len:
                        max_len = len(enclosured_packet)
                    fec_packet = fec_packet ^ self.pad_packet_to_ndarray(enclosured_packet)
                    crt_packet_num += 1
                    # self.count_enclosured_packet_for_fec(enclosured_packet)
                    enclosured_packets.append(enclosured_packet)
                fec_packet = bytes(fec_packet)[:max_len]
                fec_header = self.gen_header(total_packet_num, 0, max_len + DRX_HEADER_SIZE, fec_level,
                                         self.prev_fec_timestamp, ets,True)
                # self.count_enclosured_packet_for_fec(fec_header+fec_packet)
                enclosured_packets.append(fec_header+fec_packet)
                self.fec_stack_packets = []
            else:
                # stack_num + rest packet num < fec_num
                _pop_packets = rest_packets
                rest_packets = []
                for pop_packet in _pop_packets:
                    header = self.gen_header(total_packet_num, crt_packet_num, len(pop_packet) + DRX_HEADER_SIZE, fec_level,self.prev_fec_timestamp,ets,
                                             False)
                    enclosured_packet = header + pop_packet
                    crt_packet_num += 1
                    # self.count_enclosured_packet_for_fec(enclosured_packet)
                    enclosured_packets.append(enclosured_packet)
                    self.fec_stack_packets.append(enclosured_packet)

        # for crt_packet_num,packet in enumerate(packets):
        #
        #     header = self.gen_header(total_packet_num,crt_packet_num,len(packet)+DRX_HEADER_SIZE,ets,False)
        #     enclosured_packet = header + packet
        #     if len(enclosured_packet) > max_len:
        #         max_len = len(enclosured_packet)
        #     enclosured_packets.append(header+packet)
        #     fec_packet = fec_packet ^ self.pad_packet_to_ndarray(enclosured_packet)

        # fec_packet = bytes(fec_packet)[:max_len]
        # fec_header = self.gen_header(total_packet_num,0,max_len+DRX_HEADER_SIZE,ets,True)
        # enclosured_packets.append(fec_header+fec_packet)
        return enclosured_packets

    def count_enclosured_packet_for_fec(self,enclosured_packet):
        fec_ts = self.get_fec_ts(enclosured_packet)
        if fec_ts != self.prev_fec_ts_for_count:
            print("fec_ts:%s,count:%s" % (self.prev_fec_ts_for_count, self.prev_fec_count))
            self.prev_fec_ts_for_count = fec_ts
            self.prev_fec_count = 1
        else:
            self.prev_fec_count += 1

    def gen_header(self,total_packet_num:int,current_packet_num:int,packet_size:int,fec_lv:int,fec_ts:int,ets:int,is_fec:bool):
        return int.to_bytes(total_packet_num,DRX_HEADER_TOTAL_PACKET_NUM_LEN,'big') \
               + int.to_bytes(current_packet_num,DRX_HEADER_CRT_PACKET_NUM_LEN,'big') \
               + int.to_bytes(packet_size,DRX_HEADER_PACKET_SIZE_LEN,'big') \
               + int.to_bytes(fec_lv, DRX_HEADER_PACKET_FEC_LV_LEN, 'big') \
               + int.to_bytes(fec_ts, DRX_HEADER_FEC_TS_LEN, 'big') \
               + int.to_bytes(ets,DRX_HEADER_ETS_LEN,'big') \
               + int.to_bytes(int(is_fec)<<7,1,'big')

    def gen_ets(self):
        ts = int(time.time()*1000) & 0xffffffff
        return ts
