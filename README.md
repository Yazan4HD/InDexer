In Dexer 1.0.0
In Dexer is a powerful and lightweight desktop application for Windows that allows you to index multiple folders and instantly search through all your files and directories. It creates a local database of your file metadata, providing lightning-fast search results without constantly scanning your hard drive.

About The Project
This tool was built to solve the problem of managing files scattered across many different folders and drives. Instead of manually searching through each directory, In Dexer consolidates all your important locations into a single, searchable interface. It's perfect for users who need to quickly find files based on name or location without the overhead of a heavy system-wide search tool.

Built With
Python

PyQt6 for the user interface

SQLite for the database

Features
Index Multiple Folders: Add as many folders as you want to the index.

Hierarchical Tree View: Browse your indexed folders and their subdirectories in a familiar tree structure.

Detailed File Information: View file names, sizes, full directory paths, and creation/modification dates.

Instant Search: A powerful search bar to find what you're looking for.

Toggle between searching for Files or Folders.

Search by file name or by path.

Reveal in Tree: Click any search result to instantly locate and highlight its parent folder in the tree view.

Open Files & Folders: Double-click any file or folder in the app to open it directly with your default system application.

Persistent Database: Your index is saved locally, so it loads instantly every time you open the app.

Refresh Index: Use the "Refresh All" button or the automatic startup scan to keep your index up-to-date with any changes.

Easy Management: Add new folders or remove existing ones from the index with a single click.

Getting Started
To get a local copy up and running for development, follow these simple steps.

Prerequisites
You will need Python 3 installed on your system.

Python 3

Installation
Clone the repository

git clone [https://github.com/your_username/in-dexer.git](https://github.com/your_username/in-dexer.git)

Navigate to the project directory

cd in-dexer

Install the required packages

pip install PyQt6

Usage
To run the application from the source code, simply execute the main.py script:

python main.py

Creating a Standalone Executable
You can package the application into a single .exe file for Windows that can be run on any computer, even without Python installed.

Install PyInstaller

pip install pyinstaller

Create an Icon (Optional)

Create an icon.ico file and place it in the root project directory.

Run the Build Command

pyinstaller --name "In Dexer" --onefile --windowed --icon="icon.ico" main.py

The final In Dexer.exe will be located in the dist folder.

License
Distributed under the MIT License. See LICENSE for more information.

Contact
Yazan Shaban - dublajat@gmail.com

Project Link: https://github.com/Yazan4HD/in-dexer
