from .base import Challenge

class DistributedLockChallenge(Challenge):
    def __init__(self):
        super().__init__()
        self.id = "distributed-lock"
        self.title = "Implement Distributed Lock with Leader Election"
        self.difficulty = "Expert"
        self.test_command = "python -m pytest test_distributed.py -v"
        
        self.description = """
Build a distributed locking system that handles network partitions and leader failures.

The Problem:
- Multiple services need to coordinate access to a shared resource
- Network partitions can occur (split-brain scenario)
- The current leader might crash without releasing the lock
- Need to prevent two services from thinking they have the lock

Your Task:
- Implement a distributed lock with leader election
- Handle network partitions gracefully
- Implement heartbeat/lease mechanism
- Ensure safety: never two lock holders
- Ensure liveness: system recovers from failures
"""
        
        self.files = {
            "distributed_lock.py": '''import time
import threading
import random
from typing import Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class Node:
    """Represents a node in the distributed system"""
    node_id: str
    is_alive: bool = True
    last_heartbeat: datetime = None
    
class DistributedLock:
    """
    Implement a distributed lock with leader election.
    
    Requirements:
    1. Only one node can hold the lock at a time
    2. If lock holder dies, another node should acquire it
    3. Handle network partitions (nodes can't communicate)
    4. Implement lease/heartbeat mechanism
    """
    
    def __init__(self, node_id: str, nodes: List[str], lease_duration: int = 5):
        self.node_id = node_id
        self.nodes = {nid: Node(nid) for nid in nodes}
        self.lease_duration = lease_duration
        self.current_leader = None
        self.lease_expiry = None
        self.lock = threading.Lock()
        
        self.network_partitions = set()
        
    def acquire_lock(self, timeout: int = 10) -> bool:
        """
        Try to acquire the distributed lock.
        """
        with self.lock:
            if self.current_leader is None:
                self.current_leader = self.node_id
                self.lease_expiry = datetime.now() + timedelta(seconds=self.lease_duration)
                return True
            return False
    
    def release_lock(self) -> bool:
        """Release the lock if we hold it"""
        with self.lock:
            self.current_leader = None
            self.lease_expiry = None
            return True
    
    def extend_lease(self) -> bool:
        """Extend our lease if we're the leader"""
        with self.lock:
            if self.current_leader == self.node_id:
                self.lease_expiry = datetime.now() + timedelta(seconds=self.lease_duration)
                return True
            return False
    
    def is_leader(self) -> bool:
        """Check if this node is the current leader"""
        return self.current_leader == self.node_id
    
    def get_leader(self) -> Optional[str]:
        """Get current leader with lease validation"""
        return self.current_leader
    
    def set_network_partition(self, unreachable_nodes: List[str]):
        """Simulate network partition - can't reach these nodes"""
        self.network_partitions = set(unreachable_nodes)
    
    def can_reach_node(self, node_id: str) -> bool:
        """Check if we can communicate with a node"""
        return node_id not in self.network_partitions

def has_majority(supporters: int, total_nodes: int) -> bool:
    """Check if we have majority support"""
    return supporters > total_nodes // 2

def elect_leader(nodes: Dict[str, Node], can_reach_func) -> Optional[str]:
    """
    Implement leader election algorithm.
    Should return the node with lowest ID that has majority support.
    """
    pass
''',

            "test_distributed.py": '''import unittest
import threading
import time
from distributed_lock import DistributedLock

class TestDistributedLock(unittest.TestCase):
    
    def test_single_leader(self):
        """Only one node should be able to acquire the lock"""
        nodes = ['node1', 'node2', 'node3']
        locks = [DistributedLock(node_id, nodes) for node_id in nodes]
        
        results = []
        threads = []
        
        def try_acquire(lock):
            results.append(lock.acquire_lock())
        
        for lock in locks:
            t = threading.Thread(target=try_acquire, args=(lock,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        self.assertEqual(sum(results), 1, "Multiple nodes acquired the lock!")
    
    def test_leader_failure_recovery(self):
        """System should recover when leader fails"""
        nodes = ['node1', 'node2', 'node3']
        lock1 = DistributedLock('node1', nodes, lease_duration=2)
        lock2 = DistributedLock('node2', nodes, lease_duration=2)
        
        self.assertTrue(lock1.acquire_lock())
        self.assertTrue(lock1.is_leader())
        
        time.sleep(3)
        
        self.assertTrue(lock2.acquire_lock())
        self.assertTrue(lock2.is_leader())
        self.assertFalse(lock1.is_leader())
    
    def test_network_partition(self):
        """Handle split-brain scenario"""
        nodes = ['node1', 'node2', 'node3', 'node4', 'node5']
        
        locks = {
            'node1': DistributedLock('node1', nodes),
            'node2': DistributedLock('node2', nodes),
            'node3': DistributedLock('node3', nodes),
            'node4': DistributedLock('node4', nodes),
            'node5': DistributedLock('node5', nodes),
        }
        
        locks['node1'].set_network_partition(['node3', 'node4', 'node5'])
        locks['node2'].set_network_partition(['node3', 'node4', 'node5'])
        locks['node3'].set_network_partition(['node1', 'node2'])
        locks['node4'].set_network_partition(['node1', 'node2'])
        locks['node5'].set_network_partition(['node1', 'node2'])
        
        minority_result = locks['node1'].acquire_lock()
        majority_result = locks['node3'].acquire_lock()
        
        self.assertFalse(minority_result, "Minority partition acquired lock!")
        self.assertTrue(majority_result, "Majority partition failed to acquire lock")
    
    def test_concurrent_lease_extension(self):
        """Test that lease extension maintains exclusivity"""
        nodes = ['node1', 'node2', 'node3']
        lock1 = DistributedLock('node1', nodes, lease_duration=1)
        lock2 = DistributedLock('node2', nodes, lease_duration=1)
        
        self.assertTrue(lock1.acquire_lock())
        
        stop_extending = threading.Event()
        
        def keep_extending():
            while not stop_extending.is_set():
                lock1.extend_lease()
                time.sleep(0.5)
        
        extender = threading.Thread(target=keep_extending)
        extender.start()
        
        time.sleep(2)
        self.assertFalse(lock2.acquire_lock(timeout=1))
        
        stop_extending.set()
        extender.join()
        
        time.sleep(2)
        self.assertTrue(lock2.acquire_lock())

if __name__ == '__main__':
    unittest.main()
''',

            "requirements.txt": "pytest"
        }
        
        self.solution = {
            "distributed_lock.py": '''import time
import threading
import random
from typing import Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class Node:
    """Represents a node in the distributed system"""
    node_id: str
    is_alive: bool = True
    last_heartbeat: datetime = None
    
class DistributedLock:
    """
    Distributed lock with leader election using majority consensus.
    """
    
    def __init__(self, node_id: str, nodes: List[str], lease_duration: int = 5):
        self.node_id = node_id
        self.all_nodes = nodes
        self.nodes = {nid: Node(nid) for nid in nodes}
        self.lease_duration = lease_duration
        self.current_leader = None
        self.lease_expiry = None
        self.lock = threading.Lock()
        self.network_partitions = set()
        
        # Track votes for leader election
        self.votes_received = set()
        self.voted_for = None
        
    def acquire_lock(self, timeout: int = 10) -> bool:
        """
        Try to acquire the distributed lock with majority consensus.
        """
        with self.lock:
            # Check if there's a valid leader
            if self.current_leader and self._is_lease_valid():
                return False
            
            # Count reachable nodes
            reachable_nodes = [n for n in self.all_nodes if self.can_reach_node(n)]
            
            # Need majority of ALL nodes, not just reachable ones
            if len(reachable_nodes) <= len(self.all_nodes) // 2:
                return False  # Don't have majority
            
            # Try to become leader
            votes = 1  # Vote for self
            for node in reachable_nodes:
                if node != self.node_id:
                    # In real implementation, would send vote request
                    # For now, simulate that nodes vote for lowest ID
                    if self.node_id < node:
                        votes += 1
            
            if votes > len(self.all_nodes) // 2:
                self.current_leader = self.node_id
                self.lease_expiry = datetime.now() + timedelta(seconds=self.lease_duration)
                return True
            
            return False
    
    def release_lock(self) -> bool:
        """Release the lock if we hold it"""
        with self.lock:
            if self.current_leader == self.node_id:
                self.current_leader = None
                self.lease_expiry = None
                return True
            return False
    
    def extend_lease(self) -> bool:
        """Extend our lease if we're the leader with majority support"""
        with self.lock:
            if self.current_leader != self.node_id:
                return False
            
            # Check if we still have majority support
            reachable_nodes = [n for n in self.all_nodes if self.can_reach_node(n)]
            if len(reachable_nodes) <= len(self.all_nodes) // 2:
                # Lost majority, step down
                self.current_leader = None
                self.lease_expiry = None
                return False
            
            self.lease_expiry = datetime.now() + timedelta(seconds=self.lease_duration)
            return True
    
    def is_leader(self) -> bool:
        """Check if this node is the current leader"""
        with self.lock:
            return (self.current_leader == self.node_id and 
                    self._is_lease_valid())
    
    def get_leader(self) -> Optional[str]:
        """Get current leader with lease validation"""
        with self.lock:
            if self._is_lease_valid():
                return self.current_leader
            return None
    
    def set_network_partition(self, unreachable_nodes: List[str]):
        """Simulate network partition - can't reach these nodes"""
        self.network_partitions = set(unreachable_nodes)
    
    def can_reach_node(self, node_id: str) -> bool:
        """Check if we can communicate with a node"""
        return node_id not in self.network_partitions
    
    def _is_lease_valid(self) -> bool:
        """Check if current lease is still valid"""
        if not self.lease_expiry:
            return False
        return datetime.now() < self.lease_expiry

def has_majority(supporters: int, total_nodes: int) -> bool:
    """Check if we have majority support"""
    return supporters > total_nodes // 2

def elect_leader(nodes: Dict[str, Node], can_reach_func) -> Optional[str]:
    """
    Elect leader - lowest ID node that can reach majority.
    """
    node_ids = sorted(nodes.keys())
    total = len(nodes)
    
    for candidate in node_ids:
        reachable = sum(1 for n in nodes if can_reach_func(candidate, n))
        if has_majority(reachable, total):
            return candidate
    
    return None
'''
        }
        
        self.hints = [
            "Consider majority consensus for leader election",
            "Think about network partition scenarios", 
            "Implement proper lease expiration"
        ]