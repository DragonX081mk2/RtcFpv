from typing import List

"""
NAIVE TRANSMISSION PROTOCOL: UDP
HEADER: 1 byte
0 :1 bit CAMERA: 0 monitor,1 camera
1 :1 bit CTRL: 0 video pack, 1 CTRL pack
2-3: 2bit CTRL TYPE: 0 Connect 1 Disconnect 2 HeartBeat 3 DataChannel
....

In data channel, use serializable data sturcture


"""



def enclosure_video_packets(packets:List[bytes])->List[bytes]:
    # 1000 0000
    header = b'\x80'
    ret_packets = [header+packet for packet in packets]
    return ret_packets

def parse_packet(packet:bytes)->bytes:
    assert len(packet) > 1, "NAIVE PROTOCOL ERROR, PACKET LEN LESS THAN 1"
    return packet[1:]

def gen_connect_pack(is_camera = False):
    # *100 0000
    header = int.to_bytes(64 | (int(is_camera)<<7),1,'big')
    return header

def gen_heartbeat_pack(is_camera = False):
    # *110 0000
    header = int.to_bytes(96 | (int(is_camera)<<7),1,'big')
    return header

def gen_video_data_pack(packet:bytes, is_camera = True)->bytes:
    # F0000000
    header = int.to_bytes((int(is_camera)<<7),1,'big')
    return header + packet

def gen_ctrl_data_channel_pack(packet:bytes,is_camera = True)->bytes:
    # F111 0000
    header = int.to_bytes( 112 | (int(is_camera) << 7), 1, 'big')
    return header + packet

def is_ctrl_pack(packet:bytes):
    header = packet[0]
    ctrl_flag = bool((header & 0x40)>>6)
    return ctrl_flag

def is_data_channel_pack(packet:bytes)->bool:
    header = packet[0]
    dc_flag = (header & 0x70) >> 4
    return dc_flag == 7
