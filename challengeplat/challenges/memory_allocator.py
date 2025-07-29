from .base import Challenge

class MemoryAllocatorChallenge(Challenge):
    def __init__(self):
        super().__init__()
        self.id = "memory-allocator"
        self.title = "Implement Memory Allocator (malloc/free)"
        self.difficulty = "Expert"
        self.test_command = "python -m pytest test_allocator.py -v"
        
        self.description = """
Build a memory allocator like malloc/free that real systems use.

The Problem:
- Need to efficiently allocate and free memory blocks
- Must handle fragmentation (both internal and external)
- Need to be thread-safe for concurrent access
- Performance is critical - used by everything!

Your Task:
- Implement malloc() and free() equivalents
- Handle various allocation patterns efficiently
- Minimize fragmentation
- Implement coalescing of free blocks
- Make it thread-safe
"""
        
        self.files = {
            "allocator.py": '''import threading
import mmap
import os
from typing import Optional, List, Tuple
from dataclasses import dataclass

@dataclass
class Block:
    """Represents a memory block"""
    address: int
    size: int
    is_free: bool
    next_block: Optional['Block'] = None
    prev_block: Optional['Block'] = None

class MemoryAllocator:
    """
    Implement a memory allocator with malloc/free interface.
    
    Requirements:
    1. Efficiently allocate memory blocks of requested size
    2. Free blocks and coalesce adjacent free blocks
    3. Handle fragmentation (try different strategies)
    4. Thread-safe for concurrent access
    5. Good performance for various allocation patterns
    """
    
    def __init__(self, heap_size: int = 1024 * 1024):
        self.heap_size = heap_size
        self.heap_start = 0
        
        self.free_list = Block(address=0, size=heap_size, is_free=True)
        self.allocated_blocks = {}
        
        self.lock = threading.Lock()
        
        self.total_allocated = 0
        self.total_freed = 0
        self.fragmentation_count = 0
        
    def malloc(self, size: int) -> Optional[int]:
        """
        Allocate memory block of given size.
        Returns address of allocated block or None if failed.
        """
        if size <= 0 or size > self.heap_size:
            return None
            
        with self.lock:
            current = self.free_list
            
            while current:
                if current.is_free and current.size >= size:
                    allocated_address = current.address
                    
                    if current.size > size:
                        pass
                    
                    current.is_free = False
                    self.allocated_blocks[allocated_address] = current
                    self.total_allocated += size
                    
                    return allocated_address
                
                current = current.next_block
            
            return None
    
    def free(self, address: int) -> bool:
        """
        Free memory block at given address.
        """
        if address not in self.allocated_blocks:
            return False
            
        with self.lock:
            block = self.allocated_blocks[address]
            
            block.is_free = True
            del self.allocated_blocks[address]
            self.total_freed += block.size
            
            self._coalesce_free_blocks(block)
            
            return True
    
    def _coalesce_free_blocks(self, block: Block):
        """Merge adjacent free blocks to reduce fragmentation"""
        pass
    
    def get_fragmentation(self) -> float:
        """Calculate external fragmentation ratio"""
        with self.lock:
            total_free = 0
            largest_free = 0
            
            current = self.free_list
            while current:
                if current.is_free:
                    total_free += current.size
                    largest_free = max(largest_free, current.size)
                current = current.next_block
            
            if total_free == 0:
                return 0.0
            
            return (total_free - largest_free) / total_free
    
    def get_stats(self) -> dict:
        """Get allocator statistics"""
        return {
            'total_allocated': self.total_allocated,
            'total_freed': self.total_freed,
            'fragmentation': self.get_fragmentation(),
            'active_blocks': len(self.allocated_blocks)
        }

class BuddyAllocator(MemoryAllocator):
    """
    Implement buddy system allocator.
    - Splits memory into powers of 2
    - Reduces external fragmentation
    - Fast coalescing
    """
    pass

class SlabAllocator(MemoryAllocator):
    """
    Implement slab allocator for fixed-size objects.
    - Pre-allocate slabs for common sizes
    - Very fast for fixed-size allocations
    - Used in Linux kernel
    """
    pass
''',

            "test_allocator.py": '''import unittest
import threading
import random
import time
from allocator import MemoryAllocator

class TestMemoryAllocator(unittest.TestCase):
    
    def test_basic_allocation(self):
        """Test basic malloc/free operations"""
        allocator = MemoryAllocator(heap_size=1024)
        
        addr1 = allocator.malloc(100)
        self.assertIsNotNone(addr1)
        
        addr2 = allocator.malloc(200)
        self.assertIsNotNone(addr2)
        
        self.assertNotEqual(addr1, addr2)
        
        self.assertTrue(allocator.free(addr1))
        addr3 = allocator.malloc(100)
        self.assertIsNotNone(addr3)
    
    def test_fragmentation_handling(self):
        """Test that allocator handles fragmentation well"""
        allocator = MemoryAllocator(heap_size=10000)
        
        addresses = []
        for i in range(100):
            addr = allocator.malloc(50)
            if addr is not None:
                addresses.append(addr)
        
        for i in range(0, len(addresses), 2):
            allocator.free(addresses[i])
        
        medium_addr = allocator.malloc(45)
        self.assertIsNotNone(medium_addr, "Failed to allocate after fragmentation")
        
        frag = allocator.get_fragmentation()
        self.assertLess(frag, 0.5, f"Fragmentation too high: {frag}")
    
    def test_coalescing(self):
        """Test that adjacent free blocks are coalesced"""
        allocator = MemoryAllocator(heap_size=1000)
        
        addr1 = allocator.malloc(100)
        addr2 = allocator.malloc(100)
        addr3 = allocator.malloc(100)
        
        allocator.free(addr1)
        allocator.free(addr3)
        allocator.free(addr2)
        
        large_addr = allocator.malloc(290)
        self.assertIsNotNone(large_addr, "Coalescing failed")
    
    def test_thread_safety(self):
        """Test concurrent allocations and frees"""
        allocator = MemoryAllocator(heap_size=100000)
        addresses = []
        errors = []
        
        def allocate_and_free():
            try:
                local_addrs = []
                for _ in range(50):
                    size = random.randint(10, 100)
                    addr = allocator.malloc(size)
                    if addr is not None:
                        local_addrs.append(addr)
                
                time.sleep(random.uniform(0.001, 0.01))
                
                for addr in local_addrs[::2]:
                    allocator.free(addr)
                    
            except Exception as e:
                errors.append(str(e))
        
        threads = []
        for _ in range(10):
            t = threading.Thread(target=allocate_and_free)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        self.assertEqual(len(errors), 0, f"Thread safety errors: {errors}")
    
    def test_allocation_patterns(self):
        """Test various allocation patterns"""
        allocator = MemoryAllocator(heap_size=50000)
        
        for size in range(10, 100, 10):
            addr = allocator.malloc(size)
            self.assertIsNotNone(addr)
        
        random_addrs = []
        for _ in range(100):
            size = random.randint(5, 200)
            addr = allocator.malloc(size)
            if addr is not None:
                random_addrs.append(addr)
        
        addr = allocator.malloc(1000)
        self.assertIsNotNone(addr)
        allocator.free(addr)
        addr2 = allocator.malloc(1000)
        self.assertEqual(addr, addr2, "Should reuse freed block")
    
    def test_performance(self):
        """Basic performance benchmark"""
        allocator = MemoryAllocator(heap_size=1000000)
        
        start_time = time.time()
        
        addresses = []
        for _ in range(1000):
            addr = allocator.malloc(random.randint(50, 500))
            if addr is not None:
                addresses.append(addr)
        
        for addr in addresses[::2]:
            allocator.free(addr)
        
        for _ in range(500):
            allocator.malloc(random.randint(50, 500))
        
        elapsed = time.time() - start_time
        
        self.assertLess(elapsed, 1.0, f"Too slow: {elapsed:.3f}s")
        
        stats = allocator.get_stats()
        print(f"\\nAllocator stats: {stats}")

if __name__ == '__main__':
    unittest.main()
''',

            "requirements.txt": "pytest"
        }
        
        self.solution = None  # Expert challenge - no solution provided
        
        self.hints = [
            "Adjacent free blocks should be merged",
            "Consider different allocation strategies (first-fit, best-fit)",
            "Thread safety is critical"
        ]