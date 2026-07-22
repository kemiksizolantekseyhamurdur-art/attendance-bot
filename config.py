import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
USER_ID = int(os.getenv('USER_ID', 0))

# Attendance Settings
TARGET_ATTENDANCE = 70  # Default target attendance %
SEMESTER_START = datetime(2025, 7, 13)  # 13/7/2025
SEMESTER_END = datetime(2026, 1, 15)  # Around Dec-Jan

# Class Schedule (Monday=0, Friday=4)
CLASS_SCHEDULE = {
    0: [  # Monday
        {'slot': 1, 'time': '09:05-10:05', 'subjects': ['B1:FOS', 'B2:RDBMS']},
        {'slot': 2, 'time': '10:05-11:00', 'subjects': ['KHM', 'JJP']},
        {'slot': 3, 'time': '11:45-12:40', 'subjects': ['CX', 'PG']},
        {'slot': 4, 'time': '12:40-13:35', 'subjects': ['RDBMS', 'JJP']},
        {'slot': 5, 'time': '13:55-14:50', 'subjects': ['FOS', 'KHM']},
        {'slot': 6, 'time': '14:50-15:45', 'subjects': ['DS', 'APJ']},
    ],
    1: [  # Tuesday
        {'slot': 1, 'time': '09:05-10:05', 'subjects': ['DS', 'ABTI', 'TI']},
        {'slot': 2, 'time': '10:05-11:00', 'subjects': ['FDS', 'KHM']},
        {'slot': 3, 'time': '11:45-12:40', 'subjects': ['RWPD', 'KMJ']},
        {'slot': 4, 'time': '12:40-13:35', 'subjects': ['DEF', 'HMP']},
        {'slot': 5, 'time': '13:55-14:50', 'subjects': ['BEDS', 'APJ']},
        {'slot': 6, 'time': '14:50-15:45', 'subjects': ['B2:FOS', 'KHM']},
    ],
    2: [  # Wednesday
        {'slot': 1, 'time': '09:05-10:05', 'subjects': []},
        {'slot': 2, 'time': '10:05-11:00', 'subjects': ['B1:RWPD', 'KMJ']},
        {'slot': 3, 'time': '11:45-12:40', 'subjects': ['RDBMS', 'JJP']},
        {'slot': 4, 'time': '12:40-13:35', 'subjects': ['DEF', 'MAM']},
        {'slot': 5, 'time': '13:55-14:50', 'subjects': ['B1:RWPD', 'TKO']},
        {'slot': 6, 'time': '14:50-15:45', 'subjects': ['B2:DEF', 'MAM']},
    ],
    3: [  # Thursday
        {'slot': 1, 'time': '09:05-10:05', 'subjects': ['RDBMS', 'JJP']},
        {'slot': 2, 'time': '10:05-11:00', 'subjects': ['FOS', 'KHM']},
        {'slot': 3, 'time': '11:45-12:40', 'subjects': ['CN', 'PG']},
        {'slot': 4, 'time': '12:40-13:35', 'subjects': ['DS', 'APJ']},
        {'slot': 5, 'time': '13:55-14:50', 'subjects': ['B1:RWPD', 'KMJ']},
        {'slot': 6, 'time': '14:50-15:45', 'subjects': ['B2:RWPD', 'JJP']},
    ],
    4: [  # Friday
        {'slot': 1, 'time': '09:05-10:05', 'subjects': ['CN', 'PG']},
        {'slot': 2, 'time': '10:05-11:00', 'subjects': ['DEF', 'MAM']},
        {'slot': 3, 'time': '11:45-12:40', 'subjects': ['B1:DEF', 'HMP']},
        {'slot': 4, 'time': '12:40-13:35', 'subjects': ['B2:CN', 'PG']},
        {'slot': 5, 'time': '13:55-14:50', 'subjects': []},
        {'slot': 6, 'time': '14:50-15:45', 'subjects': ['B1:CN', 'PG']},
    ],
}

# Holidays 2025-26 (India + College specific)
HOLIDAYS = [
    # July 2025
    {'date': '2025-07-26', 'name': 'Karmavir Bhaurao Patil Jayanti', 'type': 'national'},
    
    # August 2025
    {'date': '2025-08-15', 'name': 'Independence Day', 'type': 'national'},
    {'date': '2025-08-27', 'name': 'Janmashtami', 'type': 'national'},
    
    # September 2025
    {'date': '2025-09-16', 'name': 'Milad-un-Nabi', 'type': 'national'},
    {'date': '2025-09-20', 'name': 'Mahatma Gandhi Jayanti', 'type': 'national'},
    
    # October 2025
    {'date': '2025-10-02', 'name': 'Gandhi Jayanti', 'type': 'national'},
    {'date': '2025-10-12', 'name': 'Dussehra (Vijayadashami)', 'type': 'national'},
    {'date': '2025-10-13', 'name': 'Dussehra (College Holiday)', 'type': 'college'},
    {'date': '2025-10-14', 'name': 'Dussehra Break', 'type': 'college'},
    {'date': '2025-10-22', 'name': 'Diwali', 'type': 'national'},
    {'date': '2025-10-23', 'name': 'Diwali (College Holiday)', 'type': 'college'},
    {'date': '2025-10-24', 'name': 'Diwali Break', 'type': 'college'},
    
    # November 2025
    {'date': '2025-11-01', 'name': 'Diwali Break', 'type': 'college'},
    {'date': '2025-11-11', 'name': 'Guru Nanak Jayanti', 'type': 'national'},
    {'date': '2025-11-25', 'name': 'Constitution Day', 'type': 'national'},
    
    # December 2025
    {'date': '2025-12-25', 'name': 'Christmas', 'type': 'national'},
    {'date': '2025-12-26', 'name': 'Winter Break (College Holiday)', 'type': 'college'},
    {'date': '2025-12-27', 'name': 'Winter Break', 'type': 'college'},
    {'date': '2025-12-28', 'name': 'Winter Break', 'type': 'college'},
    {'date': '2025-12-29', 'name': 'Winter Break', 'type': 'college'},
    {'date': '2025-12-30', 'name': 'Winter Break', 'type': 'college'},
    {'date': '2025-12-31', 'name': 'Winter Break', 'type': 'college'},
    
    # January 2026
    {'date': '2026-01-01', 'name': 'New Year', 'type': 'national'},
    {'date': '2026-01-02', 'name': 'Winter Break', 'type': 'college'},
    {'date': '2026-01-03', 'name': 'Winter Break', 'type': 'college'},
    {'date': '2026-01-04', 'name': 'Winter Break', 'type': 'college'},
    {'date': '2026-01-05', 'name': 'Winter Break', 'type': 'college'},
    {'date': '2026-01-06', 'name': 'Winter Break', 'type': 'college'},
    {'date': '2026-01-07', 'name': 'Winter Break', 'type': 'college'},
    {'date': '2026-01-26', 'name': 'Republic Day', 'type': 'national'},
]

DATABASE_URL = 'sqlite:///attendance.db'
