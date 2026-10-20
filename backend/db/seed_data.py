"""
Seed data script for ADMIT system.
Populates initial KB categories and creates default admin user.
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from db.database import get_db_context
from models.schemas import KBCategory, AdminUser
from auth.jwt_handler import hash_password


async def seed_categories():
    """Create initial KB categories for all departments"""
    print("Seeding KB categories...")
    
    categories = [
        # IBED Categories
        {"name": "Admission Requirements", "department": "IBED"},
        {"name": "Enrollment Steps", "department": "IBED"},
        {"name": "Programs Offered", "department": "IBED"},
        {"name": "Tuition and Payment", "department": "IBED"},
        {"name": "Scholarships", "department": "IBED"},
        {"name": "Contact Information", "department": "IBED"},
        
        # SHS Categories
        {"name": "Admission Requirements", "department": "SHS"},
        {"name": "Enrollment Steps", "department": "SHS"},
        {"name": "Programs Offered", "department": "SHS"},
        {"name": "Tuition and Payment", "department": "SHS"},
        {"name": "Scholarships", "department": "SHS"},
        {"name": "Contact Information", "department": "SHS"},
        
        # HED Categories
        {"name": "Admission Requirements", "department": "HED"},
        {"name": "Enrollment Steps", "department": "HED"},
        {"name": "Programs Offered", "department": "HED"},
        {"name": "Tuition and Payment", "department": "HED"},
        {"name": "Scholarships", "department": "HED"},
        {"name": "Contact Information", "department": "HED"},
        
        # TESDA Categories
        {"name": "Admission Requirements", "department": "TESDA"},
        {"name": "Enrollment Steps", "department": "TESDA"},
        {"name": "Programs Offered", "department": "TESDA"},
        {"name": "Tuition and Payment", "department": "TESDA"},
        {"name": "Scholarships", "department": "TESDA"},
        {"name": "Contact Information", "department": "TESDA"},
        
        # General Categories
        {"name": "About SACLI", "department": "GENERAL"},
        {"name": "Campus Facilities", "department": "GENERAL"},
        {"name": "Student Services", "department": "GENERAL"},
    ]
    
    async with get_db_context() as db:
        # Check if categories already exist
        result = await db.execute(select(KBCategory))
        existing = result.scalars().first()
        
        if existing:
            print("  ⚠ Categories already exist, skipping...")
            return
        
        # Insert categories
        for cat_data in categories:
            category = KBCategory(**cat_data)
            db.add(category)
        
        await db.commit()
        print(f"  ✓ Created {len(categories)} KB categories")


async def seed_admin_user():
    """Create default admin user account"""
    print("Creating default admin user...")
    
    # Default credentials (should be changed after first login)
    username = "admin"
    password = "admin123"  # CHANGE THIS IN PRODUCTION!
    
    async with get_db_context() as db:
        # Check if admin user already exists
        result = await db.execute(
            select(AdminUser).where(AdminUser.username == username)
        )
        existing_admin = result.scalars().first()
        
        if existing_admin:
            print(f"  ⚠ Admin user '{username}' already exists, skipping...")
            return
        
        # Hash password and create admin user
        password_hash = hash_password(password)
        admin_user = AdminUser(
            username=username,
            password_hash=password_hash,
            role="admin"
        )
        
        db.add(admin_user)
        await db.commit()
        
        print(f"  ✓ Created admin user: {username}")
        print(f"  ⚠ Default password: {password}")
        print(f"  ⚠ IMPORTANT: Change this password immediately in production!")


async def seed_sample_kb_entries():
    """
    Seed real SACLI KB entries sourced from https://sacli.edu.ph/
    Each entry is embedded using the fastembed model at insert time.
    """
    print("Creating SACLI KB entries...")

    # ----------------------------------------------------------------
    # Import embedding service here (model must already be loaded by
    # the caller, or we load it on demand via load_model()).
    # ----------------------------------------------------------------
    from services.embeddings import load_model, embed

    try:
        load_model()
    except Exception as e:
        print(f"  ⚠ Could not load embedding model: {e}")
        print("  ⚠ Skipping KB entries — run seed_database() after the server has started.")
        return

    # ----------------------------------------------------------------
    # Raw entries: (category_name, department, title, content)
    # ----------------------------------------------------------------
    kb_entries_raw = [

        # ──────────────────────────────────────────────────────────────
        # GENERAL — About SACLI
        # ──────────────────────────────────────────────────────────────
        (
            "About SACLI", "GENERAL",
            "What is SACLI?",
            "St. Anne College Lucena, Inc. (SACLI), formerly known as St. Anne School of Medical Sciences, "
            "is a private, non-stock, non-profit, and non-sectarian educational institution founded in March 1986. "
            "It is located in Lucena City, Quezon Province. SACLI offers programs from Preschool up to the college level, "
            "as well as TESDA technical-vocational courses. The institution's tagline is 'Go Higher With Us.'"
        ),
        (
            "About SACLI", "GENERAL",
            "What departments and schools does SACLI have?",
            "SACLI is organized into the following academic units:\n"
            "• Integrated Basic Education Department (IBED) — Preschool, Elementary, and Junior High School\n"
            "• Senior High School (SHS) — ABM, HUMSS, STEM, and other strands\n"
            "• School of Allied Health Sciences (SAHS) — Doctor of Dental Medicine (DMD), BS Nursing, BS Physical Therapy, BS Midwifery, BS Medical Technology\n"
            "• School of Management for International Hospitality and Tourism (SMIHT) — BS Hospitality Management, BS Tourism Management\n"
            "• College of Criminology (COC) — BS Criminology\n"
            "• School of Business, Accountancy, Technology, and Engineering (SBATE) — BS Accountancy, BS Management Accounting, BS Business Administration, BS Information Technology, BS Civil Engineering, BS Industrial Engineering\n"
            "• School of Education, Arts, and Sciences (SEAS) — AB Communication, AB Psychology, BS Secondary Education, BS Elementary Education, BS Technical Vocational Teacher Education\n"
            "• TESDA Programs — Technical-vocational courses leading to TESDA national certifications"
        ),
        (
            "Contact Information", "GENERAL",
            "SACLI general contact information and office contacts",
            "SACLI General Contact Numbers: 710-5624 / 0933-862-2338 / 0922-898-5919\n\n"
            "Office contacts:\n"
            "• Admission / Corporate Communications Office (CCO): sacli.admission@gmail.com | 0985-922-8238\n"
            "• Registrar's Office: sacli.registrar@gmail.com | 710-5624 local 105 | 0933-862-2338 | 0922-898-5919\n"
            "• Accounting Office: sacli.acctng@gmail.com | 710-5624 local 103 | 0933-862-2338 | 0922-898-5919\n"
            "• IBED Department: ibedsacli@sacli.edu.ph | Facebook: SACLI-Integrated Basic Education Department\n"
            "• SMIHT (Hospitality & Tourism): smiht@sacli.edu.ph\n"
            "• SAHS Nursing: sahs@sacli.edu.ph\n"
            "• SAHS Dentistry: dmdsacli@sacli.edu.ph\n"
            "• SAHS Midwifery: bsmidwiferysacli@sacli.edu.ph\n"
            "• SAHS Physical Therapy: sacliptherapy@gmail.com\n"
            "• College of Criminology: sacli.collegeofcriminology@gmail.com\n"
            "• SBATE Business Administration: sacli.bsba2020@gmail.com\n"
            "• SBATE Information Technology: bsitsacli@sacli.edu.ph\n"
            "• SBATE Accountancy: jpiasacopchapter@gmail.com\n"
            "• School of Engineering — Civil: civilengineeringsacli@gmail.com\n"
            "• School of Engineering — Industrial: piiesaclisc@gmail.com\n"
            "• SEAS Education: seas@sacli.edu.ph\n"
            "• SEAS Psychology: abpsychsacli@sacli.edu.ph\n"
            "• TESDA: stanne.tesda@gmail.com\n"
            "• Library: librarysacli@sacli.edu.ph\n\n"
            "Online admissions portal: https://sacli.edu.ph/admissions/"
        ),
        (
            "Student Services", "GENERAL",
            "How do I apply or enroll at SACLI online?",
            "SACLI has an online admissions portal at https://sacli.edu.ph/admissions/ where prospective students can:\n"
            "• Apply for Basic Education (BED) — Preschool, Elementary, Junior High School\n"
            "• Apply for Higher Education (HED) — Senior High School and College programs\n"
            "• Check application status using a Reference Code\n\n"
            "For questions about your application, contact the Admissions / Corporate Communications Office:\n"
            "Email: sacli.admission@gmail.com | Mobile: 0985-922-8238"
        ),
        (
            "About SACLI", "GENERAL",
            "What makes SACLI a good school to choose?",
            "SACLI is known for several distinctions:\n"
            "• Maintains small class sizes for personalized learning, especially in IBED\n"
            "• BS Hospitality Management is a recipient of the Plaque of Recognition from the Provincial Council of Quezon\n"
            "• BS Tourism Management is a consistent champion in Philippine Tourism Competitions and is called 'Home of Successful International Flight Attendants and Travel and Tour Operators'\n"
            "• BS Criminology achieved a 100% board passing rate for three consecutive years and the highest board passing rate in Quezon Province in 2018\n"
            "• Dentistry program is described as 'The First and Only Dentistry School in Quezon Province'\n"
            "• Students are sent to international practicum destinations including Canada, Thailand, USA, Singapore, Jordan, and Australia\n"
            "• Engineering school has modern laboratory facilities\n"
            "• Strong alumni network across healthcare, hospitality, business, and education sectors"
        ),

        # ──────────────────────────────────────────────────────────────
        # IBED — Integrated Basic Education
        # ──────────────────────────────────────────────────────────────
        (
            "Programs Offered", "IBED",
            "What programs does the IBED (Integrated Basic Education Department) offer?",
            "The IBED covers the following levels:\n"
            "• Preschool — nurturing, God-loving environment focused on reading, writing, arithmetic, GMRC, and talent development through play\n"
            "• Elementary — small class sizes with parent partnership for personalized learning\n"
            "• Junior High School (Grades 7–10) — develops independence and responsibility through dynamic learning experiences\n\n"
            "The IBED follows the DepEd K-12 curriculum. Class sizes are kept small to ensure each student receives special care and attention."
        ),
        (
            "Admission Requirements", "IBED",
            "What are the admission requirements for IBED (Basic Education)?",
            "To apply for IBED (Basic Education) at SACLI, you can use the online admissions portal at https://sacli.edu.ph/admissions/ and select 'Apply for BED'.\n\n"
            "General document requirements typically include:\n"
            "• Report card / Form 138 from previous school\n"
            "• Birth Certificate (PSA copy)\n"
            "• Good moral character certificate from previous school\n"
            "• 2x2 ID photos\n\n"
            "For Kindergarten/Preschool: proof of age (birth certificate) and a readiness assessment may be required.\n\n"
            "For complete and updated requirements, contact the IBED Department:\n"
            "Email: ibedsacli@sacli.edu.ph | Facebook: SACLI-Integrated Basic Education Department\n"
            "Or the Registrar's Office: sacli.registrar@gmail.com | 710-5624 local 105"
        ),
        (
            "Enrollment Steps", "IBED",
            "How do I enroll my child in SACLI's Basic Education (IBED)?",
            "Enrollment for IBED can be started online:\n"
            "1. Visit https://sacli.edu.ph/admissions/ and click 'Apply for BED'\n"
            "2. Fill out the online application form\n"
            "3. Prepare and submit required documents (report card, birth certificate, good moral certificate, photos)\n"
            "4. Wait for confirmation and check your application status using the Reference Code provided\n"
            "5. Proceed to campus for any required assessments or interviews\n"
            "6. Pay enrollment fees at the Accounting Office\n\n"
            "For questions: IBED Department — ibedsacli@sacli.edu.ph\n"
            "Registrar's Office: 710-5624 local 105 | sacli.registrar@gmail.com"
        ),
        (
            "Contact Information", "IBED",
            "How do I contact the IBED Department?",
            "IBED Department contact:\n"
            "• Email: ibedsacli@sacli.edu.ph\n"
            "• Facebook Page: SACLI-Integrated Basic Education Department\n\n"
            "Registrar's Office (for enrollment records):\n"
            "• Email: sacli.registrar@gmail.com\n"
            "• Phone: 710-5624 local 105 | 0933-862-2338 | 0922-898-5919"
        ),

        # ──────────────────────────────────────────────────────────────
        # SHS — Senior High School
        # ──────────────────────────────────────────────────────────────
        (
            "Programs Offered", "SHS",
            "What Senior High School strands does SACLI offer?",
            "SACLI's Senior High School offers strands that empower students with 21st-century skills. Confirmed strands include:\n"
            "• ABM (Accountancy, Business and Management) — Prepares students for business-related college programs. Features academic competitions, vibrant student life, a young teaching team, and involvement of college instructors from the HED department.\n\n"
            "SACLI SHS is also closely integrated with the higher education department, exposing SHS students to college-level facilities, teaching methods, and practical activities.\n\n"
            "For the full and updated list of strands offered (STEM, HUMSS, GAS, TVL, etc.), contact:\n"
            "• Admissions Office: sacli.admission@gmail.com | 0985-922-8238\n"
            "• Registrar's Office: sacli.registrar@gmail.com | 710-5624 local 105"
        ),
        (
            "Admission Requirements", "SHS",
            "What are the admission requirements for Senior High School (SHS) at SACLI?",
            "To apply for Senior High School at SACLI, you can use the online portal at https://sacli.edu.ph/admissions/ and select 'Apply for HED' (SHS is under HED for admissions purposes).\n\n"
            "General document requirements for incoming Grade 11 students typically include:\n"
            "• Form 138 / Report Card from Grade 10\n"
            "• PSA Birth Certificate\n"
            "• Good Moral Character Certificate\n"
            "• 2x2 ID photos\n\n"
            "For transferees from other schools: Honorable Dismissal and certification of grades may also be required.\n\n"
            "Government voucher programs (ESC / SHS Voucher Program) may be available — ask the Registrar's Office or Admissions Office for details.\n\n"
            "Contact:\n"
            "• Admissions/CCO: sacli.admission@gmail.com | 0985-922-8238\n"
            "• Registrar's Office: sacli.registrar@gmail.com | 710-5624 local 105"
        ),
        (
            "Enrollment Steps", "SHS",
            "How do I enroll in SACLI's Senior High School?",
            "Enrollment steps for Senior High School:\n"
            "1. Visit https://sacli.edu.ph/admissions/ and apply online (select HED/SHS)\n"
            "2. Prepare documents: Form 138, birth certificate, good moral certificate, and photos\n"
            "3. Submit documents at the Registrar's Office or upload through the online portal\n"
            "4. Check application status using your Reference Code\n"
            "5. If required, take an entrance exam or attend an interview\n"
            "6. Proceed to the Accounting Office to settle tuition and fees\n"
            "7. Complete enrollment by getting your class schedule\n\n"
            "For questions: sacli.admission@gmail.com | 0985-922-8238"
        ),
        (
            "Scholarships", "SHS",
            "Are there government voucher programs or scholarships for Senior High School students?",
            "Senior High School students may be eligible for government-funded assistance:\n"
            "• SHS Voucher Program — government vouchers that help cover tuition for qualified SHS students in private schools\n"
            "• ESC (Education Service Contracting) — available for incoming Grade 11 students from public JHS\n\n"
            "SACLI also has its own Scholarships and Grants Office (SSGO) that provides financial assistance to qualified and deserving students.\n\n"
            "For scholarship application and details:\n"
            "• SACLI Scholarships and Grants Office — contact through the Admissions Office: sacli.admission@gmail.com | 0985-922-8238\n"
            "• Registrar's Office: sacli.registrar@gmail.com | 710-5624 local 105"
        ),
        (
            "Contact Information", "SHS",
            "Who do I contact for Senior High School inquiries?",
            "For Senior High School inquiries at SACLI:\n"
            "• Admissions / Corporate Communications Office: sacli.admission@gmail.com | 0985-922-8238\n"
            "• Registrar's Office: sacli.registrar@gmail.com | 710-5624 local 105 | 0933-862-2338 | 0922-898-5919\n"
            "• Online admissions portal: https://sacli.edu.ph/admissions/"
        ),

        # ──────────────────────────────────────────────────────────────
        # HED — Higher Education (College)
        # ──────────────────────────────────────────────────────────────
        (
            "Programs Offered", "HED",
            "What college programs does SACLI offer?",
            "SACLI offers the following college degree programs:\n\n"
            "School of Allied Health Sciences (SAHS):\n"
            "• Doctor of Dental Medicine (DMD) — 'The First and Only Dentistry School in Quezon Province'\n"
            "• BS Nursing (BSN) — intensive clinical exposure in pediatrics, NICU, ICU, DR, OR\n"
            "• BS Physical Therapy (BSPT) — 4-year program for health promotion and rehabilitation\n"
            "• BS Midwifery — 4-year program preparing registered midwives\n"
            "• BS Medical Technology — 4-year program, general education + professional courses\n\n"
            "School of Management for International Hospitality and Tourism (SMIHT):\n"
            "• BS Hospitality Management — internationally recognized, with practicum in Canada, Thailand, USA, Singapore, Jordan, Australia\n"
            "• BS Tourism Management — consistent champion in Philippine Tourism Competitions\n\n"
            "College of Criminology (COC):\n"
            "• BS Criminology — 100% board passing rate for 3 consecutive years\n\n"
            "School of Business, Accountancy, Technology, and Engineering (SBATE):\n"
            "• BS Accountancy\n"
            "• BS Management Accounting\n"
            "• BS Business Administration\n"
            "• BS Information Technology\n"
            "• BS Civil Engineering (5-year program)\n"
            "• BS Industrial Engineering (5-year program)\n\n"
            "School of Education, Arts, and Sciences (SEAS):\n"
            "• AB Communication\n"
            "• AB Psychology\n"
            "• BS Secondary Education (BSEd)\n"
            "• BS Elementary Education (BEEd)\n"
            "• BS Technical Vocational Teacher Education — Major in Food Service Management"
        ),
        (
            "Admission Requirements", "HED",
            "What are the admission requirements for college (HED) at SACLI?",
            "To apply for college at SACLI, use the online portal at https://sacli.edu.ph/admissions/ and select 'Apply for HED'.\n\n"
            "General requirements for incoming freshmen:\n"
            "• Form 138 / Senior High School report card or diploma\n"
            "• PSA Birth Certificate\n"
            "• Good Moral Character Certificate\n"
            "• 2x2 ID photos\n\n"
            "For transferees, additional documents are typically required:\n"
            "• Transcript of Records (TOR)\n"
            "• Honorable Dismissal from previous school\n"
            "• Certification of grades\n\n"
            "Some programs may have additional requirements (e.g., entrance exam, interview, or minimum GWA). Contact the specific department or the Admissions Office for program-specific requirements.\n\n"
            "Contact:\n"
            "• Admissions/CCO: sacli.admission@gmail.com | 0985-922-8238\n"
            "• Registrar's Office: sacli.registrar@gmail.com | 710-5624 local 105"
        ),
        (
            "Enrollment Steps", "HED",
            "How do I enroll as a college freshman or transferee at SACLI?",
            "College enrollment process at SACLI:\n\n"
            "For incoming freshmen:\n"
            "1. Apply online at https://sacli.edu.ph/admissions/ (select HED)\n"
            "2. Prepare documents: SHS report card/diploma, birth certificate, good moral certificate, photos\n"
            "3. Submit documents and check your application status with your Reference Code\n"
            "4. Take the entrance exam or attend interview if required by your chosen program\n"
            "5. Receive acceptance and proceed to enrollment\n"
            "6. Pay tuition and fees at the Accounting Office\n"
            "7. Get your class schedule and student ID\n\n"
            "For transferees — additional steps:\n"
            "• Submit Transcript of Records (TOR) and Honorable Dismissal\n"
            "• Undergo credit evaluation at the Registrar's Office\n"
            "• Complete any bridging or removal subjects as required\n\n"
            "Contact: sacli.admission@gmail.com | 0985-922-8238\n"
            "Registrar's: sacli.registrar@gmail.com | 710-5624 local 105"
        ),
        (
            "Programs Offered", "HED",
            "Tell me about SACLI's Dentistry (DMD) program",
            "SACLI's Doctor of Dental Medicine (DMD) program is notable as 'The First and Only Dentistry School in Quezon Province.' "
            "It features highly qualified faculty members who are affiliated with top dentistry schools in Manila. "
            "The program provides students with strong clinical training alongside academic excellence.\n\n"
            "Contact: dmdsacli@sacli.edu.ph | Facebook: SACLI - College of Dentistry\n"
            "Admissions: sacli.admission@gmail.com | 0985-922-8238"
        ),
        (
            "Programs Offered", "HED",
            "Tell me about SACLI's Nursing and Allied Health programs",
            "School of Allied Health Sciences (SAHS) programs:\n\n"
            "• BS Nursing — Students receive intensive clinical exposure in pediatric units, NICU, ICU, delivery room, and operating room to prepare globally competitive nursing graduates.\n"
            "• BS Physical Therapy — 4-year program producing globally competent professionals who promote optimal health and function through movement and rehabilitation services.\n"
            "• BS Midwifery — 4-year program with general education and professional courses preparing registered midwives for higher-level competencies.\n"
            "• BS Medical Technology — 4-year program with general education and professional courses; first three years cover core subjects.\n\n"
            "Contact:\n"
            "• Nursing: sahs@sacli.edu.ph | Facebook: SACLI School of Allied Health Sciences\n"
            "• Physical Therapy: sacliptherapy@gmail.com\n"
            "• Midwifery: bsmidwiferysacli@sacli.edu.ph | Facebook: SACLI BS Midwifery"
        ),
        (
            "Programs Offered", "HED",
            "Tell me about SACLI's Hospitality and Tourism programs",
            "School of Management for International Hospitality and Tourism (SMIHT):\n\n"
            "• BS Hospitality Management — Recipient of the Plaque of Recognition from the Provincial Council of Quezon. Students gain access to:\n"
            "  - International practicum in Canada, Thailand, USA, Singapore, Jordan, and Australia\n"
            "  - Local practicum in deluxe hotels, Class A restaurants, resorts, and in-flight facilities\n"
            "  - Well-equipped facilities: travel counter, suite rooms, institutional kitchen (largest in Region IV), coffee shop, bar, and conference rooms\n"
            "  - Active alumni and hospitality industry network\n\n"
            "• BS Tourism Management — Consistent champion in Philippine Tourism Competitions. Known as 'Home of Successful International Flight Attendants and Travel and Tour Operators.' Opportunities in local and international competitions and culminating activities.\n\n"
            "Contact: smiht@sacli.edu.ph | Facebook: SACLI-School of Management for International Hospitality and Tourism"
        ),
        (
            "Programs Offered", "HED",
            "Tell me about SACLI's Business, Accountancy, IT, and Engineering programs",
            "School of Business, Accountancy, Technology, and Engineering (SBATE) programs:\n\n"
            "• BS Accountancy — Prepares students for careers in accounting and related fields; develops professional accountants, researchers, and responsible citizens.\n"
            "• BS Management Accounting (BSMA) — Trains highly competent practitioners of accountancy with high ethical and moral standards.\n"
            "• BS Business Administration — Trains students for modern corporate settings and entrepreneurship through personalized instructions, simulations, seminars, and practical exposures.\n"
            "• BS Information Technology — Prepares flexible, technologically adept IT professionals through SACLI's Online-Hybrid Learning (SACLI Online-Hybrid Learning).\n"
            "• BS Civil Engineering (5 years) — Covers structural engineering and construction engineering and management.\n"
            "• BS Industrial Engineering (5 years) — Prepares professional industrial engineers.\n\n"
            "Contact:\n"
            "• Business Administration: sacli.bsba2020@gmail.com\n"
            "• Information Technology: bsitsacli@sacli.edu.ph\n"
            "• Accountancy: jpiasacopchapter@gmail.com\n"
            "• Civil Engineering: civilengineeringsacli@gmail.com\n"
            "• Industrial Engineering: piiesaclisc@gmail.com"
        ),
        (
            "Programs Offered", "HED",
            "Tell me about SACLI's Criminology program",
            "SACLI's BS Criminology program under the College of Criminology (COC) has achieved:\n"
            "• 100% board passing rate for three consecutive years\n"
            "• Recognized as the BS Criminology school in Quezon Province with the highest board passing rate in 2018\n\n"
            "The program provides a solid foundation in criminology theory and practice.\n\n"
            "Contact: sacli.collegeofcriminology@gmail.com | Facebook: St. Anne College Lucena, Inc. - College of Criminology"
        ),
        (
            "Programs Offered", "HED",
            "Tell me about SACLI's Education, Arts and Sciences programs",
            "School of Education, Arts, and Sciences (SEAS) programs:\n\n"
            "• AB Communication — Interdisciplinary curriculum covering multimedia, digital video production, and journalism. Develops creativity and competitive skills.\n"
            "• AB Psychology — Prepares students for careers in clinical psychology, school psychology, and industrial-organizational psychology; makes a difference in people's lives through counseling and community service.\n"
            "• BS Secondary Education (BSEd) — Small class sizes for major subjects and LET preparation; diverse field studies and teaching experiences.\n"
            "• BS Elementary Education (BEEd) — Strong foundation in education theory and practice.\n"
            "• BS Technical Vocational Teacher Education — Major in Food Service Management.\n\n"
            "Contact: seas@sacli.edu.ph | Psychology: abpsychsacli@sacli.edu.ph | Facebook: SACLI - College of Teacher Education"
        ),
        (
            "Contact Information", "HED",
            "Who do I contact for college admission inquiries?",
            "For college admission inquiries at SACLI:\n"
            "• Admissions / Corporate Communications Office: sacli.admission@gmail.com | 0985-922-8238\n"
            "• Registrar's Office: sacli.registrar@gmail.com | 710-5624 local 105 | 0933-862-2338 | 0922-898-5919\n"
            "• Accounting Office (for tuition): sacli.acctng@gmail.com | 710-5624 local 103\n\n"
            "For program-specific questions, contact the department directly (see SACLI contact list at https://sacli.edu.ph/contact/).\n"
            "Online admissions: https://sacli.edu.ph/admissions/"
        ),
        (
            "Tuition and Payment", "HED",
            "How do I pay tuition fees? Who do I contact for billing?",
            "All tuition and fee payments are handled by the Accounting Office:\n"
            "• Email: sacli.acctng@gmail.com\n"
            "• Phone: 710-5624 local 103 | 0933-862-2338 | 0922-898-5919\n\n"
            "The Accounting Office handles:\n"
            "• Payment of tuition and miscellaneous fees\n"
            "• Payment schemes (full payment, installment options)\n"
            "• Official Receipts and statements of account\n\n"
            "For specific tuition amounts per program, contact the Accounting Office or the Admissions Office directly:\n"
            "• Admissions: sacli.admission@gmail.com | 0985-922-8238"
        ),
        (
            "Scholarships", "HED",
            "What scholarships and financial assistance does SACLI offer to college students?",
            "SACLI has a dedicated Scholarships and Grants Office (SSGO) that supports students with financial need or academic merit.\n\n"
            "The SSGO's mission:\n"
            "• Provide funds, financial assistance, and scholarship/grant programs\n"
            "• Eliminate financial barriers to quality education for qualified and deserving students\n"
            "• Focus on students with exceptional economic and educational needs\n\n"
            "Scholarship types may include academic scholarships, government-funded grants (TES, TDP), and institutional grants.\n\n"
            "To apply or inquire about scholarships:\n"
            "• Contact the Admissions / CCO Office: sacli.admission@gmail.com | 0985-922-8238\n"
            "• Or the Registrar's Office: sacli.registrar@gmail.com | 710-5624 local 105\n\n"
            "Details on specific scholarship slots, eligibility, retention requirements, and deadlines are provided by the SSGO directly."
        ),

        # ──────────────────────────────────────────────────────────────
        # TESDA
        # ──────────────────────────────────────────────────────────────
        (
            "Programs Offered", "TESDA",
            "What TESDA programs does SACLI offer?",
            "SACLI offers TESDA (Technical Education and Skills Development Authority) programs under its TESDA unit. "
            "TESDA courses lead to national certifications and are regulated by RA 7796 (Technical Education and Skills Development Act of 1994).\n\n"
            "SACLI's TESDA programs provide technical-vocational education and skills development. "
            "For the current list of available courses and qualifications (e.g., NC II programs), contact:\n"
            "• SACLI TESDA Office: stanne.tesda@gmail.com\n"
            "• Facebook: SACLI Tesda Affairs\n"
            "• Or the Admissions Office: sacli.admission@gmail.com | 0985-922-8238"
        ),
        (
            "Admission Requirements", "TESDA",
            "What are the admission requirements for TESDA courses at SACLI?",
            "TESDA course admission requirements at SACLI generally include:\n"
            "• Minimum educational attainment (varies by course — some accept ALS completers or high school graduates)\n"
            "• PSA Birth Certificate\n"
            "• 2x2 ID photos\n\n"
            "Some courses may have additional requirements based on the specific qualification level.\n\n"
            "For complete requirements and to apply:\n"
            "• SACLI TESDA Office: stanne.tesda@gmail.com | Facebook: SACLI Tesda Affairs\n"
            "• Admissions Office: sacli.admission@gmail.com | 0985-922-8238"
        ),
        (
            "Enrollment Steps", "TESDA",
            "How do I enroll in a TESDA course at SACLI?",
            "To enroll in a TESDA program at SACLI:\n"
            "1. Contact the TESDA Office to inquire about available courses and schedules: stanne.tesda@gmail.com\n"
            "2. Prepare required documents (birth certificate, educational records, photos)\n"
            "3. Submit your application and documents to the TESDA Office\n"
            "4. Pay the program fee at the Accounting Office\n"
            "5. Attend the training program on your scheduled dates\n"
            "6. Upon completion, undergo TESDA national assessment for certification (NC I / NC II)\n\n"
            "Contact: stanne.tesda@gmail.com | Facebook: SACLI Tesda Affairs\n"
            "Accounting Office (for payment): sacli.acctng@gmail.com | 710-5624 local 103"
        ),
        (
            "Contact Information", "TESDA",
            "How do I contact SACLI's TESDA office?",
            "SACLI TESDA contact:\n"
            "• Email: stanne.tesda@gmail.com\n"
            "• Facebook Page: SACLI Tesda Affairs\n\n"
            "For general enrollment questions, you may also contact:\n"
            "• Admissions Office: sacli.admission@gmail.com | 0985-922-8238\n"
            "• Registrar's Office: sacli.registrar@gmail.com | 710-5624 local 105"
        ),

        # ──────────────────────────────────────────────────────────────
        # Cross-cutting / FAQs
        # ──────────────────────────────────────────────────────────────
        (
            "Student Services", "GENERAL",
            "How do I check my application status after applying online?",
            "After submitting your application through the SACLI online admissions portal (https://sacli.edu.ph/admissions/), "
            "you will receive a Reference Code. Use this Reference Code to check your application status by visiting the admissions portal and clicking 'Check Status'.\n\n"
            "If you have questions about your application, contact:\n"
            "• Admissions / CCO: sacli.admission@gmail.com | 0985-922-8238"
        ),
        (
            "Student Services", "GENERAL",
            "What documents are usually required for admission at SACLI?",
            "While exact requirements vary by level, the commonly required documents for admission at SACLI are:\n"
            "• PSA-issued Birth Certificate\n"
            "• Most recent Report Card / Form 138 (or Transcript of Records for transferees)\n"
            "• Certificate of Good Moral Character from previous school\n"
            "• 2x2 ID photos (usually 2–4 copies)\n"
            "• Honorable Dismissal (for transferees)\n\n"
            "Some programs may also require:\n"
            "• Entrance exam results\n"
            "• Interview with department faculty\n"
            "• Medical certificate or health clearance (especially for health-related programs)\n\n"
            "For complete requirements: sacli.registrar@gmail.com | 710-5624 local 105\n"
            "Or apply online: https://sacli.edu.ph/admissions/"
        ),
        (
            "Student Services", "GENERAL",
            "Is there a guidance or psychological test as part of SACLI admission?",
            "Some programs at SACLI may include a guidance interview or psychological assessment as part of the admission process. "
            "This is typically handled by the Guidance Office and is done to ensure appropriate support for incoming students.\n\n"
            "For details on whether your chosen program requires this, contact:\n"
            "• Admissions Office: sacli.admission@gmail.com | 0985-922-8238\n"
            "• Registrar's Office: sacli.registrar@gmail.com | 710-5624 local 105"
        ),
        (
            "Scholarships", "GENERAL",
            "How do I apply for a scholarship at SACLI?",
            "SACLI has a Scholarships and Grants Office (SSGO) that manages all scholarship and financial assistance programs.\n\n"
            "To apply:\n"
            "1. Contact the Admissions Office or Registrar's Office to ask about currently available scholarship programs and their deadlines\n"
            "2. Prepare the required documents (academic records, income documents, recommendation letters — varies by scholarship type)\n"
            "3. Submit your application to the SSGO before the deadline\n"
            "4. Wait for the results announcement\n\n"
            "Scholarships are typically renewable per year/semester upon meeting retention requirements (GWA, conduct, etc.).\n\n"
            "Contact to start:\n"
            "• Admissions/CCO: sacli.admission@gmail.com | 0985-922-8238\n"
            "• Registrar's Office: sacli.registrar@gmail.com | 710-5624 local 105"
        ),
        (
            "Tuition and Payment", "GENERAL",
            "What are SACLI's payment options for tuition fees?",
            "For information about tuition fees, payment schedules, and modes of payment, contact the Accounting Office directly:\n"
            "• Email: sacli.acctng@gmail.com\n"
            "• Phone: 710-5624 local 103 | 0933-862-2338 | 0922-898-5919\n\n"
            "The Accounting Office can provide details on:\n"
            "• Tuition amounts per level/program\n"
            "• Payment schemes (full payment, installment, per-term)\n"
            "• Accepted payment modes (cash, bank deposit, online payment, GCash, etc.)\n"
            "• Down payment requirements for enrollment\n"
            "• Penalties for late payment\n"
            "• Refund policy for withdrawals\n"
            "• Sibling discounts or early payment discounts (if applicable)"
        ),
    ]

    async with get_db_context() as db:
        from sqlalchemy import select as sa_select
        from models.schemas import KBCategory, KnowledgeBase

        # Build a lookup: (category_name, department) -> category_id
        result = await db.execute(sa_select(KBCategory))
        all_categories = result.scalars().all()
        cat_lookup = {(c.name, c.department): c.id for c in all_categories}

        # Check how many KB entries already exist
        kb_result = await db.execute(sa_select(KnowledgeBase))
        existing_count = len(kb_result.scalars().all())
        if existing_count > 0:
            print(f"  ⚠ {existing_count} KB entries already exist, skipping...")
            return

        inserted = 0
        skipped = 0
        for (cat_name, dept, title, content) in kb_entries_raw:
            cat_id = cat_lookup.get((cat_name, dept))
            if cat_id is None:
                print(f"  ⚠ Category not found: ({cat_name}, {dept}) — skipping '{title}'")
                skipped += 1
                continue

            try:
                embedding = embed(content)
            except Exception as e:
                print(f"  ⚠ Embedding failed for '{title}': {e} — skipping")
                skipped += 1
                continue

            entry = KnowledgeBase(
                category_id=cat_id,
                title=title,
                content=content,
                embedding=embedding,
                is_active=True,
                updated_by=None,
            )
            db.add(entry)
            inserted += 1

        await db.commit()
        print(f"  ✓ Inserted {inserted} KB entries ({skipped} skipped)")
        if skipped > 0:
            print("    Run seed_categories() first if categories are missing.")


async def seed_database():
    """Main seed function"""
    print("=" * 60)
    print("ADMIT Database Seeding")
    print("=" * 60)
    
    await seed_categories()
    await seed_admin_user()
    await seed_sample_kb_entries()
    
    print("\n" + "=" * 60)
    print("Database seeding completed!")
    print("=" * 60)
    print("\nYou can now:")
    print("  1. Start the server: uvicorn main:app --reload")
    print("  2. Login to admin dashboard with:")
    print("     Username: admin")
    print("     Password: admin123")
    print("  ⚠  IMPORTANT: Change the admin password after first login!")
    print("  3. The chatbot now has real SACLI KB content and can answer questions about:")
    print("     - Programs offered (IBED, SHS, HED, TESDA)")
    print("     - Admission requirements and enrollment steps")
    print("     - Contact information for all offices")
    print("     - Scholarships and financial assistance")
    print("     - Tuition and payment")
    print("  4. Add more specific KB entries (tuition amounts, exact exam details, etc.)")
    print("     through the admin dashboard as you gather them from SACLI offices.")


if __name__ == "__main__":
    asyncio.run(seed_database())
