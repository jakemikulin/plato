import Cocoa

class MainFlutterWindow: NSWindow {
    override func awakeFromNib() {
        super.awakeFromNib()

        let appBundle = Bundle.main
        let backendPath = appBundle.resourcePath! + "/backend/main.py"
        let pythonPath = appBundle.resourcePath! + "/backend/.venv/bin/python3"

        DispatchQueue.global(qos: .background).async {
            let task = Process()
            task.launchPath = pythonPath  // Ensure the correct Python from .venv is used
            task.arguments = [backendPath]

            let pipe = Pipe()
            task.standardOutput = pipe
            task.standardError = pipe

            let fileHandle = pipe.fileHandleForReading
            fileHandle.readabilityHandler = { file in
                if let output = String(data: file.availableData, encoding: .utf8) {
                    print("🔹 Backend Output: \(output)")
                }
            }

            do {
                try task.run()
                print("✅ FastAPI backend started successfully!")
            } catch {
                print("❌ Error starting backend: \(error)")
            }
        }
    }
}
