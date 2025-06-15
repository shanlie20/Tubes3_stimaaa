import sys
from PySide6.QtWidgets import QApplication
from .ui.main_window import MainWindow


def main():
    """Entry point of the application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()