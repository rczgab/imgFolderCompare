import os
import shutil
import send2trash
import tkinter as tk
from PIL import Image, ImageTk
from datetime import datetime

# Helper function to get file information
def get_file_info(filepath):
    file_size = os.path.getsize(filepath) / (1024 * 1024)  # Convert bytes to MB
    img = Image.open(filepath)
    img_size = img.size
    mod_time = os.path.getmtime(filepath)
    mod_date = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
    return file_size, img_size, mod_date

# Function to move the image to the "same" folder
def move_to_same_folder(filepath, same_folder):
    # Ensure the "same" folder exists
    if not os.path.exists(same_folder):
        os.makedirs(same_folder)
    # Move the file to the "same" folder
    shutil.move(filepath, os.path.join(same_folder, os.path.basename(filepath)))

# Function to display images and their comparisons
def display_images(file_list, idx, same_folder, window_position=None):
    if idx >= len(file_list):
        # No more images to compare
        root = tk.Tk()
        root.title("No more pictures")
        label = tk.Label(root, text="No more pictures to compare")
        label.pack(padx=20, pady=20)
        root.mainloop()
        return
    
    filepath1, filepath2, size1, size2, img_size1, img_size2, mod_date1, mod_date2, filename = file_list[idx]

    root = tk.Toplevel()
    root.title(f"Comparing: {filename}")
    
    # Set window position to the previous window's position
    if window_position:
        root.geometry(f"+{window_position[0]}+{window_position[1]}")

    # Load and resize images
    img1 = Image.open(filepath1).resize((600, 900))
    img2 = Image.open(filepath2).resize((600, 900))
    
    img1 = ImageTk.PhotoImage(img1)
    img2 = ImageTk.PhotoImage(img2)
    
    # Create a frame for the images
    frame = tk.Frame(root)
    frame.pack(side=tk.TOP, padx=10, pady=10)
    
    # Image display
    label_img1 = tk.Label(frame, image=img1)
    label_img1.image = img1
    label_img1.grid(row=0, column=0)
    
    label_img2 = tk.Label(frame, image=img2)
    label_img2.image = img2
    label_img2.grid(row=0, column=2)
    
    # File info comparison
    info_frame = tk.Frame(root)
    info_frame.pack(side=tk.TOP, padx=10, pady=10)
    
    # Empty label for spacing (200px wide)
    spacer = tk.Label(info_frame, width=20)  # Adjust width to create 200px space
    spacer.grid(row=0, column=1, rowspan=4)

    # File size comparison (shown in MB)
    color_size = 'green' if size1 == size2 else 'red'
    size_label1 = tk.Label(info_frame, text=f"Size: {size1:.2f} MB", fg=color_size)
    size_label1.grid(row=0, column=0)

    size_label2 = tk.Label(info_frame, text=f"Size: {size2:.2f} MB", fg=color_size)
    size_label2.grid(row=0, column=2)

    # Image size comparison
    color_img_size = 'green' if img_size1 == img_size2 else 'red'
    img_size_label1 = tk.Label(info_frame, text=f"Image Size: {img_size1}", fg=color_img_size)
    img_size_label1.grid(row=1, column=0)

    img_size_label2 = tk.Label(info_frame, text=f"Image Size: {img_size2}", fg=color_img_size)
    img_size_label2.grid(row=1, column=2)

    # Modification date comparison
    mod_date1_dt = datetime.strptime(mod_date1, '%Y-%m-%d %H:%M:%S')
    mod_date2_dt = datetime.strptime(mod_date2, '%Y-%m-%d %H:%M:%S')

    if mod_date1_dt > mod_date2_dt:
        color_mod_date1 = 'red'   # Newer date is red
        color_mod_date2 = 'green' # Older date is green
    else:
        color_mod_date1 = 'green'
        color_mod_date2 = 'red'

    mod_date_label1 = tk.Label(info_frame, text=f"Modification Date: {mod_date1}", fg=color_mod_date1)
    mod_date_label1.grid(row=2, column=0)

    mod_date_label2 = tk.Label(info_frame, text=f"Modification Date: {mod_date2}", fg=color_mod_date2)
    mod_date_label2.grid(row=2, column=2)

    # File name moved below modification date
    file_name1 = os.path.basename(filepath1)
    file_name2 = os.path.basename(filepath2)
    color_name = 'green' if file_name1 == file_name2 else 'red'

    name_label1 = tk.Label(info_frame, text=f"Name: {file_name1}", fg=color_name)
    name_label1.grid(row=3, column=0)

    name_label2 = tk.Label(info_frame, text=f"Name: {file_name2}", fg=color_name)
    name_label2.grid(row=3, column=2)
    
    # Delete buttons with spacing
    button_frame = tk.Frame(root)
    button_frame.pack(side=tk.BOTTOM, padx=10, pady=10)

    def delete_file1():
        send2trash.send2trash(filepath1)
        save_position_and_continue()

    def delete_file2():
        send2trash.send2trash(filepath2)
        save_position_and_continue()

    delete_button1 = tk.Button(button_frame, text="Delete Left Image", command=delete_file1, bg='red')
    delete_button1.grid(row=0, column=0)

    # Spacer between the buttons
    delete_spacer = tk.Label(button_frame, width=10)  # Adjust width to create space between buttons
    delete_spacer.grid(row=0, column=1)

    delete_button2 = tk.Button(button_frame, text="Delete Right Image", command=delete_file2, bg='red')
    delete_button2.grid(row=0, column=2)

    # Skip button to skip the current image pair
    def skip_image():
        save_position_and_continue()

    skip_button = tk.Button(button_frame, text="Skip", command=skip_image, bg='yellow')
    skip_button.grid(row=0, column=3)
    
    # Function to save window position and continue to the next image pair
    def save_position_and_continue():
        root.update_idletasks()
        window_position = (root.winfo_x(), root.winfo_y())
        root.destroy()
        display_images(file_list, idx + 1, same_folder, window_position)

    # Move to "same" folder if all properties match
    if file_name1 == file_name2 and size1 == size2 and img_size1 == img_size2 and mod_date1 == mod_date2:
        move_to_same_folder(filepath1, same_folder)

        # Move on to next pair after auto-move
        save_position_and_continue()
    else:
        root.mainloop()

# Main function to start comparing images
def start_comparing(folder1, folder2):
    files1 = os.listdir(folder1)
    files2 = os.listdir(folder2)

    smaller_folder = files1 if len(files1) < len(files2) else files2
    larger_folder = files2 if len(files1) < len(files2) else files1

    file_list = []
    for file in smaller_folder:
        if file in larger_folder:
            filepath1 = os.path.normpath(os.path.join(folder1, file))
            filepath2 = os.path.normpath(os.path.join(folder2, file))
            size1, img_size1, mod_date1 = get_file_info(filepath1)
            size2, img_size2, mod_date2 = get_file_info(filepath2)

            file_list.append((filepath1, filepath2, size1, size2, img_size1, img_size2, mod_date1, mod_date2, file))
    
    if file_list:
        # Create the "same" folder path
        same_folder = os.path.join(os.path.dirname(folder1), "same")
        display_images(file_list, 0, same_folder)
    else:
        root = tk.Tk()
        root.title("No more pictures")
        label = tk.Label(root, text="No more pictures to compare")
        label.pack(padx=20, pady=20)
        root.mainloop()

# Example usage
folder1 = "path_to_folder1"
folder2 = "path_to_folder2"
start_comparing(folder1, folder2)
