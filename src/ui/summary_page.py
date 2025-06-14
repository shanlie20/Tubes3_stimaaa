from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QScrollArea,
    QSizePolicy
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

        # Set background color for the entire page and global styles
        self.setStyleSheet("""
            SummaryPage {
                background-color: #f0f0f0; /* Latar belakang abu-abu terang halaman */
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
                margin-top: 15px; /* Add some space above section headers */
            }
            QPushButton {
                padding: 8px 15px;
                border-radius: 5px;
                border: 1px solid #ccc; /* Border sedikit terlihat */
                background-color: white; /* Tombol putih */
                color: black;
            }
            QPushButton:hover {
                background-color: #e0e0e0; /* Latar belakang abu-abu saat kursor di atas */
            }
            /* Styling for the section wrapper frames */
            QFrame#SectionFrame { /* Menggunakan ID Selector untuk QFrame */
                background-color: #e6e6e6; /* Sedikit lebih gelap dari background halaman */
                border: none; /* Hilangkan border */
                border-radius: 8px; /* Sudut membulat */
                /* Padding sudah diatur di _create_section_wrapper, tidak di sini */
            }
            /* Styling for labels inside the gray frames */
            QFrame#SectionFrame QLabel { /* Ini akan berlaku untuk semua QLabel di dalam QFrame dengan ID SectionFrame */
                color: black; /* Pastikan teks berwarna hitam */
            }
            QLabel.info_text { /* Kelas khusus untuk teks info agar sedikit lebih kecil */
                font-size: 10pt;
                color: #333; /* Warna teks lebih gelap untuk info */
            }
            QLabel.sub_period_text {
                font-size: 10pt;
                color: #555;
            }
            QLabel#skill_tag { /* Menggunakan ID Selector untuk skill tag */
                background-color: #d3d3d3; /* Warna tag skill sesuai gambar (agak gelap) */
                color: black; /* Warna teks tag skill sesuai gambar */
                padding: 4px 8px;
                border-radius: 5px; /* Sedikit membulat */
                font-size: 10pt;
            }
            QLabel.description_text {
                font-size: 10pt;
                color: #333;
            }
        """)

        # Back button
        back_btn_layout = QHBoxLayout()
        back_btn = QPushButton("← Back to Search")
        back_btn.clicked.connect(self.back_requested.emit)
        back_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        back_btn_layout.addWidget(back_btn)
        back_btn_layout.addStretch(1)
        root.addLayout(back_btn_layout)

        # Page title
        title_lbl = QLabel("CV Summary")
        title_lbl.setObjectName("h1")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title_lbl)

        # Scroll area for the content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # Content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(10) # Reduced spacing between sections for tighter boxes

        # Personal Information Section
        self._create_personal_info_section(content_layout)

        # Skills Section
        self._create_skills_section(content_layout)

        # Job History Section
        self._create_job_history_section(content_layout)

        # Education Section
        self._create_education_section(content_layout)

        content_layout.addStretch(1)

        scroll_area.setWidget(content_widget)
        root.addWidget(scroll_area, 1)

    def _create_section_wrapper(self, parent_layout, has_header: bool = True):
        """Creates a common wrapper for each section (personal info, skills, job, education)."""
        section_wrapper_frame = QFrame()
        section_wrapper_frame.setObjectName("SectionFrame") # Using ID Selector for styling

        section_layout = QVBoxLayout(section_wrapper_frame)
        # Padding di dalam frame untuk content
        section_layout.setContentsMargins(20, 15, 20, 15)
        section_layout.setSpacing(5) # Spacing antar item di dalam section

        # Adding the frame to the parent layout
        parent_layout.addWidget(section_wrapper_frame)
        return section_layout, section_wrapper_frame

    def _create_personal_info_section(self, parent_layout):
        """Create personal information section with candidate details"""
        # Candidate name (main header for this section)
        self.name_lbl = QLabel("Gantar Puspasari") # Placeholder
        self.name_lbl.setObjectName("h2")
        parent_layout.addWidget(self.name_lbl)

        # Use the new section wrapper
        info_section_layout, _ = self._create_section_wrapper(parent_layout, has_header=False)

        # Personal info labels
        self.birthdate_lbl = QLabel("Birthdate: -")
        self.address_lbl = QLabel("Address: -")
        self.phone_lbl = QLabel("Phone: -")

        # Set object name for styling
        self.birthdate_lbl.setObjectName("info_text")
        self.address_lbl.setObjectName("info_text")
        self.phone_lbl.setObjectName("info_text")

        info_section_layout.addWidget(self.birthdate_lbl)
        info_section_layout.addWidget(self.address_lbl)
        info_section_layout.addWidget(self.phone_lbl)

    def _create_skills_section(self, parent_layout):
        """Create skills section"""
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
        # No vertical stretch here, the wrapper's layout handles it implicitly via padding

    def _create_job_history_section(self, parent_layout):
        """Create job history section"""
        job_history_lbl = QLabel("Job History:")
        job_history_lbl.setObjectName("section_header")
        parent_layout.addWidget(job_history_lbl)

        job_section_layout, _ = self._create_section_wrapper(parent_layout)

        # Role and Period on one line (or styled to look like it)
        role_period_layout = QHBoxLayout()
        self.job_role_lbl = QLabel("ACCOUNTANT") # Placeholder
        self.job_role_lbl.setStyleSheet("font-weight: bold;")
        self.job_role_lbl.setObjectName("info_text")

        self.job_period_lbl = QLabel("2003-2004") # Placeholder
        self.job_period_lbl.setObjectName("sub_period_text")

        role_period_layout.addWidget(self.job_role_lbl)
        role_period_layout.addWidget(self.job_period_lbl)
        role_period_layout.addStretch(1)

        job_section_layout.addLayout(role_period_layout)

        # Description on a new line
        self.job_description_lbl = QLabel("Leading the organization's technology strategies") # Placeholder
        self.job_description_lbl.setObjectName("description_text")
        job_section_layout.addWidget(self.job_description_lbl)

    def _create_education_section(self, parent_layout):
        """Create education section"""
        education_lbl = QLabel("Education:")
        education_lbl.setObjectName("section_header")
        parent_layout.addWidget(education_lbl)

        edu_section_layout, _ = self._create_section_wrapper(parent_layout)

        # Degree and Institution on one line, period on another
        degree_inst_layout = QHBoxLayout()
        self.edu_degree_lbl = QLabel("Informatics Engineering") # Placeholder
        self.edu_degree_lbl.setStyleSheet("font-weight: bold;")
        self.edu_degree_lbl.setObjectName("info_text")

        self.edu_institution_lbl = QLabel("(Institut Teknologi Bandung)") # Placeholder
        self.edu_institution_lbl.setObjectName("sub_period_text")

        degree_inst_layout.addWidget(self.edu_degree_lbl)
        degree_inst_layout.addWidget(self.edu_institution_lbl)
        degree_inst_layout.addStretch(1)

        edu_section_layout.addLayout(degree_inst_layout)

        self.edu_period_lbl = QLabel("2022-2026") # Placeholder
        self.edu_period_lbl.setObjectName("sub_period_text")
        edu_section_layout.addWidget(self.edu_period_lbl)

    def _create_skill_tag(self, skill_name):
        """Create a skill tag widget"""
        skill_tag = QLabel(skill_name)
        skill_tag.setObjectName("skill_tag") # Use ID Selector for styling
        skill_tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return skill_tag

    def _clear_skills(self):
        """Clear existing skill tags"""
        for i in reversed(range(self.skills_layout.count())):
            item = self.skills_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
            elif item.spacerItem():
                self.skills_layout.removeItem(item)
        self.skills_layout.addStretch(1)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def load_candidate(self, applicant_id: int):
        """Load candidate details from database using applicant_id."""
        self.current_applicant_id = applicant_id

        candidate_data = get_candidate_summary(applicant_id)

        if not candidate_data:
            self.name_lbl.setText("Candidate Not Found")
            self.birthdate_lbl.setText("Birthdate: -")
            self.address_lbl.setText("Address: -")
            self.phone_lbl.setText("Phone: -")
            self.job_role_lbl.setText("Role: -")
            self.job_period_lbl.setText("Period: -")
            self.job_description_lbl.setText("Description: -")
            self.edu_degree_lbl.setText("Degree: -")
            self.edu_institution_lbl.setText("Institution: -")
            self.edu_period_lbl.setText("Period: -")
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

        role = candidate_data.get('role', '-')
        self.job_role_lbl.setText(role or "-")
        self.job_period_lbl.setText(candidate_data.get('job_period', '2003-2004'))
        self.job_description_lbl.setText(candidate_data.get('job_description', 'Leading the organization\'s technology strategies'))

        self._clear_skills()
        actual_skills = candidate_data.get('skills', [])
        if not actual_skills:
             actual_skills = ["React", "Express", "HTML"]
        for skill in actual_skills:
            skill_tag = self._create_skill_tag(skill)
            self.skills_layout.insertWidget(self.skills_layout.count() - 1, skill_tag)

        self.edu_degree_lbl.setText(candidate_data.get('edu_degree', 'Informatics Engineering'))
        self.edu_institution_lbl.setText(f"({candidate_data.get('edu_institution', 'Institut Teknologi Bandung')})")
        self.edu_period_lbl.setText(candidate_data.get('edu_period', '2022-2026'))