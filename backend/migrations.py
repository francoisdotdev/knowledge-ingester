"""
Migration script to add 'read' column to existing 'link' table
"""
from sqlalchemy import text
from database import engine

def add_read_column():
    """Add the 'read' column to the link table if it doesn't exist"""
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='link' AND column_name='read'
                )
            """)
        )
        column_exists = result.scalar()
        
        if not column_exists:
            print("Adding 'read' column to link table...")
            conn.execute(text("ALTER TABLE link ADD COLUMN read BOOLEAN DEFAULT FALSE NOT NULL"))
            conn.commit()
            print("✅ Column 'read' added successfully")
        else:
            print("✅ Column 'read' already exists")

if __name__ == "__main__":
    add_read_column()
