import os
import glob
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ExifTags
from send2trash import send2trash
from datetime import datetime

# Constants for image display size
IMAGE_WIDTH = 500
IMAGE_HEIGHT = 750

class PictureComparatorApp:
    def __init__(self, folder_base):
        self.root = tk.Tk()
        self.root.geometry(f"{3 * IMAGE_WIDTH}x{IMAGE_HEIGHT + 150}+0+0")  # Position window at (0,0)
        self.root.title("Picture Comparator")

        self.folder_base = folder_base
        self.folders = self.get_input_folders(folder_base)
        self.image_files = self.get_image_files(folder_base)

        self.current_image_index = 0
        self.image_labels = []
        self.info_labels = []
        self.select_buttons = []

        self.create_gui()

    def get_input_folders(self, folder_base):
        """Retrieve the list of folders with decreasing numbers."""
        base_number = int(os.path.basename(folder_base))
        base_dir = os.path.dirname(folder_base)
        return [os.path.join(base_dir, str(i)) for i in range(base_number, 0, -1)]

    def get_image_files(self, folder_base):
        """Get all images from the base folder."""
        return sorted(glob.glob(os.path.join(folder_base, "*.jpg")))

    def create_gui(self):
        """Create the GUI elements."""
        for i in range(len(self.folders)):
            image_label = tk.Label(self.root)
            image_label.grid(row=0, column=i)
            self.image_labels.append(image_label)

            info_label = tk.Label(self.root, text="", wraplength=IMAGE_WIDTH, justify="center")
            info_label.grid(row=1, column=i)
            self.info_labels.append(info_label)

            select_button = tk.Button(self.root, text="Select", command=lambda i=i: self.select_image(i))
            select_button.grid(row=2, column=i)
            self.select_buttons.append(select_button)

        self.skip_button = tk.Button(self.root, text="Skip", command=self.next_image)
        self.skip_button.grid(row=3, column=1)

        self.load_image(self.current_image_index)

    def load_image(self, image_index):
        """Load the images from all folders for a specific image file."""
        if image_index >= len(self.image_files):
            messagebox.showinfo("Info", "No pictures left.")
            self.root.quit()
            return

        image_name = os.path.basename(self.image_files[image_index])
        self.common_info = {}

        for i, folder in enumerate(self.folders):
            image_path = os.path.join(folder, image_name)
            if os.path.exists(image_path):
                self.display_image(image_path, i)
            else:
                self.image_labels[i].config(image='', text=f"Image not found\n{folder}")
                self.info_labels[i].config(text="")

        # Highlight common info
        self.update_info_colors()

    def display_image(self, image_path, index):
        """Display the image and its info on the GUI."""
        img = Image.open(image_path)
        img.thumbnail((IMAGE_WIDTH, IMAGE_HEIGHT))
        img_tk = ImageTk.PhotoImage(img)

        self.image_labels[index].config(image=img_tk)
        self.image_labels[index].image = img_tk

        file_info = self.get_image_info(image_path)
        self.info_labels[index].config(text=file_info)

    def get_image_info(self, image_path):
        """Retrieve the image information to display below the picture."""
        file_stats = os.stat(image_path)
        modification_time = datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        file_size = file_stats.st_size / (1024 * 1024)  # Size in MB

        img = Image.open(image_path)
        width, height = img.size

        exif = img._getexif()
        dpi = img.info.get('dpi', (0, 0))
        bit_depth = img.mode
        camera_maker = geo_location = "Unknown"

        if exif:
            for tag, value in exif.items():
                decoded = ExifTags.TAGS.get(tag, tag)
                if decoded == "Make":
                    camera_maker = value
                if decoded == "GPSInfo":
                    geo_location = str(value)

        # Add common info logic
        file_info_dict = {
            "filename": os.path.basename(image_path),
            "modification_time": modification_time,
            "file_size": f"{file_size:.2f} MB",
            "resolution": f"{width}x{height}",
            "dpi": f"{dpi[0]}x{dpi[1]}",
            "bit_depth": bit_depth,
            "camera_maker": camera_maker,
            "geo_location": geo_location
        }

        self.update_common_info(file_info_dict)

        return (f"Filename: {file_info_dict['filename']}\n"
                f"Modified: {file_info_dict['modification_time']}\n"
                f"Size: {file_info_dict['file_size']}\n"
                f"Resolution: {file_info_dict['resolution']}\n"
                f"DPI: {file_info_dict['dpi']}\n"
                f"Bit Depth: {file_info_dict['bit_depth']}\n"
                f"Camera: {file_info_dict['camera_maker']}\n"
                f"Geo Location: {file_info_dict['geo_location']}")

    def update_common_info(self, info_dict):
        """Track common info for highlighting."""
        for key, value in info_dict.items():
            if key not in self.common_info:
                self.common_info[key] = {value}
            else:
                self.common_info[key].add(value)

    def update_info_colors(self):
        """Change the color of info labels based on commonality."""
        for i in range(len(self.folders)):
            info_text = self.info_labels[i].cget("text")
            updated_text = []
            for line in info_text.split("\n"):
                key = line.split(":")[0].strip().lower()
                value = line.split(":")[1].strip()
                if len(self.common_info.get(key, [])) == 1:  # Common value, display in green
                    updated_text.append(f"\033[32m{line}\033[0m")
                else:
                    updated_text.append(line)
            self.info_labels[i].config(text="\n".join(updated_text))

    def select_image(self, selected_index):
        """Move non-selected images to the recycle bin."""
        image_name = os.path.basename(self.image_files[self.current_image_index])
        for i, folder in enumerate(self.folders):
            image_path = os.path.join(folder, image_name)
            if os.path.exists(image_path):
                if i != selected_index:  # Keep the selected image, delete the others
                    send2trash(image_path)
        self.next_image()

    def next_image(self):
        """Move to the next image in the folder."""
        self.current_image_index += 1
        self.load_image(self.current_image_index)

    def run(self):
        self.root.mainloop()

# Entry point
if __name__ == "__main__":
    folder_base = input("Enter the path of the base folder: ")
    app = PictureComparatorApp(folder_base)
    app.run()
