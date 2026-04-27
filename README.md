# 📚 Library Management System
**Python + MySQL | CLI Application**

---

## ✨ Features

| Module | Features |
|--------|----------|
| 📖 Books | Add, View, Update, Delete |
| 👤 Members | Add, View, Update, Delete |
| 📤 Issue Book | Issue with auto due-date (14 days) |
| 📥 Return Book | Return with automatic fine calculation |
| 🔍 Search | Search by Title, Author, Genre |
| ⚠️ Overdue | View overdue books + fine amount |
| 📊 Reports | Issued list, Return history, Statistics |

---

## 🚀 Setup (Step by Step)

### Step 1 — Install Python library
```bash
pip install mysql-connector-python
```

### Step 2 — Setup MySQL Database
Open MySQL and run:
```sql
source setup_db.sql
```
Or paste the contents of `setup_db.sql` into MySQL Workbench / phpMyAdmin.

### Step 3 — Update config.py
```python
DB_HOST     = "localhost"
DB_USER     = "root"
DB_PASSWORD = "your_mysql_password"   # ← yahan apna password dalein
DB_NAME     = "library_db"
```

### Step 4 — Run the app
```bash
python library.py
```

---

## 📁 Project Structure

```
library-system/
├── library.py       ← Main application (all menus + logic)
├── db.py            ← MySQL connection helper
├── config.py        ← DB credentials + settings
├── setup_db.sql     ← Database + tables + sample data
├── requirements.txt
└── README.md
```

---

## 💰 Fine Policy
- **₹2 per day** for overdue books (configurable in `config.py`)
- **14 day** loan period (configurable in `config.py`)

---

## 🛠️ Tech Stack
- **Language**: Python 3.8+
- **Database**: MySQL 8.0+
- **Library**: mysql-connector-python
- **Architecture**: 3-file MVC style (config → db → library)
