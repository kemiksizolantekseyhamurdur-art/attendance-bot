from datetime import datetime, timedelta
from config import CLASS_SCHEDULE, HOLIDAYS
from database import AttendanceDB

class AttendanceCalculator:
    def __init__(self, db: AttendanceDB):
        self.db = db
    
    def get_total_classes_today(self):
        """Get number of classes today based on schedule"""
        today = datetime.now()
        weekday = today.weekday()  # 0=Monday, 4=Friday
        
        if weekday > 4:  # Weekend
            return 0
        
        schedule = CLASS_SCHEDULE.get(weekday, [])
        return len(schedule)
    
    def is_class_day(self, date_obj):
        """Check if date is a class day (Mon-Fri)"""
        return date_obj.weekday() < 5
    
    def is_holiday(self, date_str):
        """Check if date is a holiday"""
        holiday_name = self.db.is_holiday(date_str)
        return holiday_name is not None
    
    def get_classes_for_date(self, date_obj):
        """Get classes scheduled for a date"""
        if not self.is_class_day(date_obj):
            return []
        
        weekday = date_obj.weekday()
        return CLASS_SCHEDULE.get(weekday, [])
    
    def calculate_attendance_percentage(self, user_id, from_date=None, to_date=None):
        """Calculate attendance percentage"""
        stats = self.db.get_attendance_stats(user_id, from_date, to_date)
        total = stats['present'] + stats['absent'] + stats['leave']
        
        if total == 0:
            return 0, 0, 0
        
        percentage = (stats['present'] / total) * 100
        return round(percentage, 2), stats['present'], total
    
    def calculate_max_bunk(self, user_id, target_attendance=70):
        """Calculate how many classes can be bunked safely"""
        stats = self.db.get_attendance_stats(user_id)
        attended = stats['present']
        total = stats['present'] + stats['absent'] + stats['leave']
        
        if total == 0:
            return 0
        
        current_percentage = (attended / total) * 100
        
        if current_percentage < target_attendance:
            return 0  # Must attend more classes
        
        # Formula: (attended) / (total + x) >= target
        # Solve for x: x <= (attended - target*total) / (target - 100) if target < 100
        
        if target_attendance >= 100:
            return 0
        
        max_bunk = (attended - (target_attendance * total / 100)) / (1 - target_attendance / 100)
        return max(0, int(max_bunk))
    
    def predict_future_attendance(self, user_id, days_ahead=30, target_attendance=70):
        """Predict attendance capacity in future"""
        stats = self.db.get_attendance_stats(user_id)
        attended = stats['present']
        total = stats['present'] + stats['absent'] + stats['leave']
        
        # Count future class days (excluding holidays and weekends)
        future_classes = 0
        today = datetime.now().date()
        
        for i in range(1, days_ahead + 1):
            future_date = today + timedelta(days=i)
            date_str = future_date.strftime('%Y-%m-%d')
            
            if self.is_class_day(future_date) and not self.is_holiday(date_str):
                future_classes += 6  # 6 classes per day
        
        # Calculate max bunk in future
        future_total = total + future_classes
        required_attended = (target_attendance / 100) * future_total
        max_future_bunk = int(future_classes - (required_attended - attended))
        
        return max(0, max_future_bunk), future_classes
    
    def get_upcoming_holidays(self, days_ahead=30):
        """Get upcoming holidays"""
        today = datetime.now().date()
        future_date = today + timedelta(days=days_ahead)
        
        from_str = today.strftime('%Y-%m-%d')
        to_str = future_date.strftime('%Y-%m-%d')
        
        return self.db.get_holidays(from_str, to_str, limit=50)
    
    def get_attendance_summary(self, user_id, days=30):
        """Get detailed attendance summary"""
        today = datetime.now().date()
        from_date = (today - timedelta(days=days)).strftime('%Y-%m-%d')
        to_date = today.strftime('%Y-%m-%d')
        
        stats = self.db.get_attendance_stats(user_id, from_date, to_date)
        total = stats['present'] + stats['absent'] + stats['leave']
        
        if total == 0:
            percentage = 0
        else:
            percentage = round((stats['present'] / total) * 100, 2)
        
        return {
            'present': stats['present'],
            'absent': stats['absent'],
            'leave': stats['leave'],
            'total': total,
            'percentage': percentage,
            'period_days': days
        }
