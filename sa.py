import sys
import json
import requests
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QComboBox, QLabel, QTableWidget, 
                              QTableWidgetItem, QPushButton, QHeaderView, QTreeWidget,
                              QTreeWidgetItem)
from PySide6.QtCore import Qt
from config import Config

class S2ShowManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("S2 Show Manager")
        self.setMinimumSize(800, 600)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Show selection area
        show_layout = QHBoxLayout()
        show_label = QLabel("Select Show:")
        self.show_combo = QComboBox()
        self.show_combo.currentIndexChanged.connect(self.show_selected)
        show_layout.addWidget(show_label)
        show_layout.addWidget(self.show_combo)
        show_layout.addStretch()
        layout.addLayout(show_layout)
        
        # Details table
        self.details_table = QTableWidget()
        self.details_table.setColumnCount(3)  # Changed to match browser view
        self.details_table.setHorizontalHeaderLabels(["Show Name", "ID", "Status"])
        self.details_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.details_table)
        
        # Add Tasks table
        tasks_label = QLabel("Tasks:")
        layout.addWidget(tasks_label)
        
        # Replace tree widget with better structure
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels([
            "Name", "Type", "ID", "Status", "Due Date", "Assigned To"
        ])
        self.tree_widget.setColumnCount(6)
        self.tree_widget.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        layout.addWidget(self.tree_widget)

        # Store shows data
        self.shows_data = {}
        
        # Load shows
        self.load_shows()

    def get_headers(self):
        return {
            'Authorization': f'Token {Config.s2_tocken}',
            'Content-Type': 'application/json'
        }

    def load_shows(self):
        try:
            response = requests.get(
                f"{Config.S2_API_BASE_URL}/show/?stage=Active",
                headers=self.get_headers()
            )
            if response.status_code == 200:
                all_shows = response.json()
                # Filter and simplify show data (matching browser method)
                shows = [
                    {
                        'show_name': show.get('show_name', ''),
                        'id': show.get('show_id', ''),
                        'status': show.get('status', ''),
                        'stage': show.get('stage', '')
                    }
                    for show in all_shows
                    if show.get('stage') == 'Active'
                ]
                shows = sorted(shows, key=lambda x: x['show_name'])
                
                # Store simplified data
                self.shows_data = {show['id']: show for show in shows}
                
                # Update combo box
                self.show_combo.clear()
                self.show_combo.addItem("Select a show...", None)
                
                for show in shows:
                    show_name = show['show_name']
                    show_id = show['id']
                    self.show_combo.addItem(f"{show_name}", show_id)
                    
        except Exception as e:
            print(f"Error loading shows: {str(e)}")

    def show_selected(self):
        self.tree_widget.clear()
        show_id = self.show_combo.currentData()
        if not show_id:
            self.details_table.setRowCount(0)
            return

        show_data = self.shows_data.get(show_id, {})
        if show_data:
            # Display show details
            self.details_table.setRowCount(1)
            self.details_table.setItem(0, 0, QTableWidgetItem(show_data.get('show_name', '')))
            self.details_table.setItem(0, 1, QTableWidgetItem(str(show_data.get('id', ''))))
            self.details_table.setItem(0, 2, QTableWidgetItem(show_data.get('status', '')))
            
            # Load tasks for the show
            self.load_show_details(show_id)

    def display_show_details(self, show_data):
        # Filter out important fields to display first
        important_fields = ['show_name', 'id', 'status', 'stage', 'client', 'description']
        other_fields = [k for k in show_data.keys() if k not in important_fields]
        all_fields = important_fields + other_fields

        self.details_table.setRowCount(len(all_fields))
        
        for row, field in enumerate(all_fields):
            # Field name
            self.details_table.setItem(row, 0, QTableWidgetItem(field))
            
            # Field value
            value = show_data.get(field, '')
            if isinstance(value, (dict, list)):
                value = json.dumps(value, indent=2)
            self.details_table.setItem(row, 1, QTableWidgetItem(str(value)))
            
            # Status and Stage
            if row == 0:  # Only show status and stage in first row
                self.details_table.setItem(row, 2, QTableWidgetItem(show_data.get('status', '')))
                self.details_table.setItem(row, 3, QTableWidgetItem(show_data.get('stage', '')))

        self.details_table.resizeRowsToContents()

    def process_task_data(self, task):
        """Process and validate task data before display"""
        return {
            'task_label': task.get('task_label', 'N/A'),
            'task_id': task.get('id', 'N/A'),
            'status': task.get('status', 'N/A'),
            'nickname': task.get('nickname', 'N/A'),
            'due_date': task.get('date_bot_due', 'N/A')
        }

    def organize_data_hierarchy(self, data):
        """Organize data into show -> sequence -> shot -> task hierarchy"""
        sequences = {}
        
        for item in data:
            seq_name = item.get('sequence_name') or item.get('group_name', 'No Sequence')
            shot_name = item.get('object_name', 'Unknown Shot')
            shot_id = item.get('object_id', 'N/A')
            
            # Initialize sequence if not exists
            if seq_name not in sequences:
                sequences[seq_name] = {
                    'shots': {},
                    'seq_id': item.get('sequence_id') or item.get('group_id', 'N/A')
                }
            
            # Initialize shot if not exists
            if shot_id not in sequences[seq_name]['shots']:
                sequences[seq_name]['shots'][shot_id] = {
                    'name': shot_name,
                    'id': shot_id,
                    'status': item.get('status', 'N/A'),
                    'tasks': []
                }
            
            # Add tasks
            if 'tasks' in item:
                sequences[seq_name]['shots'][shot_id]['tasks'].extend(item['tasks'])
        
        return sequences

    def display_tasks(self, tasks_data):
        self.tree_widget.clear()
        
        if not isinstance(tasks_data, list):
            return

        # Get show data
        show_id = self.show_combo.currentData()
        show_data = self.shows_data.get(show_id, {})
        
        # Create show root item
        show_item = QTreeWidgetItem(self.tree_widget)
        show_item.setText(0, show_data.get('show_name', 'Unknown Show'))
        show_item.setText(1, "Show")
        show_item.setText(2, str(show_id))
        show_item.setText(3, show_data.get('status', 'N/A'))
        show_item.setExpanded(True)

        # Organize data hierarchically
        hierarchy = self.organize_data_hierarchy(tasks_data)

        # Create sequence items
        for seq_name, seq_data in hierarchy.items():
            seq_item = QTreeWidgetItem(show_item)
            seq_item.setText(0, seq_name)
            seq_item.setText(1, "Sequence")
            seq_item.setText(2, str(seq_data['seq_id']))
            seq_item.setExpanded(True)

            # Create shot items
            for shot_id, shot_data in seq_data['shots'].items():
                shot_item = QTreeWidgetItem(seq_item)
                shot_item.setText(0, shot_data['name'])
                shot_item.setText(1, "Shot")
                shot_item.setText(2, str(shot_id))
                shot_item.setText(3, shot_data['status'])
                shot_item.setExpanded(True)

                # Create task items
                for task in shot_data['tasks']:
                    task_item = QTreeWidgetItem(shot_item)
                    task_item.setText(0, task.get('task_label', 'N/A'))
                    task_item.setText(1, "Task")
                    task_item.setText(2, str(task.get('task_id', 'N/A')))
                    task_item.setText(3, task.get('task_status', 'N/A'))
                    task_item.setText(4, task.get('date_bot_due', 'N/A'))
                    task_item.setText(5, task.get('nickname', 'N/A'))

        # Resize columns to content
        for i in range(self.tree_widget.columnCount()):
            self.tree_widget.resizeColumnToContents(i)

    def load_show_details(self, show_id):
        try:
            response = requests.get(
                f"{Config.S2_API_BASE_URL}/object_tree/?show_id={show_id}",
                headers=self.get_headers()
            )
            if response.status_code == 200:
                tasks = response.json()
                # Validate response format
                if not isinstance(tasks, list):
                    print("Error: Invalid response format")
                    return
                    
                print(f"\n=== GUI: Processing {len(tasks)} tasks for show {show_id} ===")
                for task in tasks:
                    print("------",task)
                    # print("---task-",task['service_type_label'])
                    # print("---task_id-",task['task_id'])
                    # print("---task_status-",task['task_status'])
                    print(f"Processing task: {task.get('name', 'N/A')} - {task.get('id', 'N/A')}")
                
                self.display_tasks(tasks)
            else:
                print(f"Error: API returned status code {response.status_code}")
        except Exception as e:
            print(f"Error loading show details: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = S2ShowManager()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
