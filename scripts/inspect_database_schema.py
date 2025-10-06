#!/usr/bin/env python3
"""
Database Schema Inspector
Shows all tables, schemas, and data from Flask app models
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sqlite3
from sqlalchemy import inspect, text

def create_app_for_inspection():
    """Create Flask app for database inspection"""
    app = Flask(__name__)
    
    # Use local SQLite for inspection
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trivia_inspection.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    return app

def inspect_flask_models():
    """Inspect Flask SQLAlchemy models to show schema"""
    print("=== FLASK SQLALCHEMY MODEL SCHEMAS ===")
    
    # Import models from app.py
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Create app and import models
        app = create_app_for_inspection()
        
        with app.app_context():
            from app import db, User, UserBackup
            
            # Create tables to inspect schema
            db.create_all()
            
            # Get database inspector
            inspector = inspect(db.engine)
            
            # Get all table names
            tables = inspector.get_table_names()
            print(f"Tables defined in Flask models: {tables}")
            
            for table_name in tables:
                print(f"\n--- TABLE: {table_name} ---")
                
                # Get columns
                columns = inspector.get_columns(table_name)
                print("Columns:")
                for col in columns:
                    nullable = "NULL" if col['nullable'] else "NOT NULL"
                    default = f"DEFAULT {col['default']}" if col['default'] else ""
                    print(f"  {col['name']}: {col['type']} {nullable} {default}")
                
                # Get primary keys
                pk = inspector.get_pk_constraint(table_name)
                if pk['constrained_columns']:
                    print(f"Primary Key: {', '.join(pk['constrained_columns'])}")
                
                # Get foreign keys
                fks = inspector.get_foreign_keys(table_name)
                if fks:
                    print("Foreign Keys:")
                    for fk in fks:
                        print(f"  {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
                
                # Get indexes
                indexes = inspector.get_indexes(table_name)
                if indexes:
                    print("Indexes:")
                    for idx in indexes:
                        unique = "UNIQUE" if idx['unique'] else ""
                        print(f"  {idx['name']}: {', '.join(idx['column_names'])} {unique}")
            
            # Show model definitions
            print(f"\n--- MODEL DEFINITIONS ---")
            print(f"User model: {User.__table__.columns.keys()}")
            print(f"UserBackup model: {UserBackup.__table__.columns.keys()}")
            
            # Check for any data
            user_count = db.session.query(User).count()
            backup_count = db.session.query(UserBackup).count()
            print(f"\nData counts:")
            print(f"Users: {user_count}")
            print(f"UserBackups: {backup_count}")
            
    except Exception as e:
        print(f"Error inspecting Flask models: {e}")
        import traceback
        traceback.print_exc()

def check_existing_databases():
    """Check for any existing database files"""
    print("\n=== EXISTING DATABASE FILES ===")
    
    db_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(('.db', '.sqlite', '.sqlite3')):
                db_files.append(os.path.join(root, file))
    
    if db_files:
        print(f"Found {len(db_files)} database files:")
        for db_file in db_files:
            print(f"  {db_file}")
            
            # Inspect each database
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # Get tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                if tables:
                    print(f"    Tables: {[t[0] for t in tables]}")
                    
                    for table in tables:
                        table_name = table[0]
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                        count = cursor.fetchone()[0]
                        print(f"      {table_name}: {count} rows")
                else:
                    print("    No tables found")
                
                conn.close()
                
            except Exception as e:
                print(f"    Error reading {db_file}: {e}")
    else:
        print("No database files found in project directory")

def show_production_status():
    """Show production app status"""
    print("\n=== PRODUCTION STATUS ===")
    
    import requests
    
    urls_to_check = [
        'https://pythontrivia-production.up.railway.app',
        'https://pythontrivia-production.up.railway.app/health',
        'https://pythontrivia-production.up.railway.app/api/users/count'
    ]
    
    for url in urls_to_check:
        try:
            response = requests.get(url, timeout=10)
            print(f"{url}: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"  Response: {data}")
                except:
                    print(f"  Response: {response.text[:200]}...")
        except Exception as e:
            print(f"{url}: ERROR - {e}")

def main():
    """Main inspection function"""
    print("🔍 DATABASE SCHEMA AND STATUS INSPECTOR")
    print("=" * 60)
    
    # Check Flask model schemas
    inspect_flask_models()
    
    # Check existing database files
    check_existing_databases()
    
    # Check production status
    show_production_status()
    
    print("\n" + "=" * 60)
    print("Inspection complete!")

if __name__ == "__main__":
    main()