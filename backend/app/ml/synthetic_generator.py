import random
import uuid

from datetime import timedelta
from app.utils.db import get_db
from app.utils.time_utils import utc_now

DEPARTMENTS = ['Finance', 'Engineering', 'Human Resources', 'Sales', 'Executive', 'IT Support']
ROLES = {
    'Finance': ['Financial Analyst', 'Accountant', 'Payroll Specialist'],
    'Engineering': ['Senior Software Engineer', 'DevOps Engineer', 'Data Engineer'],
    'Human Resources': ['HR Manager', 'Recruiter', 'People Ops Specialist'],
    'Sales': ['Account Executive', 'Sales Director', 'BDR'],
    'Executive': ['VP of Operations', 'Chief Risk Officer', 'Strategy Lead'],
    'IT Support': ['Systems Administrator', 'Network Specialist', 'Helpdesk Tech']
}

NORMAL_USERS_DATA = [
    ('EMP-1001', 'Alexander Wright', 'Engineering'),
    ('EMP-1002', 'Elena Rostova', 'Finance'),
    ('EMP-1003', 'Marcus Vance', 'Human Resources'),
    ('EMP-1004', 'Sophia Chen', 'Sales'),
    ('EMP-1005', 'David Kim', 'IT Support'),
    ('EMP-1006', 'Rachel Adams', 'Finance'),
    ('EMP-1007', 'Carlos Mendez', 'Engineering'),
    ('EMP-1008', 'Priya Sharma', 'Executive'),
    ('EMP-1009', 'James Wilson', 'Sales'),
    ('EMP-1010', 'Hannah Taylor', 'Human Resources'),
]

OCCASIONAL_ANOMALY_USERS = [
    ('EMP-1011', 'Viktor Nikitin', 'Engineering'),
    ('EMP-1012', 'Amara Okafor', 'Finance'),
]

SEVERE_ANOMALY_USERS = [
    ('EMP-1013', 'Dmitri Ivanov', 'IT Support'), # Rogue Admin / Exfiltration
    ('EMP-1014', 'Chloe Bennett', 'Finance'),   # Compromised Credentials / Massive Download
]

DEVICES = [
    'MAC-CORP-9482', 'WIN-FIN-1029', 'WIN-ENG-4820', 'MAC-EXEC-0012',
    'LINUX-DEV-7721', 'WIN-HR-3392', 'MAC-SALES-5819'
]

LOCATIONS = [
    ('198.51.100.10', 'New York, USA'),
    ('198.51.100.12', 'New York, USA'),
    ('198.51.100.15', 'San Francisco, USA'),
    ('198.51.100.22', 'London, UK'),
]

FOREIGN_ANOMALOUS_LOCATIONS = [
    ('203.0.113.88', 'Zurich, Switzerland'),
    ('198.51.100.250', 'Moscow, Russia'),
    ('203.0.113.190', 'Tokyo, Japan'),
    ('198.51.100.199', 'Reykjavik, Iceland'),
]

CONFIDENTIAL_FILES = [
    'Q3_Financial_Payroll_Confidential.xlsx',
    'Customer_SSN_Vault_2026.csv',
    'Executive_Board_Strategy_M&A.pdf',
    'Source_Code_Core_Proprietary.zip',
    'Employee_Compensation_All.xlsx',
    'SSL_Private_Keys_Backup.tar.gz'
]

STANDARD_FILES = [
    'Weekly_Team_Notes.docx',
    'Project_Roadmap_2026.pptx',
    'Budget_Template.xlsx',
    'Release_Notes_v2.4.txt',
    'System_Architecture_Diagram.png'
]

def generate_synthetic_dataset(num_days=7, reset_db=True):
    db = get_db()
    if reset_db:
        db.users.delete_many({'is_demo_synthetic': True})
        db.activities.delete_many({'is_demo_synthetic': True})
        db.risk_scores.delete_many({})
        db.alerts.delete_many({})

    created_users = []
    
    # 1. Register Normal Users
    for user_id, name, dept in NORMAL_USERS_DATA:
        user_doc = {
            'user_id': user_id,
            'name': name,
            'email': f"{name.lower().replace(' ', '.')}@enterprise.internal",
            'department': dept,
            'role': random.choice(ROLES[dept]),
            'baseline_location': 'New York, USA',
            'baseline_device': f"DEV-{user_id}",
            'is_demo_synthetic': True,
            'created_at': utc_now()
        }
        db.users.update_one({'user_id': user_id}, {'$set': user_doc}, upsert=True)
        created_users.append(user_doc)

    # 2. Register Occasional Anomaly Users
    for user_id, name, dept in OCCASIONAL_ANOMALY_USERS:
        user_doc = {
            'user_id': user_id,
            'name': name,
            'email': f"{name.lower().replace(' ', '.')}@enterprise.internal",
            'department': dept,
            'role': random.choice(ROLES[dept]),
            'baseline_location': 'New York, USA',
            'baseline_device': f"DEV-{user_id}",
            'is_demo_synthetic': True,
            'created_at': utc_now()
        }
        db.users.update_one({'user_id': user_id}, {'$set': user_doc}, upsert=True)
        created_users.append(user_doc)

    # 3. Register Severe Anomaly Users
    for user_id, name, dept in SEVERE_ANOMALY_USERS:
        user_doc = {
            'user_id': user_id,
            'name': name,
            'email': f"{name.lower().replace(' ', '.')}@enterprise.internal",
            'department': dept,
            'role': random.choice(ROLES[dept]),
            'baseline_location': 'New York, USA',
            'baseline_device': f"DEV-{user_id}",
            'is_demo_synthetic': True,
            'created_at': utc_now()
        }
        db.users.update_one({'user_id': user_id}, {'$set': user_doc}, upsert=True)
        created_users.append(user_doc)

    # Generate timeline of logs over num_days
    activities = []
    now = utc_now().replace(tzinfo=None)
    start_time = now - timedelta(days=num_days)

    # Unique per generation run so non-reset runs never produce duplicate IDs
    batch_prefix = uuid.uuid4().hex[:4].upper()
    activity_id_counter = 10000

    for day in range(num_days):
        current_date = start_time + timedelta(days=day)

        # Generate normal user activity logs (regular hours 9am - 5pm)
        for user in created_users:
            u_id = user['user_id']
            
            # Determine profile behavior
            is_severe = u_id in [u[0] for u in SEVERE_ANOMALY_USERS]
            is_occasional = u_id in [u[0] for u in OCCASIONAL_ANOMALY_USERS]

            # Generate 3-6 routine daily events
            events_per_day = random.randint(4, 7) if not is_severe else random.randint(8, 14)

            for _ in range(events_per_day):
                activity_id_counter += 1
                
                if is_severe and random.random() < 0.45:
                    # ANOMALOUS LOG
                    # 1 AM - 4 AM after hours
                    event_time = current_date.replace(
                        hour=random.choice([1, 2, 3, 4]),
                        minute=random.randint(0, 59)
                    )
                    ip, loc = random.choice(FOREIGN_ANOMALOUS_LOCATIONS)
                    device = f"UNREGISTERED-MAC-{random.randint(1000,9999)}"
                    failed_logins = random.randint(3, 7)
                    file_name = random.choice(CONFIDENTIAL_FILES)
                    files_cnt = random.randint(35, 120)
                    download_mb = round(random.uniform(450.0, 3200.0), 2)
                    upload_mb = round(random.uniform(150.0, 850.0), 2)
                    event_type = random.choice(['FILE_DOWNLOAD', 'FILE_UPLOAD', 'LOGIN', 'FILE_ACCESS'])
                    after_hours = True
                elif is_occasional and random.random() < 0.25:
                    # OCCASIONAL ANOMALY LOG
                    event_time = current_date.replace(
                        hour=random.choice([20, 21, 22]),
                        minute=random.randint(0, 59)
                    )
                    ip, loc = LOCATIONS[0]
                    device = user['baseline_device']
                    failed_logins = random.randint(1, 2)
                    file_name = random.choice(CONFIDENTIAL_FILES)
                    files_cnt = random.randint(12, 28)
                    download_mb = round(random.uniform(80.0, 220.0), 2)
                    upload_mb = round(random.uniform(10.0, 45.0), 2)
                    event_type = random.choice(['FILE_DOWNLOAD', 'FILE_ACCESS'])
                    after_hours = True
                else:
                    # NORMAL LOG
                    event_time = current_date.replace(
                        hour=random.randint(9, 17),
                        minute=random.randint(0, 59)
                    )
                    ip, loc = LOCATIONS[0]
                    device = user['baseline_device']
                    failed_logins = 0
                    file_name = random.choice(STANDARD_FILES)
                    files_cnt = random.randint(1, 5)
                    download_mb = round(random.uniform(0.5, 15.0), 2)
                    upload_mb = round(random.uniform(0.1, 5.0), 2)
                    event_type = random.choice(['LOGIN', 'FILE_ACCESS', 'LOGOUT', 'APP_USAGE'])
                    after_hours = False

                act_doc = {
                    'activity_id': f"ACT-{batch_prefix}-{activity_id_counter}",
                    'user_id': u_id,
                    'timestamp': event_time.isoformat() + 'Z',
                    'event_type': event_type,
                    'location_ip': ip,
                    'location_name': loc,
                    'device_id': device,
                    'app_used': 'SecureFTP Client' if 'DOWNLOAD' in event_type or 'UPLOAD' in event_type else 'Enterprise Workplace OS',
                    'file_details': {
                        'filename': file_name,
                        'files_accessed_count': files_cnt,
                        'download_size_mb': download_mb,
                        'upload_size_mb': upload_mb
                    },
                    'after_hours': after_hours,
                    'failed_logins': failed_logins,
                    'is_demo_synthetic': True
                }
                activities.append(act_doc)

    if activities:
        db.activities.insert_many(activities)

    return {
        'users_created': len(created_users),
        'activities_created': len(activities),
        'message': f"Successfully generated {len(created_users)} users and {len(activities)} activity logs spanning {num_days} days."
    }
