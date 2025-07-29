import os
import sys
import subprocess
import shutil
import time
from pathlib import Path
from typing import List, Optional

from challenges import (
    ConnectionPoolChallenge,
    CacheStampedeChallenge,
    AnalyticsOptimizationChallenge,
    DistributedLockChallenge,
    WriteAheadLogChallenge,
    MemoryAllocatorChallenge
)

class ChallengeRunner:
    def __init__(self):
        self.challenges = [
            ConnectionPoolChallenge(),
            CacheStampedeChallenge(),
            AnalyticsOptimizationChallenge(),
            DistributedLockChallenge(),
            WriteAheadLogChallenge(),
            MemoryAllocatorChallenge()
        ]
        self.workspace_dir = Path("workspace")
    
    def run(self):
        while True:
            self.show_menu()
            choice = input("\nSelect option: ")
            
            if choice == '1':
                self.list_challenges()
            elif choice == '2':
                self.start_challenge()
            elif choice == '3':
                break
            else:
                print("Invalid option")
    
    def show_menu(self):
        print("\nCHALLENGE PLATFORM")
        print("-" * 40)
        print("1. List challenges")
        print("2. Start challenge")
        print("3. Exit")
    
    def list_challenges(self):
        print("\nAvailable Challenges:")
        print("-" * 40)
        for i, challenge in enumerate(self.challenges, 1):
            print(f"{i}. {challenge.title} [{challenge.difficulty}]")
    
    def start_challenge(self):
        self.list_challenges()
        try:
            idx = int(input("\nSelect challenge number: ")) - 1
            if 0 <= idx < len(self.challenges):
                self.run_challenge(self.challenges[idx])
            else:
                print("Invalid challenge number")
        except ValueError:
            print("Please enter a number")
    
    def run_challenge(self, challenge):
        print(f"\nStarting: {challenge.title}")
        print("-" * 40)
        print(challenge.description)
        
        # Setup workspace
        if self.workspace_dir.exists():
            shutil.rmtree(self.workspace_dir)
        self.workspace_dir.mkdir()
        
        # Write files
        for filename, content in challenge.files.items():
            filepath = self.workspace_dir / filename
            filepath.write_text(content)
        
        print(f"\nFiles created in: {self.workspace_dir}/")
        print("\nFiles:")
        for filename in challenge.files:
            print(f"  - {filename}")
        
        print(f"\nTest command: {challenge.test_command}")
        print("\nEdit the files and press Enter when ready to submit...")
        
        start_time = time.time()
        input()
        
        self.evaluate_solution(challenge, time.time() - start_time)
    
    def evaluate_solution(self, challenge, time_taken):
        print("\nRunning tests...")
        print("-" * 40)
        
        original_dir = os.getcwd()
        os.chdir(self.workspace_dir)
        
        try:
            # Install dependencies if needed
            if "requirements.txt" in challenge.files:
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"], 
                             capture_output=True)
            elif "package.json" in challenge.files:
                subprocess.run(["npm", "install", "--silent"], capture_output=True)
            
            # Run tests
            result = subprocess.run(
                challenge.test_command.split(),
                capture_output=True,
                text=True
            )
            
            os.chdir(original_dir)
            
            if result.returncode == 0:
                print("TESTS PASSED")
                print(f"Time: {int(time_taken)}s")
                
                if input("\nShow solution? (y/n): ").lower() == 'y':
                    self.show_solution(challenge)
            else:
                print("TESTS FAILED\n")
                print(result.stdout)
                if result.stderr:
                    print("\nErrors:")
                    print(result.stderr)
                
                if hasattr(challenge, 'hints'):
                    print("\nHints:")
                    for hint in challenge.hints:
                        print(f"- {hint}")
                
                if input("\nTry again? (y/n): ").lower() == 'y':
                    self.run_challenge(challenge)
        
        except Exception as e:
            os.chdir(original_dir)
            print(f"Error: {e}")
    
    def show_solution(self, challenge):
        if not challenge.solution:
            print("\nNo solution available")
            return
        
        print("\nSOLUTION")
        print("-" * 40)
        for filename, content in challenge.solution.items():
            print(f"\n{filename}:")
            print(content)