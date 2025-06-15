from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QScrollArea,
    QSizePolicy,
    QGridLayout # Perlu ini lagi untuk layout job/edu detail
)
from src.core.summary import get_candidate_summary

class SummaryPage(QWidget):
    """Displays extracted summary information for a single candidate CV."""

    back_requested = Signal()

    def __init__(self):
        super().__init__()
        self._build_ui()
        self.current_applicant_id = None

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        self.setStyleSheet("""
            SummaryPage {
                background-color: #f0f0f0;
            }
            QLabel#h1 {
                font-size: 20pt;
                font-weight: bold;
                color: black;
            }
            QLabel#h2 {
                font-size: 16pt;
                font-weight: bold;
                color: black;
            }
            QLabel#section_header {
                font-size: 14pt;
                font-weight: bold;
                color: black;
                margin-top: 15px;
            }
            QPushButton {
                padding: 8px 15px;
                border-radius: 5px;
                border: 1px solid #ccc;
                background-color: white;
                color: black;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QFrame#SectionFrame {
                background-color: #e6e6e6;
                border: none;
                border-radius: 8px;
            }
            QFrame#SectionFrame QLabel {
                color: black;
            }
            QLabel.info_text {
                font-size: 10pt;
                color: #333;
            }
            QLabel.sub_period_text {
                font-size: 10pt;
                color: #555;
            }
            QLabel#skill_tag {
                background-color: #d3d3d3;
                color: black;
                padding: 4px 8px;
                border-radius: 5px;
                font-size: 10pt;
            }
            QLabel.description_text {
                font-size: 10pt;
                color: #333;
            }
            QLabel.section_item_header { /* Gaya untuk role/degree di dalam section item */
                font-weight: bold;
                font-size: 10pt;
                color: #222;
            }
            QLabel.section_item_detail { /* Gaya untuk detail seperti company, period */
                font-size: 9pt;
                color: #555;
            }
            QLabel.section_item_description { /* Gaya untuk deskripsi multi-baris */
                font-size: 9pt;
                color: #444;
                margin-left: 10px; /* Indentasi untuk deskripsi */
                margin-top: 5px;
            }
        """)

        back_btn_layout = QHBoxLayout()
        back_btn = QPushButton("← Back to Search")
        back_btn.clicked.connect(self.back_requested.emit)
        back_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        back_btn_layout.addWidget(back_btn)
        back_btn_layout.addStretch(1)
        root.addLayout(back_btn_layout)

        title_lbl = QLabel("CV Summary")
        title_lbl.setObjectName("h1")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title_lbl)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget) # Jadikan self.content_layout
        self.content_layout.setSpacing(10)

        self._create_personal_info_section(self.content_layout)
        self._create_skills_section(self.content_layout)
        # self._create_job_history_section(self.content_layout) # Ini akan diganti dengan _add_job_history_entry
        # self._create_education_section(self.content_layout) # Ini akan diganti dengan _add_education_entry

        self.job_history_section_layout = None # Akan diinisialisasi di _create_job_history_section_base
        self.education_section_layout = None # Akan diinisialisasi di _create_education_section_base

        # Tambahkan layout dasar untuk Job History dan Education sekali
        self._create_job_history_section_base(self.content_layout)
        self._create_education_section_base(self.content_layout)

        self.content_layout.addStretch(1)

        scroll_area.setWidget(content_widget)
        root.addWidget(scroll_area, 1)

    def _create_section_wrapper(self, parent_layout, has_header: bool = True):
        section_wrapper_frame = QFrame()
        section_wrapper_frame.setObjectName("SectionFrame")

        section_layout = QVBoxLayout(section_wrapper_frame)
        section_layout.setContentsMargins(20, 15, 20, 15)
        section_layout.setSpacing(5)

        parent_layout.addWidget(section_wrapper_frame)
        return section_layout, section_wrapper_frame

    def _create_personal_info_section(self, parent_layout):
        self.name_lbl = QLabel("Gantar Puspasari")
        self.name_lbl.setObjectName("h2")
        parent_layout.addWidget(self.name_lbl)

        info_section_layout, _ = self._create_section_wrapper(parent_layout, has_header=False)

        self.birthdate_lbl = QLabel("Birthdate: -")
        self.address_lbl = QLabel("Address: -")
        self.phone_lbl = QLabel("Phone: -")

        self.birthdate_lbl.setObjectName("info_text")
        self.address_lbl.setObjectName("info_text")
        self.phone_lbl.setObjectName("info_text")

        info_section_layout.addWidget(self.birthdate_lbl)
        info_section_layout.addWidget(self.address_lbl)
        info_section_layout.addWidget(self.phone_lbl)

    def _create_skills_section(self, parent_layout):
        skills_lbl = QLabel("Skills:")
        skills_lbl.setObjectName("section_header")
        parent_layout.addWidget(skills_lbl)

        skills_section_layout, _ = self._create_section_wrapper(parent_layout)

        self.skills_container = QWidget()
        self.skills_layout = QHBoxLayout(self.skills_container)
        self.skills_layout.setContentsMargins(0,0,0,0)
        self.skills_layout.setSpacing(8)
        self.skills_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        skills_section_layout.addWidget(self.skills_container)

    # --- Base sections for Job History and Education ---
    def _create_job_history_section_base(self, parent_layout):
        job_history_lbl = QLabel("Job History:")
        job_history_lbl.setObjectName("section_header")
        parent_layout.addWidget(job_history_lbl)

        job_history_wrapper_layout, _ = self._create_section_wrapper(parent_layout)
        self.job_history_section_layout = QVBoxLayout() # This will hold individual job entries
        self.job_history_section_layout.setContentsMargins(0,0,0,0)
        self.job_history_section_layout.setSpacing(10) # Spacing between job entries
        job_history_wrapper_layout.addLayout(self.job_history_section_layout)

    def _create_education_section_base(self, parent_layout):
        education_lbl = QLabel("Education:")
        education_lbl.setObjectName("section_header")
        parent_layout.addWidget(education_lbl)

        education_wrapper_layout, _ = self._create_section_wrapper(parent_layout)
        self.education_section_layout = QVBoxLayout() # This will hold individual education entries
        self.education_section_layout.setContentsMargins(0,0,0,0)
        self.education_section_layout.setSpacing(10) # Spacing between education entries
        education_wrapper_layout.addLayout(self.education_section_layout)

    # --- Methods to add individual entries (called dynamically) ---
    def _add_job_history_entry(self, role: str, period: str, company: str, description: str):
        entry_widget = QWidget()
        entry_layout = QVBoxLayout(entry_widget)
        entry_layout.setContentsMargins(0,0,0,0)
        entry_layout.setSpacing(2)

        role_company_period_layout = QHBoxLayout()
        role_lbl = QLabel(role)
        role_lbl.setObjectName("section_item_header")
        
        company_period_lbl = QLabel(f"{company} ({period})")
        company_period_lbl.setObjectName("section_item_detail")

        role_company_period_layout.addWidget(role_lbl)
        role_company_period_layout.addSpacing(5) # Spasi antara role dan company/period
        role_company_period_layout.addWidget(company_period_lbl)
        role_company_period_layout.addStretch(1)
        entry_layout.addLayout(role_company_period_layout)
        
        if description:
            desc_lbl = QLabel(description)
            desc_lbl.setObjectName("section_item_description")
            desc_lbl.setWordWrap(True)
            entry_layout.addWidget(desc_lbl)
        
        self.job_history_section_layout.addWidget(entry_widget)

    def _add_education_entry(self, major_field: str, institution: str, period: str):
        entry_widget = QWidget()
        entry_layout = QVBoxLayout(entry_widget)
        entry_layout.setContentsMargins(0,0,0,0)
        entry_layout.setSpacing(2)

        major_inst_layout = QHBoxLayout()
        major_lbl = QLabel(major_field)
        major_lbl.setObjectName("section_item_header")
        
        institution_lbl = QLabel(f"({institution})")
        institution_lbl.setObjectName("section_item_detail")

        major_inst_layout.addWidget(major_lbl)
        major_inst_layout.addSpacing(5)
        major_inst_layout.addWidget(institution_lbl)
        major_inst_layout.addStretch(1)
        entry_layout.addLayout(major_inst_layout)
        
        if period:
            period_lbl = QLabel(period)
            period_lbl.setObjectName("section_item_detail")
            entry_layout.addWidget(period_lbl)
            
        self.education_section_layout.addWidget(entry_widget)

    def _create_skill_tag(self, skill_name):
        skill_tag = QLabel(skill_name)
        skill_tag.setObjectName("skill_tag")
        skill_tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return skill_tag

    def _clear_skills(self):
        for i in reversed(range(self.skills_layout.count())):
            item = self.skills_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
            elif item.spacerItem():
                self.skills_layout.removeItem(item)
        self.skills_layout.addStretch(1)

    def _clear_job_history_entries(self):
        if self.job_history_section_layout:
            while self.job_history_section_layout.count():
                item = self.job_history_section_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
                elif item.layout():
                    # Clear nested layouts if any, though _add_job_history_entry adds widgets directly
                    self._clear_layout(item.layout())
        
    def _clear_education_entries(self):
        if self.education_section_layout:
            while self.education_section_layout.count():
                item = self.education_section_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
                elif item.layout():
                    self._clear_layout(item.layout()) # Just in case

    def _clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget() is not None:
                    item.widget().deleteLater()
                elif item.layout() is not None:
                    self._clear_layout(item.layout())


    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def load_candidate(self, applicant_id: int, cv_path: str, cv_content: str):

        self.current_applicant_id = applicant_id

        candidate_data = get_candidate_summary(applicant_id, cv_path, cv_content)
        print(f"Loading candidate data for ID {applicant_id}: {candidate_data}")
        if not candidate_data:
            self.name_lbl.setText("Candidate Not Found")
            self.birthdate_lbl.setText("Birthdate: -")
            self.address_lbl.setText("Address: -")
            self.phone_lbl.setText("Phone: -")
            # Clear job history and education sections
            self._clear_job_history_entries()
            self._clear_education_entries()
            self._clear_skills()
            return

        full_name = f"{candidate_data.get('first_name', '')} {candidate_data.get('last_name', '')}".strip()
        self.name_lbl.setText(full_name or "Unknown Candidate")

        birthdate = candidate_data.get('date_of_birth')
        if birthdate:
            if hasattr(birthdate, 'strftime'):
                self.birthdate_lbl.setText(f"Birthdate: {birthdate.strftime('%m-%d-%Y')}")
            else:
                self.birthdate_lbl.setText(f"Birthdate: {str(birthdate)}")
        else:
            self.birthdate_lbl.setText("Birthdate: -")

        self.address_lbl.setText(f"Address: {candidate_data.get('address', '-')}")
        self.phone_lbl.setText(f"Phone: {candidate_data.get('phone_number', '-')}")

        # Update skills
        self._clear_skills()
        skills = candidate_data.get('skills', []) # Mengambil list of strings dari summary
        if not skills:
             skills = ["No Skills Found"] # Default jika kosong
        for skill in skills:
            skill_tag = self._create_skill_tag(skill)
            if skill_tag:
                self.skills_layout.insertWidget(self.skills_layout.count() - 1, skill_tag)

        # Update Job History
        self._clear_job_history_entries() # Bersihkan entri lama
        job_history = candidate_data.get('job_history', []) # Mengambil list of dicts dari summary
        if not job_history:
            # Tampilkan pesan jika tidak ada job history
            no_job_lbl = QLabel("No job history extracted.")
            no_job_lbl.setObjectName("description_text")
            self.job_history_section_layout.addWidget(no_job_lbl)
        else:
            for job in job_history:
                self._add_job_history_entry(
                    role=job.get('role', '-'),
                    period=job.get('period', '-'),
                    company=job.get('company', '-'),
                    description=job.get('description', '')
                )
        
        # Update Education
        self._clear_education_entries() # Bersihkan entri lama
        education = candidate_data.get('education', []) # Mengambil list of dicts dari summary
        if not education:
            # Tampilkan pesan jika tidak ada education
            no_edu_lbl = QLabel("No education extracted.")
            no_edu_lbl.setObjectName("description_text")
            self.education_section_layout.addWidget(no_edu_lbl)
        else:
            for edu in education:
                self._add_education_entry(
                    major_field=edu.get('major_field', '-'),
                    institution=edu.get('institution', '-'),
                    period=edu.get('period', '')
                )