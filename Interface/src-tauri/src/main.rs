use std::process::{Command, Stdio};
use std::path::PathBuf;
use std::thread;

fn main() {
    let backend_dir = PathBuf::from("/Users/neerajkumar/vs_code/SWE/se_project/operate");
    let venv_path = backend_dir.join("venv");
    
    // Create virtual environment using uv or venv code here...
    
    // Path to python in the virtual environment
    let python_path = if cfg!(target_os = "windows") {
        venv_path.join("Scripts").join("python")
    } else {
        venv_path.join("bin").join("python")
    };
    
    println!("Starting backend with virtual environment Python...");
    
    // Run Python from the virtual environment in a separate thread
    let backend_thread = thread::spawn(move || {
        let backend_process = Command::new(python_path)
            .arg(backend_dir.join("main_server.py"))
            .current_dir(&backend_dir)
            .stdout(Stdio::inherit())
            .stderr(Stdio::inherit())
            .spawn();
        
        match backend_process {
            Ok(mut process) => {
                println!("Backend started successfully.");
                // Wait for the process to finish
                let _ = process.wait();
            },
            Err(e) => println!("Failed to start backend: {:?}", e),
        }
    });
    
    // Add a small delay to ensure the backend has time to start
    thread::sleep(std::time::Duration::from_secs(2));
    
    // Start the Tauri application
    tauri::Builder::default()
        .setup(|_app| Ok(()))
        .run(tauri::generate_context!())
        .expect("error while running Tauri application");
    
    // Wait for the backend thread to finish
    let _ = backend_thread.join();
}