import time
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
