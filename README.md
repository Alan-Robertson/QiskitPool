## QiskitPool ##
A simple threadpool for qiskit's backends. 

The qiksit backend accepts five jobs at a time, before it throws 400's back at the user. 
This little thread pool will simply accrue jobs up to that limit (or up to a user specified threshold), 
before queueing the rest. The jobs will be released as the older ones finish. 

## Installation ##

As usual for a Python module
```bash
pip install -r requirements.txt
python setup.py install
```

## Usage ## 
There's a jupyter notebook with some example code, but for those that don't want to have to look through all that:

```python
import qiskitpool

# Give the pool your provider so it knows what backends it's expecting
pool = qiskitpool.QPool(provider)

job = pool(circuit, backend, shots=n_shots)
```
To check if the job has finished you can:
```python
job.poll()
```
And to get the result you can:
```python
job.result()
```

Lastly you can print the pool object to see what it's up to:
```python
print(pool)
```
This one has 17 jobs in the local queue for the statevector simulator,
with three currently in the qiskit queue
```
ibmq_qasm_simulator:	[ ][ ][ ][ ][ ] : 0
ibmq_lima:	[ ][ ][ ][ ][ ] : 0
ibmq_belem:	[ ][ ][ ][ ][ ] : 0
ibmq_quito:	[ ][ ][ ][ ][ ] : 0
simulator_statevector:	[X][X][X][ ][ ] : 17
simulator_mps:	[ ][ ][ ][ ][ ] : 0
simulator_extended_stabilizer:	[ ][ ][ ][ ][ ] : 0
simulator_stabilizer:	[ ][ ][ ][ ][ ] : 0
ibmq_manila:	[ ][ ][ ][ ][ ] : 0
ibm_nairobi:	[ ][ ][ ][ ][ ] : 0
ibm_oslo:	[ ][ ][ ][ ][ ] : 0
```

## TODO ##
Things that I might or might not get around to.

- Specify backends rather than the whole provider
- Move to a local server approach to syncrhonise between different Python processes on the same device
