-- ==========================================================
-- AI Weather Forecasting & Advisory System - Database Schema
-- Database Engine: SQLite / PostgreSQL Compatible
-- ==========================================================

-- 1. Django Authentication & User Table
CREATE TABLE IF NOT EXISTS "auth_user" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "password" varchar(128) NOT NULL,
    "last_login" datetime NULL,
    "is_superuser" bool NOT NULL,
    "username" varchar(150) NOT NULL UNIQUE,
    "first_name" varchar(150) NOT NULL,
    "last_name" varchar(150) NOT NULL,
    "email" varchar(254) NOT NULL,
    "is_staff" bool NOT NULL,
    "is_active" bool NOT NULL,
    "date_joined" datetime NOT NULL
);

-- 2. City Search History (User Queries & Coordinates)
CREATE TABLE IF NOT EXISTS "forecast_citysearchhistory" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "city_name" varchar(100) NOT NULL,
    "country" varchar(100) NOT NULL,
    "latitude" real NOT NULL,
    "longitude" real NOT NULL,
    "searched_at" datetime NOT NULL,
    "user_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS "forecast_citysearchhistory_user_id_idx" 
ON "forecast_citysearchhistory" ("user_id");

CREATE INDEX IF NOT EXISTS "forecast_citysearchhistory_searched_at_idx" 
ON "forecast_citysearchhistory" ("searched_at" DESC);

-- 3. User Favorite Cities (Bookmarked Locations)
CREATE TABLE IF NOT EXISTS "forecast_userfavoritecity" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "city_name" varchar(100) NOT NULL,
    "country" varchar(100) NOT NULL,
    "latitude" real NOT NULL,
    "longitude" real NOT NULL,
    "created_at" datetime NOT NULL,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT "forecast_userfavoritecity_user_city_unique" UNIQUE ("user_id", "city_name", "country")
);

CREATE INDEX IF NOT EXISTS "forecast_userfavoritecity_user_id_idx" 
ON "forecast_userfavoritecity" ("user_id");

-- 4. Django Session Management
CREATE TABLE IF NOT EXISTS "django_session" (
    "session_key" varchar(40) NOT NULL PRIMARY KEY,
    "session_data" text NOT NULL,
    "expire_date" datetime NOT NULL
);

CREATE INDEX IF NOT EXISTS "django_session_expire_date_idx" 
ON "django_session" ("expire_date");
