from dataclasses import dataclass, field

@dataclass
class Process:
    DEFAULT_COLORS = [
        "#2563eb",
        "#059669",
        "#dc2626",
        "#7c3aed",
        "#ea580c",
        "#0891b2",
        "#be185d",
        "#ca8a04",
    ]
    """
    Represents a CPU process.
    """

    pid: str
    arrival_time: int
    burst_time: int
    priority: int = 0

    # Runtime values
    remaining_time: int = field(init=False)

    start_time: int = field(default=-1)
    completion_time: int = field(default=0)

    turnaround_time: int = field(default=0)
    waiting_time: int = field(default=0)
    response_time: int = field(default=0)

    finished: bool = field(default=False)
    color: str = field(default="")

    def __post_init__(self):
        """
        Initialize values after object creation.
        """
        self.remaining_time = self.burst_time
        if not self.color:
            self.color = self._get_default_color()

    def _get_default_color(self) -> str:
        if not self.pid:
            return self.DEFAULT_COLORS[0]
        index = sum(ord(ch) for ch in self.pid) % len(self.DEFAULT_COLORS)
        return self.DEFAULT_COLORS[index]

    def calculate_metrics(self):
        """
        Compute turnaround, waiting, and response times.
        """

        self.turnaround_time = self.completion_time - self.arrival_time
        self.waiting_time = self.turnaround_time - self.burst_time

        if self.start_time == -1:
            self.response_time = 0
        else:
            self.response_time = self.start_time - self.arrival_time

    def reset(self):
        """
        Reset runtime values so another algorithm can simulate
        using the same processes.
        """

        self.remaining_time = self.burst_time

        self.start_time = -1
        self.completion_time = 0

        self.turnaround_time = 0
        self.waiting_time = 0
        self.response_time = 0

        self.finished = False

    def to_table(self):
        return [
            self.pid,
            self.arrival_time,
            self.burst_time,
            self.priority,
            self.completion_time,
            self.turnaround_time,
            self.waiting_time,
            self.response_time,
        ]

    def __repr__(self):
        return (
            f"Process("
            f"{self.pid}, "
            f"AT={self.arrival_time}, "
            f"BT={self.burst_time}, "
            f"RT={self.remaining_time})"
        )