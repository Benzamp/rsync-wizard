import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
import pyperclip

class RsyncCommandGenerator:
    def __init__(self, master):
        self.master = master
        self.master.title('Rsync Wizard')
        self.set_dark_theme()
        self.create_widgets()

    def create_widgets(self):
        # Login command input and button
        login_frame = tk.Frame(self.master, bg='#1E1E1E')
        login_frame.grid(row=0, column=0, padx=10, pady=5, sticky='ew')

        tk.Label(login_frame, text="Login Command:", bg='#1E1E1E', fg='white').grid(row=0, column=0, sticky='w')
        self.login_command_text = tk.Text(login_frame, wrap=tk.WORD, width=50, height=5)
        self.login_command_text.grid(row=0, column=1, columnspan=2, padx=5, pady=5)
        self.login_button = tk.Button(login_frame, text="Login", command=self.execute_login_command)
        self.login_button.grid(row=0, column=3, padx=5, pady=5)

        # Projects dropdown
        projects_frame = tk.Frame(self.master, bg='#1E1E1E')
        projects_frame.grid(row=1, column=0, padx=10, pady=5, sticky='ew')

        tk.Label(projects_frame, text="Projects:", bg='#1E1E1E', fg='white').grid(row=0, column=0, sticky='w')
        self.project_variable = tk.StringVar()
        self.project_dropdown = ttk.Combobox(projects_frame, textvariable=self.project_variable, state="readonly", width=45)
        self.project_dropdown.grid(row=0, column=1, columnspan=2, padx=5, pady=5)
        # Bind the dropdown to certain event
        self.project_dropdown.bind("<<ComboboxSelected>>", self.fetch_pods)

        # Pods dropdown
        pods_frame = tk.Frame(self.master, bg='#1E1E1E')
        pods_frame.grid(row=2, column=0, padx=10, pady=5, sticky='ew')

        tk.Label(pods_frame, text="Pods:", bg='#1E1E1E', fg='white').grid(row=0, column=0, sticky='w')
        self.pod_variable = tk.StringVar()
        self.pod_dropdown = ttk.Combobox(pods_frame, textvariable=self.pod_variable, state="readonly", width=45)
        self.pod_dropdown.grid(row=0, column=1, columnspan=2, padx=5, pady=5)
        # Bind the dropdown when selection is changed
        self.pod_dropdown.bind("<<ComboboxSelected>>", self.update_source_path)

        # Source and destination paths
        paths_frame = tk.Frame(self.master, bg='#1E1E1E')
        paths_frame.grid(row=3, column=0, padx=10, pady=5, sticky='ew')

        tk.Label(paths_frame, text="Source Path:", bg='#1E1E1E', fg='white').grid(row=0, column=0, sticky='w')
        self.source_path_entry = tk.Entry(paths_frame, width=50)
        self.source_path_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(paths_frame, text="Destination Path:", bg='#1E1E1E', fg='white').grid(row=1, column=0, sticky='w')
        self.destination_path_entry = tk.Entry(paths_frame, width=50)
        self.destination_path_entry.grid(row=1, column=1, padx=5, pady=5)
        self.browse_dest_button = tk.Button(paths_frame, text="Browse", command=self.browse_destination)
        self.browse_dest_button.grid(row=1, column=2, pady=5)

        # No perms checkbox
        self.no_perms = tk.BooleanVar()
        self.no_perms_checkbox = tk.Checkbutton(paths_frame, text="No Perms", variable=self.no_perms)
        self.no_perms_checkbox.grid(row=1, column=3, padx=5, pady=5)

        # Submit button
        self.submit_button = tk.Button(self.master, text="Submit", command=self.output_command)
        self.submit_button.grid(row=4, column=0, padx=10, pady=5, sticky='ew')

        # Output Viewer
        output_frame = tk.Frame(self.master, bg='#1E1E1E')
        output_frame.grid(row=5, column=0, padx=10, pady=5, sticky='ew')

        tk.Label(output_frame, text="Rsync Command:", bg='#1E1E1E', fg='white').pack(side='top', padx=10, pady=5)
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, width=60, height=5, bg='#333', fg='white')
        self.output_text.pack(side='top', padx=10, pady=5)
        self.output_text.config(state='disabled')

        # Copy and Execute buttons
        buttons_frame = tk.Frame(self.master, bg='#1E1E1E')
        buttons_frame.grid(row=6, column=0, padx=10, pady=5, sticky='ew')

        self.copy_button = tk.Button(buttons_frame, text="Copy", command=self.copy_command, width=20, height=2)
        self.copy_button.grid(row=0, column=0, padx=5, pady=5)

        self.execute_button = tk.Button(buttons_frame, text="Execute", command=self.execute_command, width=20, height=2)
        self.execute_button.grid(row=0, column=1, padx=5, pady=5)

        # Checkbox to toggle console visibility
        self.console_visibility_var = tk.BooleanVar(value=True)
        self.console_visibility_checkbox = tk.Checkbutton(buttons_frame, text="Show Console", variable=self.console_visibility_var, command=self.toggle_console_visibility)
        self.console_visibility_checkbox.grid(row=1, column=0, columnspan=1)

        # Execution status and Status labels
        status_frame = tk.Frame(self.master, bg='#1E1E1E')
        status_frame.grid(row=7, column=0, padx=10, pady=5, sticky='ew')

        self.execution_status_label = tk.Label(status_frame, text="", fg="green", bg='#1E1E1E')
        self.execution_status_label.grid(row=0, column=0, padx=0, pady=5, sticky='ew')
        self.execution_status_label.grid_remove()

        self.status_label = tk.Label(status_frame, text="", fg="green", bg='#1E1E1E')
        self.status_label.grid(row=0, column=1, padx=10, pady=5, sticky='ew')

        # Console-like output window
        self.console_output = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, width=60, height=10, bg='#333', fg='white')
        self.console_output.grid(row=8, column=0, padx=10, pady=5, sticky='ew')

        self.master.update_idletasks()
        self.master.minsize(self.master.winfo_reqwidth(), self.master.winfo_reqheight() + 20)
        self.master.maxsize(self.master.winfo_reqwidth(), self.master.winfo_reqheight() + 20)

    def set_dark_theme(self):
        self.master.configure(bg='#1E1E1E')  # Set background color of the window
        self.master.option_add('*TCombobox*Listbox*background', '#333')  # Set background color of combo box dropdown
        self.master.option_add('*TCombobox*Listbox*foreground', 'white')  # Set text color of combo box dropdown
        self.master.option_add('*TCombobox*Listbox*selectBackground', '#444')  # Set background color of selected item in combo box dropdown
        self.master.option_add('*TCombobox*Listbox*selectForeground', 'white')  # Set text color of selected item in combo box dropdown

    def execute_login_command(self):
        login_command = self.login_command_text.get('1.0', tk.END).strip()
        if not login_command:
            messagebox.showerror("Error", "Please enter the login command.")
            return

        try:
            # Split the login command into individual arguments
            login_args = login_command.split()

            # Execute the login command without showing the command prompt window
            subprocess.run(login_args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=subprocess.STARTUPINFO(dwFlags=subprocess.CREATE_NO_WINDOW))

            # Execute 'oc project' command and capture the output
            result = subprocess.run(['oc', 'project'], capture_output=True, text=True)

            # Parse the output to extract the current project name
            current_project = None
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.startswith('Using project'):
                    current_project = line.split('Using project ')[1].strip()
                    break

            if current_project is None:
                raise ValueError("Failed to determine current project.")

            # Execute 'oc get projects' command and capture the output
            result = subprocess.run(['oc', 'get', 'projects', '-o', 'jsonpath={.items[*].metadata.name}'], capture_output=True, text=True)

            # Parse the output to extract project names
            projects = result.stdout.strip().split()
            projects = [project.replace('*', '') for project in projects]  # Remove '*' characters from project names

            # Update login button to show loading symbol
            self.login_button.config(text="Loading...", state="disabled")

            # Update project dropdown with fetched projects
            self.master.after(0, self.update_project_dropdown, projects)

            # Execute 'oc get pods' command and capture the output
            result = subprocess.run(['oc', 'get', 'pods'], capture_output=True, text=True)

            # Parse the output to extract pod names
            pod_lines = result.stdout.strip().split('\n')[1:]  # Skip the header line
            pods = [line.split()[0] for line in pod_lines]  # Extract the first column (pod name)

            # Update pod dropdown with fetched pods
            self.master.after(0, self.update_pod_dropdown, pods)
            if pods:
                messagebox.showinfo("Success", "Pods were found.")
            else:
                messagebox.showinfo("No Pods", "No pods were found.")

        except subprocess.CalledProcessError as e:
            # Handle any errors that occur during command execution
            messagebox.showerror("Error", f"Error executing command: {e}")
        except Exception as e:
            # Handle any other unexpected errors
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            # Reset login button text and state
            self.master.after(0, self.reset_login_button)


    def run_login_command(self, login_command):
        try:
            # Split the login command into individual arguments
            login_args = login_command.split()

            # Execute the login command without showing the command prompt window
            subprocess.run(login_args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=subprocess.STARTUPINFO(dwFlags=subprocess.CREATE_NO_WINDOW))

            # Execute 'oc project' command to get the current project
            result = subprocess.run(['oc', 'project'], capture_output=True, text=True)

            # Parse the output to extract the current project name
            current_project = result.stdout.strip().split()[-1]  # Get the last word, which is the current project name

            # Execute 'oc projects' command to get all projects
            result = subprocess.run(['oc', 'projects'], capture_output=True, text=True)

            # Parse the output to extract project names
            project_lines = result.stdout.strip().split('\n')[1:]  # Skip the header line
            projects = []
            for line in project_lines:
                if line.strip():  # Check if the line is not empty
                    project_name = line.split()[0]  # Extract the first column (project name)
                    if project_name != current_project:
                        projects.append(project_name)

            projects.append(current_project)  # Add the current project to the list of projects

            # Update the Projects dropdown with fetched projects
            self.update_project_dropdown(projects)

            if projects:
                messagebox.showinfo("Success", "Projects were found.")
            else:
                messagebox.showinfo("No Projects", "No projects were found.")
        except subprocess.CalledProcessError as e:
            # Handle any errors that occur during command execution
            messagebox.showerror("Error", f"Error executing command: {e}")
        finally:
            # Reset login button text and state
            self.master.after(0, self.reset_login_button)


    def update_project_dropdown(self, projects):
        if projects:
            self.project_variable.set("")
            self.project_dropdown["values"] = projects
        else:
            self.project_dropdown["values"] = []

    def reset_login_button(self):
        self.login_button.config(text="Login", state="normal")

    def get_pods(self):
        selected_project = self.project_variable.get()
        if not selected_project:
            messagebox.showerror("Error", "Please select a project.")
            return

        # Change the button text to show loading symbol
        self.get_pods_button.config(text="Loading...", state="disabled")

        # Execute the command "oc project <selected_project> && oc get pods" in a separate thread
        get_pods_thread = threading.Thread(target=self.run_get_pods_command, args=(selected_project,))
        get_pods_thread.start()

    def run_get_pods_command(self, event=None):
        selected_project = self.project_variable.get()
        if selected_project:
            try:
                # Execute 'oc project <selected_project> && oc get pods' command and capture the output
                result = subprocess.run(['oc', 'project', selected_project, '&&', 'oc', 'get', 'pods'], capture_output=True, text=True)

                # Parse the output to extract pod names
                pod_lines = result.stdout.strip().split('\n')[1:]  # Skip the header line
                pods = [line.split()[0] for line in pod_lines]  # Extract the first column (pod name)

                # Update pod dropdown with fetched pods
                self.master.after(0, self.update_pod_dropdown, pods)
                if pods:
                    messagebox.showinfo("Success", "Pods were found.")
                else:
                    messagebox.showinfo("No Pods", "No pods were found.")
            except subprocess.CalledProcessError as e:
                # Handle any errors that occur during command execution
                messagebox.showerror("Error", f"Error executing command: {e}")

    def browse_destination(self):
        dest_dir = filedialog.askdirectory()
        if dest_dir:
            self.destination_path_entry.delete(0, tk.END)
            self.destination_path_entry.insert(0, dest_dir)

    def update_source_path(self, event=None):
        selected_pod = self.pod_variable.get()
        if selected_pod:
            # Get the desired path from the user or set a default path
            desired_path = "/var/www/html/wp-content/plugins/"
            
            # Update the source path entry with the selected pod and the desired path
            self.source_path_entry.delete(0, tk.END)
            self.source_path_entry.insert(0, f"{selected_pod}:{desired_path}")

    def output_command(self):
        # Get the destination path
        destination_path = self.destination_path_entry.get()

        # Append '/' to the destination path if it doesn't end with '/'
        if destination_path and not destination_path.endswith('/'):
            destination_path += '/'

        # Append --no-perms=true if checkbox is checked
        if self.no_perms.get():  # Check the state of the checkbox
            destination_path += " --no-perms=true"

        # Construct the rsync command
        rsync_command = f"oc rsync {self.source_path_entry.get()} {destination_path}"

        # Display the rsync command in the output section
        self.output_text.config(state='normal')
        self.output_text.delete('1.0', 'end')
        self.output_text.insert('1.0', f"Rsync Command:\n{rsync_command}")
        self.output_text.config(state='disabled')

    def copy_command(self):
        # Copy the command to the clipboard
        command = self.output_text.get('1.0', 'end').strip()
        pyperclip.copy(command)

        # Change the button text to 'Copied!' and disable momentarily
        self.copy_button.config(text="Copied!", state="disabled")
        self.master.after(1000, self.reset_copy_button)

    def reset_copy_button(self):
        self.copy_button.config(text="Copy", state="normal")

    def execute_command(self):
        # Get the selected pod from the dropdown
        selected_pod = self.pod_dropdown.get()

        # Get the destination path
        destination_path = self.destination_path_entry.get()

        # Append '/' to the destination path if it doesn't end with '/'
        if destination_path and not destination_path.endswith('/'):
            destination_path += '/'

        # Append --no-perms=true if checkbox is checked
        if self.no_perms.get():  # Check the state of the checkbox
            destination_path += " --no-perms=true"

        # Construct the rsync command
        rsync_command = f"oc rsync {self.source_path_entry.get()} {destination_path}"

        # Change execute button text to 'Executing' and disable it
        self.execute_button.config(text="Executing", state="disabled")

        # Display the execution status
        self.execution_status_label.config(text="Executing rsync command...", fg="blue")
        self.execution_status_label.grid(row=9, column=0, columnspan=4, padx=10, pady=5, sticky='ew')

        # Execute the rsync command in a separate thread
        execute_thread = threading.Thread(target=self.run_rsync_command, args=(rsync_command,))
        execute_thread.start()

    def run_rsync_command(self, rsync_command):
        try:
            # Open a subprocess with stdout and stderr redirected to a pipe
            process = subprocess.Popen(rsync_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, bufsize=1)

            # Continuously read output from the subprocess and update the console window
            for line in iter(process.stdout.readline, ''):
                self.console_output.insert(tk.END, line)
                self.console_output.see(tk.END)  # Scroll to the end of the console window

            # Wait for the subprocess to finish
            process.wait()

            # Check the return code of the subprocess
            if process.returncode == 0:
                self.execution_status_label.config(text="Rsync command executed successfully.", fg="green")
                # Display a message in the console
                self.console_output.insert(tk.END, "Rsync command has been executed!\n")
                self.console_output.see(tk.END)  # Scroll to the end of the console window
            else:
                self.execution_status_label.config(text="Rsync command execution failed.", fg="red")
        except Exception as e:
            self.execution_status_label.config(text=f"Error executing rsync command: {e}", fg="red")
        finally:
            # Reset execute button text and state
            self.execute_button.config(text="Execute", state="normal")
            # Hide the execution status label after 3 seconds
            self.master.after(3000, self.hide_execution_status_label)

    def hide_execution_status_label(self):
        self.execution_status_label.grid_remove()

    def update_pod_dropdown(self, pods):
        if pods:
            self.pod_variable.set("")
            self.pod_dropdown["values"] = pods
        else:
            self.pod_dropdown["values"] = []

    

    # Define a new method fetch_pods to execute the commands to retrieve pods
    def fetch_pods(self, event=None):
        # Get the selected project from the Projects dropdown
        selected_project = self.project_dropdown.get()

        # Execute the commands to switch project and get pods
        if selected_project:
            try:
                # Execute 'oc project' command to switch the project
                subprocess.run(['oc', 'project', selected_project], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # Execute 'oc get pods' command and capture the output
                result = subprocess.run(['oc', 'get', 'pods'], capture_output=True, text=True)

                # Parse the output to extract pod names
                pod_lines = result.stdout.strip().split('\n')[1:]  # Skip the header line
                pods = [line.split()[0] for line in pod_lines]  # Extract the first column (pod name)

                # Update the pods dropdown with fetched pods
                self.update_pod_dropdown(pods)
            except subprocess.CalledProcessError as e:
                # Handle any errors that occur during command execution
                messagebox.showerror("Error", f"Error executing command: {e}")

    def toggle_console_visibility(self):
        if self.console_visibility_var.get():
            self.console_output.grid()
        else:
            self.console_output.grid_remove()

def main():
    window = tk.Tk()
    app = RsyncCommandGenerator(window)
    window.mainloop()

if __name__ == "__main__":
    main()
