# 🗄️ Database Architecture & Storage Layer

This directory houses the database engine, migrations, and schema definitions for the **AI Weather Forecasting & Advisory System**.

---

## 📂 Contents
- **`db.sqlite3`**: Active SQLite database instance storing user accounts, search histories, bookmarks, and sessions.
- **`schema.sql`**: Full SQL schema script for tables, indexes, constraints, and foreign key relationships.
- **`migrations/`**: Django ORM migration history files tracking schema versions (`0001_initial.py`, `0002_citysearchhistory_user_userfavoritecity.py`).

---

## 📊 Entity Relationship (ER) Overview

### 1. `auth_user` (Django Standard User Model)
- `id` (PK, Integer)
- `username` (VARCHAR, Unique)
- `password` (VARCHAR, Argon2/PBKDF2 Hashed)
- `email` (VARCHAR)
- `is_staff`, `is_active`, `date_joined`, `last_login`

### 2. `forecast_citysearchhistory` (Recent Searches)
- `id` (PK, Integer)
- `city_name` (VARCHAR)
- `country` (VARCHAR)
- `latitude` (Float)
- `longitude` (Float)
- `searched_at` (DateTime)
- `user_id` (FK -> `auth_user.id`, Nullable for Guest searches)

### 3. `forecast_userfavoritecity` (Bookmarked Cities)
- `id` (PK, Integer)
- `city_name` (VARCHAR)
- `country` (VARCHAR)
- `latitude` (Float)
- `longitude` (Float)
- `created_at` (DateTime)
- `user_id` (FK -> `auth_user.id`)
- *Unique Constraint:* `(user_id, city_name, country)`
