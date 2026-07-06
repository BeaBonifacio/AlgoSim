from copy import deepcopy


class Scheduler:

    def __init__(self, processes):
        self.processes = deepcopy(processes)

        self.gantt_chart = []

        self.avg_waiting = 0
        self.avg_turnaround = 0
        self.avg_response = 0

    def reset(self):

        for p in self.processes:
            p.reset()

        self.gantt_chart.clear()

    def calculate_statistics(self):

        total_wait = sum(p.waiting_time for p in self.processes)
        total_turnaround = sum(p.turnaround_time for p in self.processes)

        n = len(self.processes)

        if n == 0:
            return

        self.avg_waiting = total_wait / n
        self.avg_turnaround = total_turnaround / n

    def results(self):
        def sort_key(process):
            pid_suffix = process.pid[1:] if process.pid.startswith("P") else process.pid
            return int(pid_suffix) if pid_suffix.isdigit() else process.pid

        return sorted(self.processes, key=sort_key)

    def fcfs(self):

        self.reset()

        current_time = 0

        processes = sorted(
            self.processes,
            key=lambda x: (x.arrival_time, x.pid)
        )

        for process in processes:

            # CPU Idle
            if current_time < process.arrival_time:

                self.gantt_chart.append({
                    "pid": "Idle",
                    "start": current_time,
                    "end": process.arrival_time
                })

                current_time = process.arrival_time

            process.start_time = current_time
            start = current_time
            current_time += process.burst_time
            end = current_time
            process.completion_time = end
            process.calculate_metrics()
            process.finished = True

            self.gantt_chart.append({
                "pid": process.pid,
                "start": start,
                "end": end
            })

        self.calculate_statistics()
        return self.results()

    def sjf(self):

        self.reset()
        current_time = 0
        completed = 0
        n = len(self.processes)

        while completed < n:
            # Find all processes that have arrived and are not finished
            available = [
                p for p in self.processes
                if p.arrival_time <= current_time and not p.finished
            ]
            # If no process is available, CPU is idle
            if not available:
                future = [
                    p.arrival_time
                    for p in self.processes
                    if not p.finished
                ]

                if not future:
                    break

                next_arrival = min(future)

                self.gantt_chart.append({
                    "pid": "Idle",
                    "start": current_time,
                    "end": next_arrival
                })

                current_time = next_arrival
                continue

            # Select the shortest burst time
            available.sort(
                key=lambda p: (
                    p.burst_time,
                    p.arrival_time,
                    p.pid
                )
            )

            process = available[0]
            process.start_time = current_time
            start = current_time
            current_time += process.burst_time
            end = current_time
            process.completion_time = end
            process.finished = True
            process.calculate_metrics()
            completed += 1

            self.gantt_chart.append({
                "pid": process.pid,
                "start": start,
                "end": end
            })

        self.calculate_statistics()
        return self.results()

    def srtf(self):

        self.reset()
        current_time = 0
        completed = 0
        n = len(self.processes)
        
        while completed < n:

            available = [
                p for p in self.processes
                if p.arrival_time <= current_time and not p.finished
            ]

            if not available:
                future = [
                    p.arrival_time
                    for p in self.processes
                    if not p.finished
                ]

                if not future:
                    break

                next_arrival = min(future)
                self.gantt_chart.append({
                    "pid": "Idle",
                    "start": current_time,
                    "end": next_arrival
                })
                current_time = next_arrival
                continue

            available.sort(
                key=lambda p: (
                    p.remaining_time,
                    p.arrival_time,
                    p.pid
                )
            )

            process = available[0]

            if process.start_time == -1:
                process.start_time = current_time

            start = current_time
            process.remaining_time -= 1
            current_time += 1

            if self.gantt_chart and self.gantt_chart[-1]["pid"] == process.pid and self.gantt_chart[-1]["end"] == start:
                self.gantt_chart[-1]["end"] = current_time
            else:
                self.gantt_chart.append({
                    "pid": process.pid,
                    "start": start,
                    "end": current_time
                })

            if process.remaining_time == 0:
                process.completion_time = current_time
                process.finished = True
                process.calculate_metrics()
                completed += 1

        self.calculate_statistics()

        return self.results()

    def round_robin(self, quantum):
        if quantum <= 0:
            raise ValueError("Quantum must be greater than 0")

        self.reset()

        current_time = 0
        completed = 0
        n = len(self.processes)
        ready_queue = []

        while completed < n:
            for process in sorted(self.processes, key=lambda p: (p.arrival_time, p.pid)):
                if process.arrival_time <= current_time and not process.finished and process not in ready_queue:
                    ready_queue.append(process)

            if not ready_queue:
                future_arrivals = [p.arrival_time for p in self.processes if not p.finished]
                if not future_arrivals:
                    break

                next_arrival = min(future_arrivals)
                self.gantt_chart.append({
                    "pid": "Idle",
                    "start": current_time,
                    "end": next_arrival
                })
                current_time = next_arrival
                continue

            process = ready_queue.pop(0)
            if process.start_time == -1:
                process.start_time = current_time

            slice_time = min(quantum, process.remaining_time)
            start = current_time
            process.remaining_time -= slice_time
            current_time += slice_time

            if self.gantt_chart and self.gantt_chart[-1]["pid"] == process.pid and self.gantt_chart[-1]["end"] == start:
                self.gantt_chart[-1]["end"] = current_time
            else:
                self.gantt_chart.append({
                    "pid": process.pid,
                    "start": start,
                    "end": current_time
                })

            for process_to_enqueue in sorted(self.processes, key=lambda p: (p.arrival_time, p.pid)):
                if process_to_enqueue.arrival_time <= current_time and not process_to_enqueue.finished and process_to_enqueue not in ready_queue and process_to_enqueue is not process:
                    ready_queue.append(process_to_enqueue)

            if process.remaining_time > 0:
                ready_queue.append(process)
            else:
                process.completion_time = current_time
                process.finished = True
                process.calculate_metrics()
                completed += 1

        self.calculate_statistics()
        return self.results()