# Syshtum: SYStem Heuristic Task Undertaking through Prompt Management

Syshtum is a system designed to act as an **Operating System (OS) Controlling Agent**, leveraging AI models and heuristic task management techniques. The project integrates **OmniParser**, a vision-based GUI parsing tool, to enable seamless interaction with graphical user interfaces (GUIs) and execute tasks autonomously. Syshtum is capable of interpreting user prompts, generating actionable plans, and performing operations such as mouse clicks, keyboard inputs, and file management, making it a versatile tool for automating complex workflows.

---

## How to Use

1. **Clone the Repository**:  
   Ensure you have the project files on your local machine.

2. **Navigate to the Project Directory**:  
   Open a terminal and run:
   ```bash
   cd Syshtum
   ```

3. Create a Virtual Environment:
    Set up a Python virtual environment to manage dependencies:
    ```
    python3 -m venv venv
    ```
    
4. Activate the Virtual Environment:

    On macOS/Linux:
    ```
    source venv/bin/activate
    ```
    On Windows:
    ```
    venv\Scripts\activate
    ```

5. Install Dependencies:
    Install the required Python packages:
    ```
    pip install -r requirements.txt
    ```

6. Run the Application:
    Start the PyQt-based GUI application:
    ```
    python3 main_ui.py
    ```

---

## Key Features

1. **OmniParser Integration**:  
   Syshtum utilizes **OmniParser**, a screen parsing tool, to analyze GUI screenshots and extract structured data. This data is used to ground AI-generated actions in specific regions of the interface, enabling precise and context-aware task execution. OmniParser supports multiple models, which can be orchestrated for enhanced performance.

2. **OS Control Capabilities**:  
   The system can perform a variety of OS-level operations, such as:
   - Simulating keyboard inputs and mouse clicks.
   - Navigating GUIs based on parsed screen data.
   - Automating repetitive tasks with minimal user intervention.

3. **Modular Design**:  
   The project is organized into modular components, making it easy to extend and customize. Key modules include `operate`, which handles OS-level operations, and `OmniParser`, which focuses on GUI parsing.

---