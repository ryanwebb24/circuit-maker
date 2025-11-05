# Circuit Maker

Circuit Maker is an interactive circuit design and simulation tool built with Python and Pygame. It provides a user-friendly interface for creating and experimenting with electrical circuits.

## Features

-   **Interactive Grid System**: Easy-to-use grid-based circuit design interface
-   **Component Library**:
    -   Resistors with customizable values
    -   Wires for connecting components
    -   More components coming soon!
-   **Tool Selection**:
    -   Wire tool for creating connections
    -   Resistor tool for placing resistors
    -   Click-to-place interface
-   **Visual Feedback**:
    -   Clear component visualization
    -   Grid-based alignment
    -   Highlighted selection

## Getting Started

### Prerequisites

-   Python 3.x
-   Pygame

### Installation

1. Clone the repository:

```bash
git clone https://github.com/ryanwebb24/circuit-maker.git
cd circuit-maker
```

2. Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

### Running the Application

Run the main script:

```bash
python main.py
```

## How to Use

1. **Starting the Application**:

    - Launch the program using the command above
    - You'll see a grid interface with a toolbar

2. **Using Tools**:

    - Click the "Wire" button to place wires
    - Click the "Resistor" button to place resistors
    - Click on the grid to place components

3. **Component Manipulation**:
    - Click on existing components to remove them
    - More features coming soon!

## Project Structure

```
circuit-maker/
├── components/         # Component classes and logic
│   ├── resistor.py    # Resistor component
│   ├── wire.py        # Wire component
│   └── base_component.py
├── core/              # Core circuit logic
│   └── circuit.py     # Circuit management
├── ui/                # User interface elements
│   ├── renderer.py    # Main rendering system
│   └── button.py      # UI components
└── main.py           # Application entry point
```

## Future Plans

See the [TODO.md](TODO.md) file for planned features and improvements.

## Author

Ryan Webb - [GitHub Profile](https://github.com/ryanwebb24)
