from datetime import datetime
import sqlite3
from pathlib import Path

class AttendanceDB:
    def __init__(self, db_path='attendance.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Attendance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date TEXT,
                status TEXT,
                slots_count INTEGER DEFAULT 1,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Holidays table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS holidays (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT UNIQUE,
                name TEXT,
                type TEXT
            )
        ''')
        
        # User settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id INTEGER PRIMARY KEY,
                target_attendance INTEGER DEFAULT 70,
                semester_start TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_attendance(self, user_id, date, status, slots_count=1):
        """Add or update attendance record"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if record exists
        cursor.execute('SELECT id FROM attendance WHERE user_id=? AND date=?', (user_id, date))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute(
                'UPDATE attendance SET status=?, slots_count=? WHERE user_id=? AND date=?',
                (status, slots_count, user_id, date)
            )
        else:
            cursor.execute(
                'INSERT INTO attendance (user_id, date, status, slots_count) VALUES (?, ?, ?, ?)',
                (user_id, date, status, slots_count)
            )
        
        conn.commit()
        conn.close()
    
    def get_attendance(self, user_id, date):
        """Get attendance for specific date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT status, slots_count FROM attendance WHERE user_id=? AND date=?', (user_id, date))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def get_attendance_stats(self, user_id, from_date=None, to_date=None):
        """Get attendance statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT status, SUM(slots_count) as count FROM attendance WHERE user_id=?'
        params = [user_id]
        
        if from_date:
            query += ' AND date >= ?'
            params.append(from_date)
        if to_date:
            query += ' AND date <= ?'
            params.append(to_date)
        
        query += ' GROUP BY status'
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        stats = {'present': 0, 'absent': 0, 'leave': 0}
        for row in results:
            stats[row[0]] = row[1]
        
        return stats
    
    def get_all_attendance(self, user_id, limit=20):
        """Get recent attendance records"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT date, status, slots_count FROM attendance WHERE user_id=? ORDER BY date DESC LIMIT ?',
            (user_id, limit)
        )
        results = cursor.fetchall()
        conn.close()
        return results
    
    def add_holiday(self, date, name, holiday_type):
        """Add holiday"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO holidays (date, name, type) VALUES (?, ?, ?)',
                (date, name, holiday_type)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            pass  # Holiday already exists
        conn.close()
    
    def is_holiday(self, date):
        """Check if date is holiday"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM holidays WHERE date=?', (date,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def get_holidays(self, from_date=None, to_date=None, limit=20):
        """Get holidays in range"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT date, name, type FROM holidays'
        params = []
        
        if from_date and to_date:
            query += ' WHERE date BETWEEN ? AND ?'
            params = [from_date, to_date]
        
        query += ' ORDER BY date ASC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results
    
    def set_user_setting(self, user_id, target_attendance):
        """Set user target attendance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT OR REPLACE INTO user_settings (user_id, target_attendance) VALUES (?, ?)',
            (user_id, target_attendance)
        )
        conn.commit()
        conn.close()
    
    def get_user_target(self, user_id):
        """Get user target attendance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT target_attendance FROM user_settings WHERE user_id=?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 70
