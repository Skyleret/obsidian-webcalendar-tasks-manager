"""
iCalendar to Obsidian Task Sync | MIT License
Compatible with and made to use with obsitian and obsidian-rollover-daily-todos plutin (MIT)
This is NOT an Obsidian plugin.
"""
import os
import sqlite3
import threading
from queue import Queue
from time import sleep
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
from ics import Calendar
import requests

CALENDAR_URL = ""
DB_PATH = Path(__file__).parent / "tasks.db"
BASE_DIR = Path(__file__).parent

class ThreadSafeDB:
    def __init__(self, db_path):
        self.local = threading.local()
        self.db_path = db_path
    
    def get_conn(self):
        if not hasattr(self.local, 'conn'):
            self.local.conn = sqlite3.connect(self.db_path)
            self.local.conn.execute("PRAGMA journal_mode=WAL")
        return self.local.conn

class TaskManager:
    def __init__(self):
        print("📂 Initializing TaskManager...")
        self.db = ThreadSafeDB(DB_PATH)
        self.init_db()
    
    def init_db(self):
        print("🗄️ Initializing database tables...")
        conn = self.db.get_conn()
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    name TEXT,
                    due_date TEXT,
                    PRIMARY KEY (name, due_date)
                ) WITHOUT ROWID
            """)
        print("✅ Database ready")

    def get_new_tasks(self):
        print("\n🔄 Fetching calendar updates...")
        try:
            https_url = CALENDAR_URL.replace('webcal://', 'https://')
            print(f"🌐 Connecting to: {https_url}")
            
            response = requests.get(
                https_url,
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=10
            )
            response.raise_for_status()
            
            calendar = Calendar(response.text)
            event_count = len(list(calendar.events))
            print(f"📅 Found {event_count} events in calendar")

            new_tasks = []
            conn = self.db.get_conn()
            with conn:
                cursor = conn.cursor()
                for event in calendar.events:
                    name = event.name.strip()
                    due_date = event.begin.strftime('%Y-%m-%d')
                    
                    cursor.execute(
                        "SELECT 1 FROM tasks WHERE name=? AND due_date=?",
                        (name, due_date)
                    )
                    if not cursor.fetchone():
                        print(f"➕ New task found: {name} (@{due_date})")
                        new_tasks.append((name, due_date))
                        cursor.execute(
                            "INSERT INTO tasks VALUES (?, ?)",
                            (name, due_date)
                        )
            
            print(f"🔍 Found {len(new_tasks)} new tasks")
            return new_tasks
            
        except Exception as e:
            print(f"❌ Error fetching tasks: {e}")
            return []

class MarkdownHandler(FileSystemEventHandler):
    def __init__(self, processor):
        self.processor = processor
        self.processed_files = set()
        self.task_queue = Queue()
        self.worker_started = False
        print("👀 File watcher initialized")
    
    def start_worker(self):
        if not self.worker_started:
            worker = threading.Thread(target=self._process_queue, daemon=True)
            worker.start()
            self.worker_started = True
    
    def _process_queue(self):
        while True:
            src_path = self.task_queue.get()
            try:
                if not src_path.endswith('.md'):
                    continue
                    
                file_path = Path(src_path)
                try:
                    file_date = file_path.stem
                    datetime.strptime(file_date, "%Y-%m-%d")
                except ValueError:
                    continue
                    
                if src_path in self.processed_files:
                    continue
                    
                self.processed_files.add(src_path)
                sleep(0.5)
                
                new_tasks = self.processor.get_new_tasks()
                if new_tasks:
                    with open(src_path, 'a') as f:
                        f.write("\n" + "\n".join(f"- [ ] {n}(@{d})" for n,d in new_tasks) + "\n")
                
            except Exception as e:
                print(f"🔥 Error processing file: {e}")
            finally:
                self.task_queue.task_done()
    
    def on_created(self, event):
        if not event.is_directory:
            self.start_worker()
            self.task_queue.put(event.src_path)
def start_monitor():
    print("\n" + "="*50)
    print(f"🚀 Starting task monitor in {BASE_DIR}")
    print("="*50 + "\n")
    
    observer = Observer()
    processor = TaskManager()
    handler = MarkdownHandler(processor)
    
    observer.schedule(handler, str(BASE_DIR), recursive=True)
    observer.start()
    print("\n🛠️ Monitoring active. Waiting for file changes...")
    
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping monitor...")
        observer.stop()
    observer.join()
    print("👋 Monitor stopped")

if __name__ == "__main__":
    start_monitor()
