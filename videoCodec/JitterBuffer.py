class JitterFrame:
    def __init__(self, data: bytes, timestamp: int) -> None:
        self.data = data
        self.timestamp = timestamp