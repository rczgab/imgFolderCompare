import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from send2trash import send2trash
import datetime

class ImageComparerApp:
    def __init__(self, folder_base):
        self.folder_base = folder_base
        self.root_folder = os.path.dirname(folder_base)
        self.base_folder_number = int(os.path.basename(folder_base))
        self.other_folders = self.get_other_folders()
        self.image_files = self.get_image_files()
        self.current_index = 0

        self.root = tk.Tk()
        self.root.title("Image Comparer")
        self.root.geometry("+0+0")  # Position the window at (0,0)
        self.create_widgets()
        self.display_images()
        self.root.mainloop()

    def get_other_folders(self):
        folders = []
        for i in range(self.base_folder_number - 1, 0, -1):
            folder_path = os.path.join(self.root_folder, str(i))
            if os.path.isdir(folder_path):
                folders.append(folder_path)
        return folders

    def get_image_files(self):
        files = os.listdir(self.folder_base)
        image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        return image_files

    def create_widgets(self):
        self.image_frames = []
        self.select_buttons = []
        self.info_labels = []

        self.skip_button = tk.Button(self.root, text="Skip", command=self.skip_images)
        self.skip_button.pack(side=tk.TOP, pady=10)

        self.images_container = tk.Frame(self.root)
        self.images_container.pack()

    def display_images(self):
        if self.current_index >= len(self.image_files):
            self.clear_images()
            tk.Label(self.images_container, text="No pictures left.").pack()
            return

        image_name = self.image_files[self.current_index]
        image_paths = [os.path.join(self.folder_base, image_name)]
        for folder in self.other_folders:
            image_path = os.path.join(folder, image_name)
            if os.path.exists(image_path):
                image_paths.append(image_path)

        if not image_paths:
            self.current_index += 1
            self.display_images()
            return

        self.clear_images()

        infos = []
        sizes = []
        mod_times = []
        file_sizes = []

        for idx, img_path in enumerate(image_paths):
            frame = tk.Frame(self.images_container)
            frame.pack(side=tk.LEFT, padx=10)

            img = Image.open(img_path)
            img = img.resize((500, 750), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(img)

            img_label = tk.Label(frame, image=photo)
            img_label.image = photo  # Keep a reference to prevent garbage collection
            img_label.pack()

            # Get image info
            info = f"Dimensions: {img.width}x{img.height}"
            infos.append(info)

            # Get modification date
            mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(img_path))
            mod_times.append(mod_time.strftime('%Y-%m-%d %H:%M:%S'))

            # Get file size
            size_mb = os.path.getsize(img_path) / (1024 * 1024)
            file_sizes.append(f"{size_mb:.2f} MB")

            # Get file name
            file_name = os.path.basename(img_path)

            # Collect info labels
            label_text = f"{info}\nModified: {mod_times[-1]}\n{file_name}\nSize: {file_sizes[-1]}"
            info_label = tk.Label(frame, text=label_text, justify=tk.CENTER)
            info_label.pack()
            self.info_labels.append(info_label)

            # Select button
            select_button = tk.Button(frame, text="Select", command=lambda p=img_path: self.select_image(p, image_paths))
            select_button.pack(pady=5)
            self.select_buttons.append(select_button)

        # Compare infos and color text accordingly
        if all(inf == infos[0] for inf in infos):
            for label in self.info_labels:
                label.config(fg="green")
        else:
            for label in self.info_labels:
                label.config(fg="black")

    def clear_images(self):
        for widget in self.images_container.winfo_children():
            widget.destroy()

    def select_image(self, selected_image_path, all_image_paths):
        for img_path in all_image_paths:
            if img_path != selected_image_path and os.path.exists(img_path):
                send2trash(img_path)
        self.current_index += 1
        self.display_images()

    def skip_images(self):
        self.current_index += 1
        self.display_images()

def main():
    import sys
    if len(sys.argv) != 2:
        print("Usage: python script.py <folder_base_path>")
        return
    folder_base = sys.argv[1]
    if not os.path.isdir(folder_base):
        print("Provided folder_base path does not exist.")
        return
    app = ImageComparerApp(folder_base)

if __name__ == "__main__":
    main()
