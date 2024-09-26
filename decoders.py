import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

def get_project_structure(start_path, exclude_dirs=None):
    project_structure = []
    for root, dirs, files in os.walk(start_path):
        # Exclude specified directories
        if exclude_dirs:
            dirs[:] = [d for d in dirs if os.path.abspath(os.path.join(root, d)) not in exclude_dirs]

        level = root.replace(start_path, '').count(os.sep)
        indent = ' ' * 4 * level
        project_structure.append(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            project_structure.append(f'{subindent}{f}')
    return '\n'.join(project_structure)

def write_project_to_file(start_path, output_file):
    output_dir = os.path.dirname(os.path.abspath(output_file))
    exclude_dirs = {os.path.abspath(output_dir)}

    with open(output_file, 'w', encoding='utf-8') as f:
        # Write file structure
        f.write("Project File Structure:\n")
        f.write(get_project_structure(start_path, exclude_dirs))
        f.write("\n\n")

        # Write contents of each file
        for root, dirs, files in os.walk(start_path):
            # Exclude specified directories
            if exclude_dirs and os.path.abspath(root) in exclude_dirs:
                continue

            for file in files:
                file_path = os.path.join(root, file)
                f.write(f"File: {file_path}\n")
                f.write("=" * 80 + "\n")
                try:
                    with open(file_path, 'r', encoding='utf-8') as file_content:
                        f.write(file_content.read())
                except Exception as e:
                    f.write(f"Error reading file: {e}")
                f.write("\n\n")

def organize_files_by_extension(start_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Exclude the output directory from being traversed
    output_dir_abs = os.path.abspath(output_dir)
    for root, dirs, files in os.walk(start_path):
        # Modify dirs in-place to exclude output_dir
        dirs[:] = [d for d in dirs if os.path.abspath(os.path.join(root, d)) != output_dir_abs]

        for file in files:
            file_ext = os.path.splitext(file)[1].lower()
            if file_ext:
                ext_folder = os.path.join(output_dir, file_ext[1:] + '_files')
                os.makedirs(ext_folder, exist_ok=True)
                src_file = os.path.join(root, file)
                dest_file = os.path.join(ext_folder, file)
                try:
                    shutil.copy2(src_file, dest_file)
                except Exception as e:
                    print(f"Error copying {src_file} to {dest_file}: {e}")

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Project Organizer")
        self.geometry("600x400")
        self.create_widgets()

    def create_widgets(self):
        # Start Directory Selection
        self.start_dir_label = ttk.Label(self, text="Select Project Directory:")
        self.start_dir_label.pack(pady=10)

        self.start_dir_entry = ttk.Entry(self, width=50)
        self.start_dir_entry.pack(pady=5)

        self.browse_start_btn = ttk.Button(self, text="Browse", command=self.browse_start_dir)
        self.browse_start_btn.pack(pady=5)

        # Output Options
        self.option = tk.StringVar(value="single")

        self.single_radio = ttk.Radiobutton(self, text="Export to Single Text File", variable=self.option, value="single", command=self.toggle_output_dir)
        self.single_radio.pack(pady=5)

        self.separate_radio = ttk.Radiobutton(self, text="Organize Files by Extension", variable=self.option, value="separate", command=self.toggle_output_dir)
        self.separate_radio.pack(pady=5)

        # Output Directory Selection (for separate option)
        self.output_dir_label = ttk.Label(self, text="Select Output Directory:")
        self.output_dir_label.pack(pady=10)

        self.output_dir_entry = ttk.Entry(self, width=50)
        self.output_dir_entry.pack(pady=5)

        self.browse_output_btn = ttk.Button(self, text="Browse", command=self.browse_output_dir)
        self.browse_output_btn.pack(pady=5)

        # Execute Button
        self.execute_btn = ttk.Button(self, text="Execute", command=self.execute_action)
        self.execute_btn.pack(pady=20)

        # Initially disable output directory selection if "single" is selected
        self.toggle_output_dir()

    def toggle_output_dir(self):
        if self.option.get() == "separate":
            self.output_dir_label.configure(state='normal')
            self.output_dir_entry.configure(state='normal')
            self.browse_output_btn.configure(state='normal')
        else:
            self.output_dir_label.configure(state='disabled')
            self.output_dir_entry.configure(state='disabled')
            self.browse_output_btn.configure(state='disabled')

    def browse_start_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.start_dir_entry.delete(0, tk.END)
            self.start_dir_entry.insert(0, directory)

    def browse_output_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir_entry.delete(0, tk.END)
            self.output_dir_entry.insert(0, directory)

    def execute_action(self):
        start_dir = self.start_dir_entry.get()
        if not start_dir or not os.path.isdir(start_dir):
            messagebox.showerror("Error", "Please select a valid project directory.")
            return

        option = self.option.get()

        if option == "single":
            output_dir = filedialog.askdirectory(title="Select Output Directory for Text File")
            if not output_dir:
                messagebox.showerror("Error", "Please select an output directory.")
                return
            output_file = os.path.join(output_dir, 'project_summary.txt')

            # Check if output_dir is inside start_dir
            if os.path.commonpath([os.path.abspath(start_dir)]) == os.path.commonpath([os.path.abspath(start_dir), os.path.abspath(output_dir)]):
                # Output directory is inside start_dir, which is allowed since we excluded it in the code
                pass

            try:
                write_project_to_file(start_dir, output_file)
                messagebox.showinfo("Success", f"Project has been saved to {output_file}")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

        elif option == "separate":
            output_dir = self.output_dir_entry.get()
            if not output_dir:
                messagebox.showerror("Error", "Please select an output directory.")
                return

            # Ensure output_dir is not inside start_dir to avoid potential issues
            if os.path.commonpath([os.path.abspath(start_dir)]) == os.path.commonpath([os.path.abspath(start_dir), os.path.abspath(output_dir)]):
                response = messagebox.askyesno("Warning", "The output directory is inside the project directory. This may lead to unexpected behavior. Do you want to continue?")
                if not response:
                    return

            try:
                organize_files_by_extension(start_dir, output_dir)
                messagebox.showinfo("Success", f"Files have been organized in {output_dir}")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

def main():
    app = Application()
    app.mainloop()

if __name__ == "__main__":
    main()
