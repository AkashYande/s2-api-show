from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QComboBox, QLabel, QTreeWidget, QHeaderView)
from PySide6.QtCore import Qt

class S2UI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("S2 Show Manager")
        self.setMinimumSize(800, 600)
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                color: #ffffff;
            }
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #e0e0e0;
            }
            QComboBox {
                padding: 5px;
                border: 1px solid #404040;
                border-radius: 3px;
                background-color: #2d2d2d;
                color: #ffffff;
                min-width: 200px;
            }
            QComboBox:hover {
                border: 1px solid #505050;
                background-color: #353535;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 20px;
            }
            QComboBox::down-arrow {
                image: none;
            }
            QTreeWidget {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 3px;
                alternate-background-color: #333333;
                color: #ffffff;
            }
            QTreeWidget::item {
                padding: 5px;
            }
            QTreeWidget::item:hover {
                background-color: #383838;
            }
            QTreeWidget::item:selected {
                background-color: #0066cc;
                color: #ffffff;
            }
            QTreeWidget QHeaderView::section {
                background-color: #252525;
                padding: 5px;
                border: none;
                color: #ffffff;
                font-weight: bold;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 14px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #404040;
                min-height: 20px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #505050;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                background-color: #2d2d2d;
                height: 14px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background-color: #404040;
                min-width: 20px;
                border-radius: 3px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #505050;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Show selection area
        show_layout = QHBoxLayout()
        show_layout.setSpacing(10)
        show_label = QLabel("Select Show:")
        self.show_combo = QComboBox()
        
        # Status filter area
        status_label = QLabel("Filter Status:")
        self.status_combo = QComboBox()
        
        # Add widgets to show layout with proper spacing
        show_layout.addWidget(show_label)
        show_layout.addWidget(self.show_combo)
        show_layout.addSpacing(20)
        show_layout.addWidget(status_label)
        show_layout.addWidget(self.status_combo)
        show_layout.addStretch()
        
        # Create a container for the header section
        header_container = QWidget()
        header_container.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-radius: 5px;
                border: 1px solid #404040;
            }
        """)
        header_container.setLayout(show_layout)
        header_container.setMinimumHeight(60)
        layout.addWidget(header_container)
        
        # Tree widget setup
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels([
            "Name", "Type", "ID", "Status", "Due Date", "Assigned To"
        ])
        self.tree_widget.setColumnCount(6)
        self.tree_widget.setAlternatingRowColors(True)
        self.tree_widget.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        layout.addWidget(self.tree_widget)
