use std::env;
use std::process::{Command, Stdio};

fn main() {
    let project_root = env::current_dir().unwrap();  // Get current directory
    let backend_path = project_root.join("../operate/main.py");  // Construct absolute path

    let mut backend_process = Command::new("python3")
        .arg(backend_path)  // Use dynamically resolved path
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .expect("Failed to start Python backend");

    tauri::Builder::default()
        .setup(|_app| Ok(()))
        .run(tauri::generate_context!())
        .expect("error while running tauri application");

    let _ = backend_process.kill();
}
