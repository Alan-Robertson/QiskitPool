'''
    worker_pool
    Contains the QWorkerPool class
'''

import threading
import time
from queue import Queue
from qiskitpool.job import QJob


class QWorkerPool(threading.Thread):
    '''
        QWorkerPool
        A qiskit worker pool class for a single backend
        Spawned as a single thread, it has two jobs:
            - Confirm current job status
            - Send new jobs to the ibmq backends as they complete
    '''
    def __init__(self, n_workers=5, sleep_time=10):
        '''
            QWorkerPool.__init__
            :: n_workers :: Number of workers that may concurrently send jobs to the ibmq backend
            :: sleep_time :: Time between queue updates
        '''
        self.workers = [None] * n_workers
        self.queue = Queue()
        self.n_workers = n_workers

        self.queue_lock = threading.Lock()
        self.run_lock = threading.Lock()

        self.sleep_time = sleep_time
        self.running = True
        self.finished_jobs = []

        super().__init__()

    def __call__(self, *args, **kwargs):
        '''
            QWorkerPool.__call__
            Wrapper for QWorkerPool.enqueue
        '''
        return self.enqueue(*args, **kwargs)

    def enqueue(self, *args, **kwargs):
        '''
            QWorkerPool.enqueue
            Adds a new job to the queue
            Arguments should be whatever is passed to qiskit.execute
        '''
        self.queue_lock.acquire()
        job = QJob(*args, **kwargs)
        self.queue.put(job)
        self.queue_lock.release()
        return job

    def dequeue(self):
        '''
            QWorkerPool.dequeue
            Returns the first job from the queue
        '''
        self.queue_lock.acquire()
        job = None
        if self.queue.qsize() > 0:
            job = self.queue.get(job)
        self.queue_lock.release()
        return job

    def run(self, *args, **kwargs):
        '''
            QWorkerPool.run
            Loop through jobs, check if they're done, if they are then enqueue the next
        '''

        # Allocate jobs to workers:
        self.run_lock.acquire()
        while self.running:

            for i, worker in enumerate(self.workers):
                if (worker is not None) and worker.poll():
                    # Worker has finished, add it to the finished jobs
                    # Set this worker to None
                    self.finished_jobs.append(self.workers[i])
                    self.workers[i] = None
                    worker = None
                if worker is None:
                    # Current worker has no job, grab a new job from the queue
                    new_worker = self.dequeue()
                    if new_worker is not None:
                        self.workers[i] = new_worker
                        self.workers[i].run()

            self.run_lock.release()
            time.sleep(self.sleep_time)
            self.run_lock.acquire()

        self.run_lock.release()

    def flush(self):
        '''
            Clear finished jobs
        '''
        self.run_lock.acquire()
        self.finished_jobs = []
        self.run_lock.release()

    def free(self):
        '''
            QWorkerPool.free
            Deallocate all workers, cancel all active jobs, then join the thread
        '''
        self.run_lock.acquire()

        workers = self.workers
        for i, worker in enumerate(self.workers):
            if worker is not None:
                try: # May throw an error if the job finishes while trying to cancel
                    worker.cancel()
                except:
                    pass
                workers[i] = None

        self.running = False

        self.run_lock.release()
        self.join()

    def __repr__(self):
        str_rep = "{workers} : Queue: {qsize} Finished: {fsize}".format(
            qsize=self.queue.qsize(),
            workers=''.join(['[X]','[ ]'][i is None] for i in self.workers
            fsize=len(self.finished_jobs)
            )
        )
        return str_rep
