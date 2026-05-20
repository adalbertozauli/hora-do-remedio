APP_STYLE = """
QMainWindow {
    background: #f5f7fa;
}
QLabel {
    color: #17202a;
    font-size: 18px;
    font-weight: 600;
}
QPushButton {
    background: #1f4e79;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 12px 18px;
    font-size: 17px;
    font-weight: 700;
}
QPushButton:hover {
    background: #173b5c;
}
QPushButton:disabled {
    background: #9aa8b5;
}
QTextEdit, QTableWidget, QLineEdit {
    background: white;
    color: #111827;
    border: 1px solid #aeb8c2;
    border-radius: 6px;
    font-size: 17px;
    selection-background-color: #cfe4ff;
}
QHeaderView::section {
    background: #dbe8f4;
    color: #111827;
    border: 1px solid #aeb8c2;
    padding: 8px;
    font-size: 16px;
    font-weight: 700;
}
QStatusBar {
    color: #17202a;
    font-size: 15px;
}
QProgressBar {
    background: #e5edf5;
    border: 1px solid #aeb8c2;
    border-radius: 6px;
}
QProgressBar::chunk {
    background: #1f4e79;
    border-radius: 6px;
}
QMessageBox {
    background: #f5f7fa;
}
QMessageBox QLabel {
    color: #111827;
    font-size: 17px;
    font-weight: 500;
}
QMessageBox QPushButton {
    min-width: 110px;
    min-height: 42px;
    padding: 10px 18px;
    background: #1f4e79;
    color: white;
    border-radius: 6px;
    font-size: 16px;
    font-weight: 700;
}
"""
