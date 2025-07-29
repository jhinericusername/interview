from .base import Challenge

class ConnectionPoolChallenge(Challenge):
    def __init__(self):
        super().__init__()
        self.id = "connection-pool"
        self.title = "Fix Database Connection Pool Leak"
        self.difficulty = "Medium"
        self.test_command = "python -m pytest test_pool.py -v"
        
        self.description = """
A Flask API is experiencing connection pool exhaustion under load.

The Problem:
- Database connections aren't being properly released
- The pool exhausts after ~20 requests  
- Error cases leak connections

Your Task:
- Fix the connection leak
- Ensure connections are returned to pool in ALL cases
- Make the code handle concurrent requests properly
"""
        
        self.files = {
            "app.py": '''from flask import Flask, jsonify
import psycopg2
from psycopg2 import pool
import time

app = Flask(__name__)

connection_pool = psycopg2.pool.SimpleConnectionPool(
    1, 20,
    host="localhost",
    database="testdb",
    user="testuser",
    password="testpass"
)

@app.route('/users/<int:user_id>')
def get_user(user_id):
    try:
        conn = connection_pool.getconn()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        time.sleep(0.1)
        
        connection_pool.putconn(conn)
        
        return jsonify({"id": user[0], "name": user[1]})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
''',

            "test_pool.py": '''import unittest
from unittest.mock import Mock, patch
import threading

class MockCursor:
    def execute(self, query, params):
        pass
    
    def fetchone(self):
        return (1, "Test User")

class MockConnection:
    def cursor(self):
        return MockCursor()

class MockPool:
    def __init__(self):
        self.available = 20
        self.in_use = 0
        
    def getconn(self):
        if self.available <= 0:
            raise Exception("Pool exhausted")
        self.available -= 1
        self.in_use += 1
        return MockConnection()
    
    def putconn(self, conn):
        self.available += 1
        self.in_use -= 1

class TestConnectionPool(unittest.TestCase):
    def setUp(self):
        self.pool_patch = patch('psycopg2.pool.SimpleConnectionPool')
        mock_pool_class = self.pool_patch.start()
        self.mock_pool = MockPool()
        mock_pool_class.return_value = self.mock_pool
        
        global app
        from app import app
        self.app = app.test_client()
        
    def tearDown(self):
        self.pool_patch.stop()
        
    def test_connection_leak_on_404(self):
        """Test that connections are returned even on 404"""
        initial_available = self.mock_pool.available
        
        with patch('app.MockCursor.fetchone', return_value=None):
            response = self.app.get('/users/999')
            self.assertEqual(response.status_code, 404)
        
        self.assertEqual(self.mock_pool.available, initial_available)
        self.assertEqual(self.mock_pool.in_use, 0)
        
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        results = []
        
        def make_request():
            try:
                resp = self.app.get('/users/1')
                results.append(resp.status_code)
            except Exception as e:
                results.append(f"error: {e}")
        
        threads = []
        for _ in range(25):
            t = threading.Thread(target=make_request)
            threads.append(t)
            t.start()
            
        for t in threads:
            t.join()
            
        self.assertEqual(self.mock_pool.in_use, 0)
        
        successful = [r for r in results if r == 200]
        self.assertGreater(len(successful), 0)

if __name__ == '__main__':
    unittest.main()
''',

            "requirements.txt": "flask\npsycopg2-binary\npytest"
        }
        
        self.solution = {
            "app.py": '''from flask import Flask, jsonify
import psycopg2
from psycopg2 import pool
import time
from contextlib import contextmanager

app = Flask(__name__)

connection_pool = psycopg2.pool.SimpleConnectionPool(
    1, 20,
    host="localhost",
    database="testdb", 
    user="testuser",
    password="testpass"
)

@contextmanager
def get_db_connection():
    """Context manager ensures connections are always returned"""
    conn = connection_pool.getconn()
    try:
        yield conn
    finally:
        connection_pool.putconn(conn)

@app.route('/users/<int:user_id>')
def get_user(user_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                return jsonify({"error": "User not found"}), 404
                
            time.sleep(0.1)
            
            return jsonify({"id": user[0], "name": user[1]})
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
'''
        }
        
        self.hints = [
            "Consider using Python's context managers (with statement)",
            "Make sure connections are returned in ALL code paths",
            "Check what happens when errors occur"
        ]