'''
    qiskitpool/pool.py
    Contains the QPool class
'''
from qiskitpool.worker_pool import QWorkerPool

class QPool():
    '''
        QPool
        ThreadPool controller for device backends
    '''
    def __init__(self, provider, jobs_per_device=5, sleep_time=10):
        '''
            QPool.__init__
            :: provider :: Qiskit Provider object
            :: jobs_per_device = 5 :: Number of jobs for each backend device
            :: sleep_time = 10 :: Time to sleep between polling backends
        '''
        self.worker_pools = {
            backend.name():QWorkerPool(n_workers=jobs_per_device, sleep_time=sleep_time)
            for backend in provider.backends()
        }

        self.queue_running = True
        self.jobs_per_device = jobs_per_device
        self.sleep_time = sleep_time

        for backend in self.worker_pools:
            self.worker_pools[backend].start()


    def __call__(self, *args, **kwargs):
        '''
            QPool.__call__
            Wrapper for QPool.enqueue
        '''
        return self.enqueue(*args, **kwargs)

    def enqueue(self, circ, backend, *args, **kwargs):
        '''
            QPool.enqueue
            Adds a new job to the appropriate backend worker pool
            :: circ     :: QuantumCircuit object
            :: backend  :: Backend object
            :: *args    :: Circuit args
            :: **kwargs :: Circuit kwargs
            Returns a job object
        '''
        dev_name = backend.name()
        if dev_name not in self.worker_pools:
            raise Exception("Backend not recognised by provider")

        job = self.worker_pools[dev_name].enqueue(circ, backend, *args, **kwargs)
        return job

    def join(self):
        '''
            QPool.join
            Joins each thread for each worker pool
        '''
        for backend in self.worker_pools:
            self.worker_pools[backend].free()

    def __repr__(self):
        '''
            QPool.__repr__
            Returns the reprs of each worker pool
        '''
        return ''.join(["{}:\t{}\n".format(
            i,
            self.worker_pools[i].__repr__()) for i in self.worker_pools]
        )

    def __str__(self):
        '''
            QPool.__str__
            Wrapper for QPool.__repr__
        '''
        return self.__repr__()
