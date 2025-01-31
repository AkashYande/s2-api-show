import sys
import json
import requests
from PySide6.QtWidgets import QApplication, QTreeWidgetItem
from config.config import Config
from ui.s2_ui import S2UI

class S2ShowManager(S2UI):
    def __init__(self):
        super().__init__()
        
        # Connect signals
        self.show_combo.currentIndexChanged.connect(self.show_selected)
        self.status_combo.currentTextChanged.connect(self.filter_by_status)
        
        # Initialize data
        self.shows_data = {}
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
            return

        show_data = self.shows_data.get(show_id, {})
        if show_data:
            # Load tasks for the show
            self.load_show_details(show_id)

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
        """Organize data into show -> sequence -> shot -> service -> task hierarchy"""
        sequences = {}
        
        for item in data:
            seq_name = item.get('group_name', 'No Sequence')
            shot_name = item.get('object_name', 'Unknown Shot')
            shot_id = item.get('object_id', 'N/A')
            services = item.get('services', [])
            
            # Initialize sequence if not exists
            if seq_name not in sequences:
                sequences[seq_name] = {
                    'shots': {},
                    'seq_id': item.get('group_id', 'N/A')
                }
            
            # Initialize shot if not exists
            if shot_id not in sequences[seq_name]['shots']:
                sequences[seq_name]['shots'][shot_id] = {
                    'name': shot_name,
                    'id': shot_id,
                    'services': []
                }
            
            # Add services and their tasks
            for service in services:
                service_data = {
                    'name': service.get('service_type_label', 'N/A'),
                    'id': service.get('service_id', 'N/A'),
                    'status': service.get('status_label', 'N/A'),
                    'due_date': service.get('date_bot_due', 'N/A'),
                    'tasks': service.get('tasks', [])
                }
                sequences[seq_name]['shots'][shot_id]['services'].append(service_data)
        
        return sequences

    def get_available_statuses(self, tasks_data):
        """Extract unique task statuses from the data"""
        statuses = set(["All"])
        
        def extract_status(items):
            for item in items:
                services = item.get('services', [])
                for service in services:
                    # Add service status
                    if service.get('status_label'):
                        statuses.add(service.get('status_label'))
                    # Add task statuses
                    for task in service.get('tasks', []):
                        if task.get('task_status'):
                            statuses.add(task.get('task_status'))

        extract_status(tasks_data)
        
        return sorted(list(statuses))

    def update_status_filter(self, tasks_data):
        """Update status filter dropdown with available statuses"""
        current_status = self.status_combo.currentText()
        self.status_combo.clear()
        
        available_statuses = self.get_available_statuses(tasks_data)
        self.status_combo.addItems(available_statuses)
        
        # Restore previous selection if available, otherwise select "All"
        index = self.status_combo.findText(current_status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)
        else:
            self.status_combo.setCurrentText("All")

    def display_tasks(self, tasks_data):
        # Update status filter before displaying tasks
        self.update_status_filter(tasks_data)
        
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
        show_item.setExpanded(True)

        # Organize and display data hierarchically
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
                shot_item.setExpanded(True)

                # Create service items
                for service in shot_data['services']:
                    service_item = QTreeWidgetItem(shot_item)
                    service_item.setText(0, service['name'])
                    service_item.setText(1, "Service")
                    service_item.setText(2, str(service['id']))
                    service_item.setText(3, service['status'])
                    service_item.setText(4, service['due_date'])
                    service_item.setExpanded(True)

                    # Create task items
                    for task in service['tasks']:
                        task_item = QTreeWidgetItem(service_item)
                        task_item.setText(0, task.get('task_label', 'N/A'))
                        task_item.setText(1, "Task")
                        task_item.setText(2, str(task.get('task_id', 'N/A')))
                        task_item.setText(3, task.get('task_status', 'N/A'))
                        task_item.setText(4, task.get('date_bot_due', 'N/A'))
                        task_item.setText(5, task.get('nickname', 'N/A'))

        # Resize columns to content
        for i in range(self.tree_widget.columnCount()):
            self.tree_widget.resizeColumnToContents(i)

        # After creating all items, apply current filter
        current_filter = self.status_combo.currentText()
        if current_filter != "All":
            self.filter_by_status(current_filter)

    def load_show_details(self, show_id):
        try:
            response = requests.get(
                f"{Config.S2_API_BASE_URL}/object_tree/?show_id={show_id}",
                headers=self.get_headers()
            )
            if response.status_code == 200:
                tasks = response.json()
                if not isinstance(tasks, list):
                    print("Error: Invalid response format")
                    return
                
                self.display_tasks(tasks)
            else:
                print(f"Error: API returned status code {response.status_code}")
        except Exception as e:
            print(f"Error loading show details: {str(e)}")

    def filter_by_status(self, status):
        """Filter tree items based on selected status"""
        # Store the current show ID before filtering
        show_id = self.show_combo.currentData()
        if not show_id:
            return

        # Hide/show items based on status
        root = self.tree_widget.invisibleRootItem()
        self.filter_tree_items(root, status)

    def filter_tree_items(self, parent, status):
        """Recursively filter tree items"""
        show_item = False
        for i in range(parent.childCount()):
            child = parent.child(i)
            if child.text(1) == "Task":  # Only filter task items
                if status == "All" or child.text(3) == status:
                    child.setHidden(False)
                    show_item = True
                else:
                    child.setHidden(True)
            else:
                # Recursively filter child items
                show_child = self.filter_tree_items(child, status)
                child.setHidden(not show_child)
                show_item = show_item or show_child

        return show_item

def main():
    app = QApplication(sys.argv)
    window = S2ShowManager()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()