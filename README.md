Report Cycle Time/
├── app.py                          # Main entry point
├── requirements.txt                # Dependencies
├── README.md                       # This file
│
├── config/
│   └── settings.py                 # Configuration constants
│
├── models/
│   ├── __init__.py
│   ├── cycle_time.py              # CycleTime data model
│   └── cycle_record.py            # CycleRecord data model
│
├── utils/
│   ├── __init__.py
│   ├── security.py                # Password hashing & validation
│   ├── validation.py              # Input validation
│   └── file_manager.py            # File operations & persistence
│
├── auth/
│   ├── __init__.py
│   └── authentication.py          # Login/logout & user management
│
├── pages/
│   ├── __init__.py
│   ├── main_entry.py              # Data entry page
│   ├── view_edit.py               # View/Edit records page
│   ├── analytics.py               # Analytics dashboard
│   ├── export.py                  # Export & reports
│   ├── admin.py                   # Admin panel
│   └── settings.py                # Settings & maintenance
│
└── data/                           # Data storage (auto-created)
    ├── users.json                  # User accounts
    ├── cycle_time_records.json    # Cycle time data
    └── audit_log.json             # Audit trail