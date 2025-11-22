"""
Script de migration pour ajouter la colonne resource_type
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

try:
    print("Adding resource_type column...")
    cur.execute("""
        ALTER TABLE link 
        ADD COLUMN IF NOT EXISTS resource_type VARCHAR(20) DEFAULT 'article';
    """)
    
    print("Updating existing records...")
    cur.execute("""
        UPDATE link 
        SET resource_type = 'article' 
        WHERE resource_type IS NULL;
    """)
    
    conn.commit()
    print("✅ Migration completed successfully!")
    
except Exception as e:
    print(f"❌ Error during migration: {e}")
    conn.rollback()
finally:
    cur.close()
    conn.close()
