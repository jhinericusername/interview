from .base import Challenge

class AnalyticsOptimizationChallenge(Challenge):
    def __init__(self):
        super().__init__()
        self.id = "analytics-optimization"
        self.title = "Optimize Analytics Engine"
        self.difficulty = "Hard"
        self.test_command = "python -m pytest test_analytics.py -v"
        
        self.description = """
An analytics engine is running too slowly as data grows.
The current implementation has O(n²) complexity and needs optimization.

The Problem:
- Processing 10k events takes over 30 seconds
- Memory usage grows exponentially
- Dashboard timeouts are common

Your Task:
- Optimize from O(n²) to O(n log n) or better
- Maintain exact same output/functionality
- Reduce memory usage
"""
        
        self.files = {
            "analytics.py": '''from datetime import datetime, timedelta
from typing import List, Dict

class Event:
    def __init__(self, user_id: str, timestamp: datetime, action: str):
        self.user_id = user_id
        self.timestamp = timestamp
        self.action = action

class AnalyticsEngine:
    def __init__(self):
        self.events = []
    
    def add_event(self, event: Event):
        self.events.append(event)
    
    def get_user_sessions(self, user_id: str, gap_minutes: int = 30) -> List[List[Event]]:
        """Group user events into sessions based on time gaps"""
        user_events = []
        for event in self.events:
            if event.user_id == user_id:
                user_events.append(event)
        
        if not user_events:
            return []
        
        for i in range(len(user_events)):
            for j in range(0, len(user_events) - i - 1):
                if user_events[j].timestamp > user_events[j + 1].timestamp:
                    user_events[j], user_events[j + 1] = user_events[j + 1], user_events[j]
        
        sessions = []
        current_session = [user_events[0]]
        
        for i in range(1, len(user_events)):
            time_diff = user_events[i].timestamp - user_events[i-1].timestamp
            if time_diff > timedelta(minutes=gap_minutes):
                sessions.append(current_session)
                current_session = [user_events[i]]
            else:
                current_session.append(user_events[i])
        
        sessions.append(current_session)
        return sessions
    
    def get_active_users_count(self, start_time: datetime, end_time: datetime) -> int:
        """Count unique active users in time range"""
        active_users = set()
        
        for event in self.events:
            if start_time <= event.timestamp <= end_time:
                found = False
                for user in active_users:
                    if user == event.user_id:
                        found = True
                        break
                if not found:
                    active_users.add(event.user_id)
        
        return len(active_users)
''',

            "test_analytics.py": '''import unittest
import time
from datetime import datetime, timedelta
import random
import string
from analytics import AnalyticsEngine, Event

class TestAnalyticsPerformance(unittest.TestCase):
    def generate_events(self, num_events, num_users):
        """Generate test events"""
        events = []
        base_time = datetime.now()
        
        for i in range(num_events):
            user_id = f"user_{random.randint(1, num_users)}"
            timestamp = base_time + timedelta(minutes=random.randint(0, 1000))
            action = random.choice(['click', 'view', 'purchase'])
            events.append(Event(user_id, timestamp, action))
        
        return events
    
    def test_session_performance(self):
        """Test that session detection is efficient"""
        engine = AnalyticsEngine()
        
        events = self.generate_events(5000, 100)
        for event in events:
            engine.add_event(event)
        
        start = time.time()
        sessions = engine.get_user_sessions("user_1")
        elapsed = time.time() - start
        
        self.assertLess(elapsed, 0.1, f"Too slow: {elapsed:.3f}s")
    
    def test_active_users_performance(self):
        """Test active users count performance"""
        engine = AnalyticsEngine()
        
        events = self.generate_events(10000, 500)
        for event in events:
            engine.add_event(event)
        
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=1)
        
        start = time.time()
        count = engine.get_active_users_count(start_time, end_time)
        elapsed = time.time() - start
        
        self.assertLess(elapsed, 0.05, f"Too slow: {elapsed:.3f}s")
    
    def test_correctness(self):
        """Ensure optimization maintains correctness"""
        engine = AnalyticsEngine()
        
        base = datetime.now()
        events = [
            Event("user1", base, "click"),
            Event("user1", base + timedelta(minutes=10), "view"),
            Event("user1", base + timedelta(minutes=50), "click"),
            Event("user2", base + timedelta(minutes=5), "view"),
        ]
        
        for e in events:
            engine.add_event(e)
        
        sessions = engine.get_user_sessions("user1", gap_minutes=30)
        self.assertEqual(len(sessions), 2)
        self.assertEqual(len(sessions[0]), 2)
        self.assertEqual(len(sessions[1]), 1)
        
        count = engine.get_active_users_count(base, base + timedelta(hours=1))
        self.assertEqual(count, 2)

if __name__ == '__main__':
    unittest.main()
''',

            "requirements.txt": "pytest"
        }
        
        self.solution = {
            "analytics.py": '''from datetime import datetime, timedelta
from typing import List, Dict
from collections import defaultdict

class Event:
    def __init__(self, user_id: str, timestamp: datetime, action: str):
        self.user_id = user_id
        self.timestamp = timestamp
        self.action = action

class AnalyticsEngine:
    def __init__(self):
        self.events = []
        self.events_by_user = defaultdict(list)
    
    def add_event(self, event: Event):
        self.events.append(event)
        self.events_by_user[event.user_id].append(event)
    
    def get_user_sessions(self, user_id: str, gap_minutes: int = 30) -> List[List[Event]]:
        """Optimized O(n log n) session detection"""
        user_events = self.events_by_user.get(user_id, [])
        
        if not user_events:
            return []
        
        sorted_events = sorted(user_events, key=lambda e: e.timestamp)
        
        sessions = []
        current_session = [sorted_events[0]]
        
        for i in range(1, len(sorted_events)):
            time_diff = sorted_events[i].timestamp - sorted_events[i-1].timestamp
            if time_diff > timedelta(minutes=gap_minutes):
                sessions.append(current_session)
                current_session = [sorted_events[i]]
            else:
                current_session.append(sorted_events[i])
        
        sessions.append(current_session)
        return sessions
    
    def get_active_users_count(self, start_time: datetime, end_time: datetime) -> int:
        """Optimized O(n) active users count"""
        active_users = set()
        
        for event in self.events:
            if start_time <= event.timestamp <= end_time:
                active_users.add(event.user_id)
        
        return len(active_users)
'''
        }
        
        self.hints = [
            "Bubble sort is O(n²) - use built-in sort instead",
            "Pre-indexing data can turn O(n) lookups into O(1)",
            "Sets are more efficient than lists for membership testing"
        ]