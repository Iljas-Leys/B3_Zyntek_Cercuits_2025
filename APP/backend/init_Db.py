"""
Database initialization and seed data script
Run this to create tables and add test data
"""
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app.core.database import engine, SessionLocal, Base
from app.models import models
from app import crud, schemas
from datetime import datetime, timedelta

def init_db():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")

def seed_data():
    """Add test/seed data"""
    db = SessionLocal()
    
    try:
        print("\nAdding seed data...")
        
        # Create test users
        print("Creating users...")
        user1 = crud.create_user(db, schemas.UserCreate(
            name="Gary (Technical Expert)",
            email="gary@cercuits.com",
            role="senior_engineer"
        ))
        
        user2 = crud.create_user(db, schemas.UserCreate(
            name="John Doe",
            email="john@cercuits.com",
            role="engineer"
        ))
        
        print(f"✓ Created users: {user1.name}, {user2.name}")
        
        # Create test emails
        print("\nCreating test emails...")
        
        email1 = crud.create_email(db, schemas.EmailCreate(
            from_email="customer1@example.com",
            subject="BIOS configuration issue on CER-2000 board",
            body="""Hello,

I'm experiencing issues with the BIOS configuration on our CER-2000 board. 
The system fails to boot after updating to the latest firmware version.

System details:
- Board: CER-2000 Rev 3.1
- Firmware: v2.4.1
- Error code: 0x8A

Can you please advise on how to resolve this?

Best regards,
Customer""",
            category=schemas.CategoryEnum.BIOS,
            priority=schemas.PriorityEnum.HIGH
        ))
        
        email2 = crud.create_email(db, schemas.EmailCreate(
            from_email="customer2@example.com",
            subject="Driver compatibility question",
            body="""Hi,

I need to know if the v3.2 drivers are compatible with Windows 11 24H2.
Our production line is planning to upgrade and we want to ensure compatibility.

Thanks!""",
            category=schemas.CategoryEnum.DRIVERS,
            priority=schemas.PriorityEnum.MEDIUM
        ))
        
        email3 = crud.create_email(db, schemas.EmailCreate(
            from_email="customer3@example.com",
            subject="Thermal performance specifications",
            body="""Hello CERcuits team,

Could you provide the thermal performance specifications for the CER-5000 series?
Specifically, I need:
- Maximum operating temperature
- Thermal conductivity values
- Recommended cooling solutions

This is for a high-temperature industrial application.

Thank you.""",
            category=schemas.CategoryEnum.HARDWARE,
            priority=schemas.PriorityEnum.URGENT
        ))
        
        print(f"✓ Created 3 test emails")
        
        # Create a chat session and draft for the first email
        print("\nCreating test chat session with draft...")
        session1 = crud.create_chat_session(db, email1.id)
        
        # Add a message
        crud.create_message(db, schemas.MessageCreate(
            chat_session_id=session1.id,
            content="I need help with BIOS configuration",
            sender="user"
        ))
        
        # Create a draft
        draft1 = crud.create_draft(
            db,
            session1.id,
            response_text="""Thank you for contacting CERcuits technical support.

Regarding the BIOS configuration issue on your CER-2000 board (Rev 3.1):

The error code 0x8A typically indicates a firmware checksum mismatch. This can occur when:
1. The firmware update was interrupted
2. The board's power supply is unstable
3. There's a compatibility issue with the specific revision

**Recommended Solution:**
1. Power cycle the board completely (remove power for 30 seconds)
2. Re-flash the firmware using our recovery mode:
   - Hold the reset button while powering on
   - Use the CERcuits Firmware Tool v4.2 or later
   - Select "Recovery Mode Flash"
3. Verify the checksum after flashing

If the issue persists, it may be necessary to revert to firmware v2.3.5 (stable) while we investigate the v2.4.1 compatibility with Rev 3.1 boards.

Please let us know the outcome, and we'll assist further if needed.

Best regards,
CERcuits Technical Support""",
            summary="BIOS recovery procedure for error 0x8A"
        )
        
        print(f"✓ Created chat session and draft for email: {email1.subject[:30]}...")
        
        # Create some test documents
        print("\nCreating test knowledge documents...")
        doc1 = crud.create_source_document(db, schemas.SourceDocumentCreate(
            title="CER-2000 Technical Manual",
            file_name="cer2000_manual_v3.pdf",
            file_type="pdf",
            category="Hardware",
            tags="CER-2000, manual, hardware",
            uploaded_by=user1.id,
            file_url="/documents/cer2000_manual_v3.pdf"
        ))
        
        doc2 = crud.create_source_document(db, schemas.SourceDocumentCreate(
            title="BIOS Configuration Guide",
            file_name="bios_config_guide.pdf",
            file_type="pdf",
            category="BIOS",
            tags="BIOS, configuration, troubleshooting",
            uploaded_by=user1.id,
            file_url="/documents/bios_config_guide.pdf"
        ))
        
        print(f"✓ Created 2 test documents")
        
        print("\n" + "="*50)
        print("✓ Database initialization and seeding completed!")
        print("="*50)
        print("\nTest data summary:")
        print(f"- Users: 2 (Gary, John)")
        print(f"- Emails: 3 (1 High, 1 Urgent, 1 Medium priority)")
        print(f"- Chat sessions: 1")
        print(f"- Drafts: 1")
        print(f"- Documents: 2")
        print("\nYou can now start the API server with:")
        print("  cd backend")
        print("  uvicorn app.main:app --reload")
        print("\nAPI docs will be available at: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\n✗ Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("="*50)
    print("Agent TSE - Database Setup")
    print("="*50)
    
    init_db()
    
    # Ask user if they want to seed data
    response = input("\nDo you want to add test/seed data? (y/n): ").lower()
    if response == 'y':
        seed_data()
    else:
        print("\nSkipping seed data. Database tables are ready.")
        print("\nYou can run this script again to add seed data later.")