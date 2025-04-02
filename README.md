# Syshtum
**SYStem Heuristic Task Undertaking through Prompt Management**

Syshtum is a project designed to streamline task management through heuristic systems and prompt-based workflows. This repository contains both a web application and a Tauri-based desktop application for managing tasks efficiently.

---

## Branch Information
The current codebase resides in the **staging branch**. Ensure you are on the correct branch before making changes or running the application.

---

## Prerequisites
Before running the application, ensure you have the following installed:
- **Node.js** (v16 or later)
- **npm** (Node Package Manager)
- **Tauri prerequisites** (Rust, Cargo, etc., for building the desktop app)

---

## Running the Application

### Web Application
The web application is built using modern JavaScript frameworks. Follow these steps to run it locally:

1. **Navigate to the project folder:**
    ```bash
    cd Interface
    ```

2. **Install dependencies:**
    ```bash
    npm install
    ```

3. **Start the development server:**
    ```bash
    npm run dev
    ```
    This will start the web application on a local development server. Open your browser and navigate to the URL provided in the terminal (usually `http://localhost:3000`).

---

### Tauri Desktop Application
The desktop application is built using Tauri, which combines web technologies with Rust for a lightweight and secure desktop experience.

1. **Navigate to the project folder:**
    ```bash
    cd Interface
    ```

2. **Start the Tauri development environment:**
    ```bash
    npm run tauri dev
    ```
    This will launch the desktop application in development mode.

---

### Building the Desktop Application
To create a production-ready build of the desktop application:

1. **Navigate to the project folder:**
    ```bash
    cd Interface
    ```

2. **Build the Tauri application:**
    ```bash
    npm run tauri build
    ```
    The built application will be available in the `src-tauri/target/release` directory.

---

## Project Structure
- **Interface/**: Contains the source code for both the web and desktop applications.
- **src-tauri/**: Contains Tauri-specific configuration and Rust code for the desktop application.

---

## Contributing
1. Clone the repository:
    ```bash
    git clone https://github.com/your-repo/syshtum.git
    ```
2. Switch to the staging branch:
    ```bash
    git checkout staging
    ```
3. Make your changes and submit a pull request.

---

## License
This project is licensed under the MIT License. See the `LICENSE` file for more details.

---

## Support
For any issues or questions, please open an issue in the repository or contact the maintainers.

