import unittest
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
