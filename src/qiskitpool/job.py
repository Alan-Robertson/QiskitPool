'''
    qiskitpool/job.py
    Contains the QJob class
'''
from functools import partial
from qiskit import execute

class QJob():
    '''
        QJob
        Job manager for asynch qiskit backends
    '''
    def __init__(self, *args, qjob_id=None, **kwargs):
        '''
            QJob.__init__
            Initialiser for a qiksit job
            :: *args    :: Args for qiskit execute
            :: **kwargs :: Kwargs for qiskit execute
        '''
        self.job_fn = partial(execute, *args, **kwargs)
        self.job = None
        self.done = False
        self.test_count = 10
        self.qjob_id = qjob_id

    def __call__(self):
        '''
            QJob.__call__
            Wrapper for QJob.run
        '''
        return self.run()

    def run(self):
        '''
            QJob.run
            Send async job to qiskit backend
        '''
        self.job = self.job_fn()
        return self

    def poll(self):
        '''
            QJob.poll
            Poll qiskit backend for job completion status
        '''
        if self.job is not None:
            return self.job.done()
        return False

    def cancel(self):
        '''
            QJob.cancel
            Cancel job on backend
        '''
        if self.job is None:
            return None
        return self.job.cancel()

    def result(self):
        '''
            QJob.result
            Get result from backend
            Non blocking - returns False if a job is not yet ready
        '''
        if self.poll():
            return self.job.result()
        return False
