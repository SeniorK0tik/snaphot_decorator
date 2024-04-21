import time



class SnapShotTimer:
    def __init__(self, timeout: int) -> None:
        self.timeout = timeout
        self.previous_snapshot_time = time.time()


    def upd_previous_snapshot_time(self, new: int | float) -> None:
        self.previous_snapshot_time = new

    def suppose_time(self) -> int | float:
        return self.previous_snapshot_time + self.timeout
