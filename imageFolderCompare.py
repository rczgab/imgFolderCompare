import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import send2trash
from datetime import datetime

def get_file_info(filepath):
    """Return file size, image size (if image), and last modification date."""
    file_size = os.path.getsize(filepath)
    mod_time = os.path.getmtime(filepath)
    mod_date = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
    try:
        with Image.open(filepath) as img:
            img_size = img.size
    except:
        img_size = (0, 0)
    return file_size, img_size, mod_date

def compare_images(folder1, folder2):
    files1 = os.listdir(folder1)
    files2 = os.listdir(folder2)

    smaller_folder = files1 if len(files1) < len(files2) else files2
    larger_folder = files2 if len(files1) < len(files2) else files1

    for file in smaller_folder:
        if file in larger_folder:
            filepath1 = os.path.normpath(os.path.join(folder1, file))
            filepath2 = os.path.normpath(os.path.join(folder2, file))

            # Get file information
            size1, img_size1, mod_date1 = get_file_info(filepath1)
            size2, img_size2, mod_date2 = get_file_info(filepath2)

            display_images(filepath1, filepath2, size1, size2, img_size1, img_size2, mod_date1, mod_date2, file)

def display_images(filepath1, filepath2, size1, size2, img_size1, img_size2, mod_date1, mod_date2, filename):
    root = tk.Toplevel()
    root.title(f"Comparing: {filename}")
    
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

    # File name comparison (same filename, but added here for structure)
    file_name1 = os.path.basename(filepath1)
    file_name2 = os.path.basename(filepath2)
    color_name = 'green' if file_name1 == file_name2 else 'red'

    name_label1 = tk.Label(info_frame, text=f"Name: {file_name1}", fg=color_name)
    name_label1.grid(row=0, column=0)

    name_label2 = tk.Label(info_frame, text=f"Name: {file_name2}", fg=color_name)
    name_label2.grid(row=0, column=2)

    # File size comparison
    color_size = 'green' if size1 == size2 else 'red'
    size_label1 = tk.Label(info_frame, text=f"Size: {size1} bytes", fg=color_size)
    size_label1.grid(row=1, column=0)

    size_label2 = tk.Label(info_frame, text=f"Size: {size2} bytes", fg=color_size)
    size_label2.grid(row=1, column=2)

    # Image size comparison
    color_img_size = 'green' if img_size1 == img_size2 else 'red'
    img_size_label1 = tk.Label(info_frame, text=f"Image Size: {img_size1}", fg=color_img_size)
    img_size_label1.grid(row=2, column=0)

    img_size_label2 = tk.Label(info_frame, text=f"Image Size: {img_size2}", fg=color_img_size)
    img_size_label2.grid(row=2, column=2)

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
    mod_date_label1.grid(row=3, column=0)

    mod_date_label2 = tk.Label(info_frame, text=f"Modification Date: {mod_date2}", fg=color_mod_date2)
    mod_date_label2.grid(row=3, column=2)
    
    # Delete buttons with spacing
    delete_frame = tk.Frame(root)
    delete_frame.pack(side=tk.BOTTOM, padx=10, pady=10)

    def delete_file1():
        send2trash.send2trash(filepath1)
        root.destroy()

    def delete_file2():
        send2trash.send2trash(filepath2)
        root.destroy()

    delete_button1 = tk.Button(delete_frame, text="Delete Left Image", command=delete_file1, bg='red')
    delete_button1.grid(row=0, column=0)

    # Spacer between the buttons
    delete_spacer = tk.Label(delete_frame, width=10)  # Adjust width to create space between buttons
    delete_spacer.grid(row=0, column=1)

    delete_button2 = tk.Button(delete_frame, text="Delete Right Image", command=delete_file2, bg='red')
    delete_button2.grid(row=0, column=2)
    
    root.mainloop()

def main():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    folder1 = filedialog.askdirectory(title="Select First Folder")
    folder2 = filedialog.askdirectory(title="Select Second Folder")
    
    if folder1 and folder2:
        compare_images(folder1, folder2)
    else:
        print("Please select two valid folders.")
    
if __name__ == "__main__":
    main()
