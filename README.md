# Coding Challenge Platform

A terminal-based platform for practicing real-world coding challenges. Unlike traditional algorithmic puzzles, these challenges simulate actual problems developers face in production systems.

## Features

- **Real-world problems**: Fix database connection leaks, solve cache stampedes, optimize performance bottlenecks
- **Multiple difficulty levels**: From Medium to Expert
- **Instant feedback**: Tests run automatically and provide detailed error messages
- **Clean interface**: Simple terminal UI focused on the problems
- **Multiple languages**: Challenges in Python, JavaScript/Node.js
- **Learning focused**: Includes hints and reference solutions

## Quick Start

### 1. Clone the repository
```bash
git clone <repository-url>
cd challenge-platform
```

### 2. Run the platform
```bash
python main.py
```

### 3. Select a challenge
```
CHALLENGE PLATFORM
----------------------------------------
1. List challenges
2. Start challenge
3. Exit

Select option: 2
```

### 4. Solve the challenge
- Files are created in the `workspace/` directory
- Edit them with your preferred editor
- Press Enter when ready to submit
- Tests run automatically

## Available Challenges

### Medium Difficulty
1. **Fix Database Connection Pool Leak** (Python/Flask)
   - Debug a resource leak in a web application
   - Learn about context managers and error handling

2. **Fix Cache Stampede Problem** (Node.js/Express)
   - Solve a concurrency issue in a caching system
   - Understand race conditions and promises

### Hard Difficulty
3. **Optimize Analytics Engine** (Python)
   - Transform O(n²) algorithms to O(n log n)
   - Practice algorithm optimization and data structures

### Expert Difficulty
4. **Implement Distributed Lock** (Python)
   - Build a distributed locking mechanism with leader election
   - Learn about consensus and network partitions

5. **Build Write-Ahead Log** (Python)
   - Implement database durability guarantees
   - Understand ACID properties and crash recovery

6. **Implement Memory Allocator** (Python)
   - Create a malloc/free implementation
   - Handle fragmentation and thread safety

## Project Structure

```
challenge-platform/
├── main.py                    # Entry point
├── challenge_runner.py        # Core platform logic
├── challenges/
│   ├── __init__.py
│   ├── base.py               # Base challenge class
│   ├── connection_pool.py    # Challenge implementations
│   ├── cache_stampede.py
│   ├── analytics_optimization.py
│   ├── distributed_lock.py
│   ├── write_ahead_log.py
│   └── memory_allocator.py
└── workspace/                # Created at runtime for challenge files
```

## Requirements

- Python 3.6+
- For specific challenges:
  - Python challenges: `pytest`
  - Node.js challenges: `npm` and `node`

Dependencies are installed automatically when running each challenge.

## How It Works

1. **Select a challenge**: Each challenge simulates a real bug or performance issue
2. **Understand the problem**: Read the description and examine the test failures
3. **Fix the code**: Edit the files in `workspace/` using any editor
4. **Submit solution**: Tests run automatically and provide immediate feedback
5. **Learn from solutions**: View reference implementations after solving

## Example Session

```bash
$ python main.py

CHALLENGE PLATFORM
----------------------------------------
1. List challenges
2. Start challenge  
3. Exit

Select option: 2

Available Challenges:
----------------------------------------
1. Fix Database Connection Pool Leak [Medium]
2. Fix Cache Stampede Problem [Medium]
3. Optimize Analytics Engine [Hard]
4. Implement Distributed Lock [Expert]
5. Build Write-Ahead Log [Expert]
6. Implement Memory Allocator [Expert]

Select challenge number: 1

Starting: Fix Database Connection Pool Leak
----------------------------------------

A Flask API is experiencing connection pool exhaustion under load.

The Problem:
- Database connections aren't being properly released
- The pool exhausts after ~20 requests  
- Error cases leak connections

Your Task:
- Fix the connection leak
- Ensure connections are returned to pool in ALL cases
- Make the code handle concurrent requests properly

Files created in: workspace/

Files:
  - app.py
  - test_pool.py
  - requirements.txt

Test command: python -m pytest test_pool.py -v

Edit the files and press Enter when ready to submit...
```

## Adding New Challenges

To add a new challenge:

1. Create a new file in `challenges/` directory
2. Inherit from the `Challenge` base class
3. Define the problem files, tests, and solution
4. Import it in `challenges/__init__.py`
5. Add it to the challenge list in `challenge_runner.py`

Example:
```python
from .base import Challenge

class MyNewChallenge(Challenge):
    def __init__(self):
        super().__init__()
        self.id = "my-challenge"
        self.title = "My New Challenge"
        self.difficulty = "Medium"
        self.test_command = "python -m pytest test.py"
        self.description = "..."
        self.files = {"main.py": "...", "test.py": "..."}
        self.solution = {"main.py": "..."}
        self.hints = ["Hint 1", "Hint 2"]
```

## Tips for Success

- **Read the tests first**: Understanding what's being tested helps identify the bug
- **Run tests frequently**: Use the test command to check progress
- **Check error messages**: Test output often reveals the exact issue
- **Use the hints**: If stuck, hints provide direction without giving away the solution
- **Learn from solutions**: After solving, study the reference implementation

## Contributing

Contributions are welcome! Ideas for contributions:
- New challenges covering different topics
- Support for additional programming languages
- Improved test coverage
- Better error messages and hints
- Performance benchmarks

## License

MIT License - see LICENSE file for details
