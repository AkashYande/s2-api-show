# S2 Show Manager

A Python-based GUI application for managing and viewing S2 show data. This application provides a hierarchical view of shows, sequences, shots, services, and tasks from the S2 API.

## Features

- Show selection from active projects
- Hierarchical tree view display of:
  - Shows
  - Sequences
  - Shots
  - Services
  - Tasks
- Status-based filtering
- Real-time data updates
- Due date tracking
- Task assignment viewing

## Prerequisites

- Python 3.7+
- PySide6
- Requests
- python-dotenv

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd s2-api-show
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/MacOS
# or
.venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure the environment:
- Create a `.env` file in the project root
- Add your S2 API token:
```
S2_API_TOKEN=your_token_here
```

## Usage

1. Start the application:
```bash
python s2_app_gui.py
```

2. Select a show from the dropdown menu
3. Use the status filter to filter tasks by their current status
4. Navigate the tree view to explore show details

## Project Structure

```
s2-api-show/
├── s2_app_gui.py    # Main application file
├── config.py        # Configuration settings
├── requirements.txt # Project dependencies
└── .env            # Environment variables (create this)
```

## Configuration

The application uses a configuration file (`config.py`) for API settings. Make sure to:
1. Set the correct API base URL
2. Configure your API token
3. Set any additional environment variables in `.env`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
