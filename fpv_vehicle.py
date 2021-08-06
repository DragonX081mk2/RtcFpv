from videoCodec.VideoManager import VideoManager,CONNECTION_MODE_FPV,CONNECTION_MODE_CONTROLLER
from videoCodec.VideoSink import VideoRender,VideoBlackHole
from vehicle.car_driver import *
from vehicle.FPVSensor import FPVSensorsManager
from vehicle.GPSSensor import GpsSensor


sink = CarCTRLSinkInterface()
videoManager = VideoManager.instance(CONNECTION_MODE_FPV)
videoManager.init_all_resources(VideoBlackHole(),sink)
sensorManager = FPVSensorsManager.instance()
sensorManager.register_sensor(GpsSensor())
sensorManager.start()

