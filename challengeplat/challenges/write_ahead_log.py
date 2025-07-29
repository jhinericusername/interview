from .base import Challenge

class WriteAheadLogChallenge(Challenge):
    def __init__(self):
        super().__init__()
        self.id = "write-ahead-log"
        self.title = "Build Write-Ahead Log for Database Recovery"
        self.difficulty = "Expert"
        self.test_command = "python -m pytest test_wal.py -v"
        
        self.description = """
Implement a Write-Ahead Log (WAL) system used by databases like PostgreSQL 
for crash recovery and durability guarantees.

The Problem:
- Databases need to recover from crashes without losing committed data
- Need to handle partially written transactions
- Must ensure ACID properties even with power failures
- Performance is critical - can't sync to disk on every write

Your Task:
- Implement a WAL with checkpointing
- Handle crash recovery by replaying the log
- Implement proper fsync strategies
- Support concurrent readers during writes
- Ensure durability without killing performance
"""
        
        self.files = {
            "wal.py": '''import os
import struct
import threading
import mmap
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from enum import Enum

class RecordType(Enum):
    BEGIN = 1
    COMMIT = 2
    ABORT = 3
    UPDATE = 4
    CHECKPOINT = 5

@dataclass
class LogRecord:
    """A record in the WAL"""
    lsn: int
    transaction_id: int
    record_type: RecordType
    data: bytes
    
    def serialize(self) -> bytes:
        """Serialize record to bytes for storage"""
        pass
    
    @staticmethod
    def deserialize(data: bytes) -> 'LogRecord':
        """Deserialize bytes to LogRecord"""
        pass

class WriteAheadLog:
    """
    Implement a Write-Ahead Log for database durability.
    
    Key requirements:
    1. All changes must be logged before being applied
    2. Log records must be flushed to disk before commit returns
    3. Support crash recovery by replaying the log
    4. Implement checkpointing to limit recovery time
    5. Handle torn pages (partial writes during crash)
    """
    
    def __init__(self, log_dir: str, segment_size: int = 16 * 1024 * 1024):
        self.log_dir = log_dir
        self.segment_size = segment_size
        self.current_lsn = 0
        self.lock = threading.RLock()
        
        os.makedirs(log_dir, exist_ok=True)
        
        self.active_transactions: Dict[int, List[LogRecord]] = {}
        
        self.buffer = bytearray()
        self.buffer_lock = threading.Lock()
        
    def begin_transaction(self, txn_id: int) -> int:
        """Start a new transaction"""
        with self.lock:
            self.current_lsn += 1
            record = LogRecord(
                lsn=self.current_lsn,
                transaction_id=txn_id,
                record_type=RecordType.BEGIN,
                data=b''
            )
            self.active_transactions[txn_id] = []
            return self.current_lsn
    
    def log_update(self, txn_id: int, table: str, key: bytes, 
                   old_value: bytes, new_value: bytes) -> int:
        """Log an update operation"""
        with self.lock:
            if txn_id not in self.active_transactions:
                raise ValueError(f"Transaction {txn_id} not active")
            
            self.current_lsn += 1
            return self.current_lsn
    
    def commit_transaction(self, txn_id: int) -> bool:
        """Commit a transaction - must be durable when this returns!"""
        with self.lock:
            if txn_id in self.active_transactions:
                del self.active_transactions[txn_id]
                return True
            return False
    
    def abort_transaction(self, txn_id: int) -> bool:
        """Abort a transaction"""
        pass
    
    def force_log(self, up_to_lsn: Optional[int] = None):
        """Force log records to stable storage"""
        pass
    
    def checkpoint(self) -> int:
        """Create a checkpoint to limit recovery time"""
        pass
    
    def recover(self) -> List[int]:
        """Recover from crash by replaying the log"""
        recovered_txns = []
        return recovered_txns
    
    def get_log_size(self) -> int:
        """Get total size of log files"""
        total = 0
        for file in os.listdir(self.log_dir):
            if file.startswith('wal_'):
                total += os.path.getsize(os.path.join(self.log_dir, file))
        return total

class LogSegment:
    """Represents a single log file segment"""
    def __init__(self, filepath: str, segment_id: int):
        self.filepath = filepath
        self.segment_id = segment_id
        self.file = None
        self.mmap = None
        
    def open(self):
        """Open segment file with memory mapping for performance"""
        pass
    
    def append_record(self, record: LogRecord) -> int:
        """Append record to segment, return offset"""
        pass
    
    def read_record(self, offset: int) -> Optional[LogRecord]:
        """Read record at given offset"""
        pass
''',

            "test_wal.py": '''import unittest
import tempfile
import shutil
import os
import threading
import time
import random
from wal import WriteAheadLog, RecordType

class TestWriteAheadLog(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_basic_durability(self):
        """Test that committed transactions survive crash"""
        wal = WriteAheadLog(self.test_dir)
        
        txn_id = 1
        wal.begin_transaction(txn_id)
        
        wal.log_update(txn_id, "users", b"user1", b"old_data", b"new_data")
        wal.log_update(txn_id, "users", b"user2", b"old_data2", b"new_data2")
        
        self.assertTrue(wal.commit_transaction(txn_id))
        
        wal2 = WriteAheadLog(self.test_dir)
        recovered = wal2.recover()
        
        self.assertIn(txn_id, recovered)
    
    def test_abort_not_recovered(self):
        """Aborted transactions should not be recovered"""
        wal = WriteAheadLog(self.test_dir)
        
        wal.begin_transaction(1)
        wal.log_update(1, "users", b"user1", b"old", b"new")
        wal.commit_transaction(1)
        
        wal.begin_transaction(2)
        wal.log_update(2, "users", b"user2", b"old", b"new")
        wal.abort_transaction(2)
        
        wal.begin_transaction(3)
        wal.log_update(3, "users", b"user3", b"old", b"new")
        
        wal2 = WriteAheadLog(self.test_dir)
        recovered = wal2.recover()
        
        self.assertEqual(recovered, [1])
    
    def test_concurrent_transactions(self):
        """Test multiple concurrent transactions"""
        wal = WriteAheadLog(self.test_dir)
        results = []
        errors = []
        
        def run_transaction(txn_id):
            try:
                wal.begin_transaction(txn_id)
                
                for i in range(10):
                    key = f"key_{txn_id}_{i}".encode()
                    wal.log_update(txn_id, "table", key, b"old", b"new")
                    time.sleep(random.uniform(0.001, 0.01))
                
                if random.random() < 0.3:
                    wal.abort_transaction(txn_id)
                    results.append((txn_id, 'aborted'))
                else:
                    wal.commit_transaction(txn_id)
                    results.append((txn_id, 'committed'))
                    
            except Exception as e:
                errors.append((txn_id, str(e)))
        
        threads = []
        for i in range(20):
            t = threading.Thread(target=run_transaction, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        
        wal2 = WriteAheadLog(self.test_dir)
        recovered = wal2.recover()
        
        committed_txns = [txn_id for txn_id, status in results if status == 'committed']
        for txn_id in committed_txns:
            self.assertIn(txn_id, recovered)
    
    def test_checkpoint_recovery(self):
        """Test that checkpoint limits recovery work"""
        wal = WriteAheadLog(self.test_dir)
        
        for i in range(100):
            wal.begin_transaction(i)
            wal.log_update(i, "table", f"key{i}".encode(), b"old", b"new")
            wal.commit_transaction(i)
        
        checkpoint_lsn = wal.checkpoint()
        
        for i in range(100, 150):
            wal.begin_transaction(i)
            wal.log_update(i, "table", f"key{i}".encode(), b"old", b"new")
            wal.commit_transaction(i)
        
        start_time = time.time()
        wal2 = WriteAheadLog(self.test_dir)
        recovered = wal2.recover()
        recovery_time = time.time() - start_time
        
        self.assertEqual(len(recovered), 150)
        
        self.assertLess(recovery_time, 1.0)

if __name__ == '__main__':
    unittest.main()
''',

            "requirements.txt": "pytest"
        }
        
        self.solution = None  # Expert challenge - no solution provided
        
        self.hints = [
            "All writes must go to log before data",
            "Commits must force log to disk (fsync)",
            "Recovery needs to handle partial writes"
        ]