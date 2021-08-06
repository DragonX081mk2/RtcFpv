from abc import ABCMeta,abstractmethod

class SerializableData(metaclass=ABCMeta):

    @classmethod
    @abstractmethod
    def serialize(cls,data:dict)->bytes:
        pass

    @classmethod
    @abstractmethod
    def deserialize(cls,serialized_data:bytes)->dict:
        pass


class FPVSerializeControlData(SerializableData):
    #serialization related
    ORDER = 'big'

    #servo motion
    KEY_YAW = 'yaw'

    # motor motion
    KEY_MOTION = 'motion'
    KEY_SPEED = 'spd' # 0-1 acc 0.1
    VALUE_FORWARD = 0
    VALUE_BACKWARD = 1
    VALUE_TURN_LEFT = 2
    VALUE_TURN_RIGHT = 3
    VALUE_BACK_LEFT = 4
    VALUE_BACK_RIGHT = 5
    VALUE_SPIN_LEFT = 6
    VALUE_SPIN_RIGHT = 7
    VALUE_BRAKE = 8
    VALUE_STANDBY = 9

    """
    FPV CTRL DATA STRUCTURE
    1 byte yaw 0-180 degrees
    1 byte motion (in big order)
    1 byte speed (0-1 acc 0.1 in big order
    """


    @classmethod
    def serialize(cls,data:dict) ->bytes:
        yaw = data[cls.KEY_YAW]
        motion = data[cls.KEY_MOTION]
        speed = data[cls.KEY_SPEED]
        return int.to_bytes(yaw,1,cls.ORDER) + int.to_bytes(motion,1,cls.ORDER)+int.to_bytes(int(speed*1e1),1,cls.ORDER)

    @classmethod
    def deserialize(cls,serialized_data:bytes) ->dict:
        data_dict = dict()
        yaw_bytes = serialized_data[0:1]
        motion_bytes = serialized_data[1:2]
        spd_bytes = serialized_data[2:3]

        data_dict[cls.KEY_YAW] = int.from_bytes(yaw_bytes,cls.ORDER)
        data_dict[cls.KEY_MOTION] = int.from_bytes(motion_bytes,cls.ORDER)
        data_dict[cls.KEY_SPEED] = int.from_bytes(spd_bytes,cls.ORDER) / 10
        return data_dict

class FPVStatusData(SerializableData):
    # serialization related
    ORDER = 'big'

    # gps
    KEY_LATITUDE = 'latitude'
    KEY_LONGITUDE = 'longitude'
    KEY_SPEED = 'spd'
    KEY_DIRECTION = 'direction'

    """
    GPS: 
        4 byte latitude (signed number, accuracy 1e-7, the positive is N)
        4 byte longitude (signed number, accuracy 1e-7, the position is E)
    SPD：
        1 byte  velocity (m/s , accuracy 1e-1)
    
    DIRECTION:
        2 byte degree ( degree, acc 1e-2)        
    
    
    """
    @classmethod
    def serialize(cls,data:dict) ->bytes:
        latitude = int(data.setdefault(cls.KEY_LATITUDE,91)*1e7)
        longitude = int(data.setdefault(cls.KEY_LONGITUDE,181)*1e7)
        speed = int(data.setdefault(cls.KEY_SPEED,0.0)*1e1)
        direction = int(data.setdefault(cls.KEY_DIRECTION,0.0)*1e2)
        # print(latitude,longitude,speed,direction)
        return int.to_bytes(latitude,4,cls.ORDER,signed=True) \
               + int.to_bytes(longitude,4,cls.ORDER,signed=True)\
               +int.to_bytes(speed,1,cls.ORDER)\
               +int.to_bytes(direction,2,cls.ORDER)

    @classmethod
    def deserialize(cls,serialized_data:bytes) ->dict:
        data_dict = dict()
        latitude_bytes = serialized_data[0:4]
        longitude_bytes = serialized_data[4:8]
        speed_bytes = serialized_data[8:9]
        direction_bytes = serialized_data[9:11]
        data_dict[cls.KEY_LATITUDE] = int.from_bytes(latitude_bytes,cls.ORDER,signed=True)/1e7
        data_dict[cls.KEY_LONGITUDE] = int.from_bytes(longitude_bytes,cls.ORDER,signed=True)/1e7
        data_dict[cls.KEY_SPEED] = int.from_bytes(speed_bytes,cls.ORDER)/1e1
        data_dict[cls.KEY_DIRECTION] = int.from_bytes(direction_bytes,cls.ORDER)/1e2
        return data_dict