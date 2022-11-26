import subprocess
import os
import psutil
import signal
from pathlib import Path
from multiprocessing import Process, Queue


class Task:
    TERM_CMD = "DONE"
    EMPTY_CMD = ""

    def __init__(self, cmd, out_dir, func=None, func_arg=None):
        self.cmd = cmd
        self.out_dir = out_dir
        self.func = func
        self.func_arg = func_arg


class Worker(Process):
    def __init__(self, tasks_queue, worker_id, results_queue):
        super(Worker, self).__init__()
        self.tasks_queue = tasks_queue
        self.worker_id = worker_id
        self.num_tasks = 0
        self.results_queue = results_queue

    def run(self):
        while True:
            task = self.tasks_queue.get()
            assert isinstance(task, Task)
            if task.cmd == Task.TERM_CMD:
                print(f"Worker #{self.worker_id} will exit! {self.num_tasks} tasks finished.")
                break

            if task.func is not None:
                self.results_queue.put(task.func(task.func_arg))

            if task.cmd != Task.EMPTY_CMD:
                Path(task.out_dir).mkdir(parents=True, exist_ok=True)
                out = open(os.path.join(task.out_dir, "out.txt"), "w")
                err = open(os.path.join(task.out_dir, "err.txt"), "w")
                print(f"[Worker {self.worker_id}]: {task.cmd}")
                ret = subprocess.run(task.cmd.split(" "), stdout=out, stderr=err).returncode
                if ret != 0:
                    subprocess.run(["touch", os.path.join(task.out_dir, "aborted")])
                else:
                    subprocess.run(["touch", os.path.join(task.out_dir, "completed")])

            self.num_tasks += 1


def kill_child_process(parent_pid, sig=signal.SIGTERM):
    try:
        parent = psutil.Process(parent_pid)
    except psutil.NoSuchProcess:
        return
    children = parent.children(recursive=True)
    for process in children:
        process.send_signal(sig)


default_config = {
    "num_workers": 3,
    "tasks": [Task("echo hello", "./build/{0}".format(i)) for i in range(0, 10)]
}


def run(config):
    pid = os.getpid()

    def stop_signal_handler(signum, frame):
        if os.getpid() == pid:
            print("Killing proc {0} and its children...".format(pid))
            kill_child_process(pid)
        exit(signum)

    signal.signal(signal.SIGTERM, stop_signal_handler)
    signal.signal(signal.SIGINT, stop_signal_handler)

    num_workers = config["num_workers"]
    tasks = config["tasks"]

    tasks_queue = Queue()
    for t in tasks:
        tasks_queue.put(t)

    results_queue = Queue()

    workers = []
    for i in range(0, num_workers):
        w = Worker(tasks_queue, i, results_queue)
        workers.append(w)
        w.start()
        tasks_queue.put(Task(Task.TERM_CMD, None))

    for w in workers:
        w.join()

    results_queue.put(Task.TERM_CMD)
    return results_queue


if __name__ == '__main__':
    run(default_config)
