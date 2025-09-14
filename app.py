# main.py

import sys
import os
import sqlite3
import datetime
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTreeView, QTableView, QSplitter, QStatusBar, 
    QFileDialog, QMessageBox, QLineEdit, QCheckBox
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt

# Import our database initializer
import database

# --- HELPER FUNCTIONS ---
def format_size(size_bytes):
    """Converts bytes to a human-readable format (KB, MB, GB)."""
    if size_bytes is None: return "0 B"
    if size_bytes == 0: return "0 B"
    power = 1024
    n = 0
    power_labels = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size_bytes >= power and n < len(power_labels) - 1:
        size_bytes /= power
        n += 1
    return f"{size_bytes:.2f} {power_labels[n]}"

def normalize_path(path):
    """Consistently normalizes a path for the current OS."""
    return os.path.normcase(os.path.normpath(path))


class MainWindow(QMainWindow):
    """The main class for the File Indexer application."""
    def __init__(self):
        super().__init__()
        
        # --- 1. Window Setup ---
        self.setWindowTitle("In Dexer 1.0.0 | Developed by Yazan Shaban")
        self.setGeometry(100, 100, 1400, 800)
        
        self.path_to_item_map = {}

        # --- 2. Create UI Elements ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        top_bar_layout = QHBoxLayout()

        self.add_folder_button = QPushButton("Add Folder")
        self.remove_folder_button = QPushButton("Remove Selected Folder")
        self.refresh_button = QPushButton("Refresh All")
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search all indexed files...")
        
        # --- NEW: Add the checkbox for folder search ---
        self.search_folders_checkbox = QCheckBox("Search Folders")

        self.folder_tree_view = QTreeView()
        self.tree_model = QStandardItemModel()
        self.folder_tree_view.setModel(self.tree_model)
        self.file_details_table = QTableView()
        self.table_model = QStandardItemModel()
        self.file_details_table.setModel(self.table_model)
        self.file_details_table.setSortingEnabled(True)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Developed by Yazan Shaban | dublajat@gmail.com")

        # --- 3. Arrange Layouts ---
        top_bar_layout.addWidget(self.add_folder_button)
        top_bar_layout.addWidget(self.remove_folder_button)
        top_bar_layout.addStretch(1)
        top_bar_layout.addWidget(self.search_field, 2)
        top_bar_layout.addWidget(self.search_folders_checkbox) # Add checkbox to layout
        top_bar_layout.addWidget(self.refresh_button)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.folder_tree_view)
        splitter.addWidget(self.file_details_table)
        splitter.setSizes([500, 900])
        main_layout.addLayout(top_bar_layout)
        main_layout.addWidget(splitter)

        # --- 4. Connect Signals to Functions ---
        self.add_folder_button.clicked.connect(self.add_folder_to_index)
        self.remove_folder_button.clicked.connect(self.remove_selected_folder)
        self.refresh_button.clicked.connect(self.refresh_all_indexes)
        self.search_field.textChanged.connect(self.search)
        self.search_folders_checkbox.stateChanged.connect(self.on_search_mode_changed)
        self.folder_tree_view.clicked.connect(self.on_folder_selected_in_tree)
        self.folder_tree_view.doubleClicked.connect(self.open_folder_in_explorer)
        self.file_details_table.doubleClicked.connect(self.on_table_double_clicked)
        self.file_details_table.selectionModel().selectionChanged.connect(self.on_search_result_selected)

        # --- 5. Initial Load ---
        self.refresh_all_indexes()

    # --- Core Logic Methods ---

    def _perform_index_for_path(self, folder_path):
        # ... (This function remains unchanged)
        files_to_add = []
        try:
            conn = sqlite3.connect(database.DB_FILE)
            cursor = conn.cursor()
            folder_path_norm = normalize_path(folder_path)

            cursor.execute("INSERT OR IGNORE INTO indexed_folders (path) VALUES (?)", (folder_path_norm,))
            cursor.execute("SELECT id FROM indexed_folders WHERE path = ?", (folder_path_norm,))
            folder_id = cursor.fetchone()[0]
            
            cursor.execute("DELETE FROM files WHERE folder_id = ?", (folder_id,))

            for dirpath, _, filenames in os.walk(folder_path_norm):
                for filename in filenames:
                    full_path = os.path.join(dirpath, filename)
                    try:
                        stat = os.stat(full_path)
                        files_to_add.append((
                            folder_id, filename, normalize_path(dirpath), stat.st_size,
                            datetime.datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                            datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                        ))
                    except (FileNotFoundError, PermissionError):
                        continue
            
            if files_to_add:
                cursor.executemany("INSERT INTO files VALUES (NULL, ?, ?, ?, ?, ?, ?)", files_to_add)
            
            conn.commit()
            conn.close()
            return len(files_to_add)
        except Exception as e:
            print(f"Error indexing {folder_path}: {e}")
            return 0

    def refresh_all_indexes(self):
        # ... (This function remains unchanged)
        self.status_bar.showMessage("Refreshing all indexed folders...")
        QApplication.processEvents()
        
        conn = sqlite3.connect(database.DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT path FROM indexed_folders")
        all_root_paths = [row[0] for row in cursor.fetchall()]
        conn.close()

        total_files = sum(self._perform_index_for_path(path) for path in all_root_paths)
        
        self.load_and_display_indexed_folders()
        self.status_bar.showMessage(f"Refresh complete. {total_files} files indexed.", 10000)

    def load_and_display_indexed_folders(self):
        # ... (This function remains unchanged)
        self.tree_model.clear()
        self.tree_model.setHorizontalHeaderLabels(['Indexed Folders'])
        self.path_to_item_map.clear()
        
        conn = sqlite3.connect(database.DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT directory FROM files")
        file_dirs = {normalize_path(row[0]) for row in cursor.fetchall()}
        cursor.execute("SELECT path FROM indexed_folders")
        root_paths = {normalize_path(row[0]) for row in cursor.fetchall()}
        all_paths = sorted(list(file_dirs.union(root_paths)))
        conn.close()

        root_item = self.tree_model.invisibleRootItem()
        self.path_to_item_map[''] = root_item

        for path in all_paths:
            parts = path.split(os.sep)
            current_parent_item = root_item
            path_so_far = ""

            for part in parts:
                if path_so_far == "" and part.endswith(':'): 
                    path_so_far = part + os.sep
                else:
                    path_so_far = os.path.join(path_so_far, part)
                
                if path_so_far in self.path_to_item_map:
                    current_parent_item = self.path_to_item_map[path_so_far]
                else:
                    new_item = QStandardItem(part)
                    new_item.setData(path_so_far, Qt.ItemDataRole.UserRole)
                    new_item.setEditable(False)
                    current_parent_item.appendRow(new_item)
                    self.path_to_item_map[path_so_far] = new_item
                    current_parent_item = new_item
        
        self.folder_tree_view.expandToDepth(0)

    # --- UI Interaction Methods ---

    def add_folder_to_index(self):
        # ... (This function remains unchanged)
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder to Index")
        if folder_path:
            self.status_bar.showMessage(f"Indexing {folder_path}...")
            QApplication.processEvents()
            files_indexed = self._perform_index_for_path(folder_path)
            self.status_bar.showMessage(f"Successfully indexed {files_indexed} files.", 5000)
            self.load_and_display_indexed_folders()

    def remove_selected_folder(self):
        # ... (This function remains unchanged)
        selected_indexes = self.folder_tree_view.selectedIndexes()
        if not selected_indexes:
            QMessageBox.warning(self, "No Selection", "Please select a top-level folder to remove.")
            return

        item = self.tree_model.itemFromIndex(selected_indexes[0])
        if item.parent() is not self.tree_model.invisibleRootItem():
             QMessageBox.warning(self, "Invalid Selection", "You can only remove a top-level folder.")
             return
             
        path_to_remove = item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(self, 'Confirm Removal', f"Are you sure you want to remove '{os.path.basename(path_to_remove)}' from the index?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            conn = sqlite3.connect(database.DB_FILE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM indexed_folders WHERE path = ?", (path_to_remove,))
            conn.commit()
            conn.close()
            self.refresh_all_indexes()

    # --- MODIFIED: The main search function now handles both modes ---
    def search(self):
        search_term = self.search_field.text()
        self.table_model.clear()
        
        if not search_term:
            return

        if self.search_folders_checkbox.isChecked():
            # --- FOLDER SEARCH LOGIC ---
            self.table_model.setHorizontalHeaderLabels(['Folder Name', 'Full Path'])
            conn = sqlite3.connect(database.DB_FILE)
            cursor = conn.cursor()
            pattern = f'%{search_term}%'
            cursor.execute("SELECT DISTINCT directory FROM files WHERE directory LIKE ?", (pattern,))
            results = cursor.fetchall()
            conn.close()
            
            for (path,) in results:
                folder_name_item = QStandardItem(os.path.basename(path) or path)
                full_path_item = QStandardItem(path)
                folder_name_item.setEditable(False)
                full_path_item.setEditable(False)
                self.table_model.appendRow([folder_name_item, full_path_item])
        else:
            # --- FILE SEARCH LOGIC (Existing) ---
            self.table_model.setHorizontalHeaderLabels(['Name', 'Size', 'Directory', 'Date Modified', 'Date Created'])
            conn = sqlite3.connect(database.DB_FILE)
            cursor = conn.cursor()
            pattern = f'%{search_term}%'
            cursor.execute("SELECT * FROM files WHERE name LIKE ? OR directory LIKE ?", (pattern, pattern))
            results = cursor.fetchall()
            conn.close()
            
            for file_data in results:
                self._add_file_to_table(file_data[2:])
        
        self.file_details_table.resizeColumnsToContents()

    def on_folder_selected_in_tree(self, index):
        # ... (This is the original on_folder_selected function)
        self.search_field.clear()
        item = self.tree_model.itemFromIndex(index)
        if not item: return
        selected_path = item.data(Qt.ItemDataRole.UserRole)
        
        self.table_model.clear()
        self.table_model.setHorizontalHeaderLabels(['Name', 'Size', 'Directory', 'Date Modified', 'Date Created'])
        
        conn = sqlite3.connect(database.DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM files WHERE directory = ?", (selected_path,))
        files = cursor.fetchall()
        conn.close()
        
        for file_data in files:
            self._add_file_to_table(file_data[2:])
        self.file_details_table.resizeColumnsToContents()

    def on_search_result_selected(self, selected, deselected):
        # --- MODIFIED: Handles selection for both file and folder search results ---
        if not self.search_field.text() or not selected.indexes():
            return
        
        selected_row = selected.indexes()[0].row()
        path_to_reveal = ""

        if self.search_folders_checkbox.isChecked():
            # In folder mode, the path is in the second column (index 1)
            path_item = self.table_model.item(selected_row, 1)
            if path_item:
                path_to_reveal = normalize_path(path_item.text())
        else:
            # In file mode, the directory is in the third column (index 2)
            directory_item = self.table_model.item(selected_row, 2)
            if directory_item:
                path_to_reveal = normalize_path(directory_item.text())

        if path_to_reveal and path_to_reveal in self.path_to_item_map:
            target_item = self.path_to_item_map[path_to_reveal]
            self.folder_tree_view.expand(target_item.index())
            self.folder_tree_view.setCurrentIndex(target_item.index())
            self.folder_tree_view.scrollTo(target_item.index())

    def open_folder_in_explorer(self, index):
        # ... (This function remains unchanged)
        path = self.tree_model.itemFromIndex(index).data(Qt.ItemDataRole.UserRole)
        self.open_path(path)

    def on_table_double_clicked(self, index):
        # --- MODIFIED: Handles double-clicks for both file and folder results ---
        row = index.row()
        path_to_open = ""

        if self.search_folders_checkbox.isChecked():
            # In folder mode, the path is in the second column (index 1)
            path_item = self.table_model.item(row, 1)
            if path_item:
                path_to_open = path_item.text()
        else:
            # In file mode, we construct the path from name and directory
            filename_item = self.table_model.item(row, 0)
            directory_item = self.table_model.item(row, 2)
            if filename_item and directory_item:
                path_to_open = os.path.join(directory_item.text(), filename_item.text())
        
        if path_to_open:
            self.open_path(path_to_open)

    # --- NEW: Helper function to manage search mode changes ---
    def on_search_mode_changed(self):
        if self.search_folders_checkbox.isChecked():
            self.search_field.setPlaceholderText("Search all indexed folders...")
        else:
            self.search_field.setPlaceholderText("Search all indexed files...")
        # Re-run the search with the new mode
        self.search()

    # --- Helper Methods ---

    def _add_file_to_table(self, file_data):
        # ... (This function remains unchanged)
        name, directory, size_bytes, creation_date, mod_date = file_data
        name_item = QStandardItem(name)
        size_item = QStandardItem(format_size(size_bytes))
        dir_item = QStandardItem(directory)
        mod_date_item = QStandardItem(mod_date)
        cre_date_item = QStandardItem(creation_date)
        
        for item in [name_item, size_item, dir_item, mod_date_item, cre_date_item]:
            item.setEditable(False)
            
        self.table_model.appendRow([name_item, size_item, dir_item, mod_date_item, cre_date_item])

    def open_path(self, path):
        # ... (This function remains unchanged)
        try:
            if sys.platform == "win32":
                os.startfile(os.path.normpath(path))
            elif sys.platform == "darwin": # macOS
                subprocess.Popen(["open", path])
            else: # Linux
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            print(f"Error opening path {path}: {e}")

# --- Application Entry Point ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

