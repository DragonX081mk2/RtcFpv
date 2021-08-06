from videoCodec.VideoManager import VideoManager,CONNECTION_MODE_FPV,CONNECTION_MODE_CONTROLLER
from videoCodec.VideoSink import VideoRender,VideoBlackHole
from vehicle.FPVSensor import FPVSensorsManager
from vehicle.GPSSensor import MockGpsSensor
from videoCodec.FPVCTRLSink import MockCtrlSinkInterface

sink = MockCtrlSinkInterface()
videoManager = VideoManager.instance(CONNECTION_MODE_FPV)
videoManager.init_all_resources(VideoBlackHole(),sink)
sensorManager = FPVSensorsManager.instance()
sensorManager.register_sensor(MockGpsSensor())
sensorManager.start()

