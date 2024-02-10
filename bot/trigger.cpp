#include <cstdlib>
#include <sys/wait.h>
#include <unistd.h>
#include <iostream>
#include <fstream>
#include <string>
#include <chrono>
#include <thread>
using namespace std;

bool monitorLogFile(const std::string& filename) {
    // Open the log file
    std::ifstream file(filename);
    bool alert = false;
    // Check if the file is opened successfully
    if (!file.is_open()) {
        std::cerr << "Error: Unable to open file " << filename << std::endl;
        return false; // Return false indicating failure
    }

    // Store the current position in the file
    file.seekg(0, std::ios::end);
    std::streampos lastPos = file.tellg();

    while (true) {
        // Sleep for a short duration
        std::this_thread::sleep_for(std::chrono::seconds(1));

        // Check if the file has been modified
        file.seekg(0, std::ios::end);
        std::streampos currentPos = file.tellg();

        if (currentPos != lastPos) {
            // Read the new content from the file
            alert = true;
            file.seekg(lastPos);
            std::string newContent;
            std::getline(file, newContent);

            // Output the new content
            std::cout << "New content in file: " << newContent << std::endl;

            // Update the last position
            lastPos = currentPos;
        }
    }
    return alert;
}

int main() {
    // Execute tmux session creation and Python command within it

    string filename = "actions.log"; // Double quotes for string literals
    bool alert = monitorLogFile(filename); // Declare and initialize alert variable
    if (alert) {
        std::system("tmux new-session -d -s my_session 'python3 main.py'");

        // Wait for the tmux session process to terminate
        pid_t pid = fork();
        if (pid == 0) {
            // Child process
            execlp("tmux", "tmux", "wait-session", "-t", "my_session", NULL);
        } else if (pid > 0) {
            // Parent process
            waitpid(pid, NULL, 0);
        } else {
            // Error
            std::cerr << "Failed to fork." << std::endl;
            return 1;
        }
    }

    return 0;
}
