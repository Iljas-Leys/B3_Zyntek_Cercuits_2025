from datetime import datetime, timedelta
from sqlalchemy.orm import Session
# from setupPostgress import SessionLocal, Model, Agent, ChatSession, ChatResponse, engine, Base
from setupPostgress import SessionLocal, StatusEnum, PriorityEnum, CategoryEnum, DraftStatusEnum, Table, User, Email, ChatSession, Message, Draft, SourceDocument, EngineerRating
import sys
from pathlib import Path

def seed_data():
    db: Session = SessionLocal()
    
    user1 = User(
        name = "Gary (Technical Expert)",
        email="gary@cercuits.com",
        role="senior_engineer"
    )
    db.add(user1)
    db.flush()

    user2 = User(
        name="John Doe",
        email="john@cercuits.com",
        role="engineer"
    )
    db.add(user2)
    db.flush()

    email1 = Email(
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
        category=CategoryEnum.BIOS,
        priority=PriorityEnum.HIGH
    )
    db.add(email1)
    db.flush()

    email2 = Email(
        from_email="customer2@example.com",
        subject="Driver compatibility question",
        body="""Hi,

        I need to know if the v3.2 drivers are compatible with Windows 11 24H2.
        Our production line is planning to upgrade and we want to ensure compatibility.

        Thanks!""",
        category=CategoryEnum.DRIVERS,
        priority=PriorityEnum.MEDIUM
    )
    db.add(email2)
    db.flush()
        
    email3 = Email(
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
            category=CategoryEnum.HARDWARE,
            priority=PriorityEnum.URGENT
    )
    db.add(email2)
    db.flush()

    session1 = ChatSession(
        email_id=email1.id
    )
    db.add(session1)
    db.flush()

    message1 = Message(
            chat_session_id=session1.id,
            content="I need help with BIOS configuration",
            sender="user"
        )
    db.add(message1)
    db.flush()

    draft1 = Draft(
        chat_session_id=session1.id,
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
    db.add(draft1)
    db.flush()

    doc1 = SourceDocument(
        title="CER-2000 Technical Manual",
        file_name="cer2000_manual_v3.pdf",
        file_type="pdf",
        category="Hardware",
        tags="CER-2000, manual, hardware",
        uploaded_by=user1.id,
        file_url="/documents/cer2000_manual_v3.pdf"
    )
    db.add(doc1)
    db.flush()
        
    doc2 = SourceDocument(
        title="BIOS Configuration Guide",
        file_name="bios_config_guide.pdf",
        file_type="pdf",
        category="BIOS",
        tags="BIOS, configuration, troubleshooting",
        uploaded_by=user1.id,
        file_url="/documents/bios_config_guide.pdf"
    )
    db.add(doc2)
    db.flush()
    
    db.commit()
    db.close()

if __name__ == "__main__":
    seed_data()