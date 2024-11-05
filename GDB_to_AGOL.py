import arcgis
import os
import zipfile
import tkinter as tk
from tkinter import messagebox
from arcgis.gis import GIS

# Function to zip the geodatabase and upload it
def zip_and_upload():
    # Retrieve user inputs
    username = username_entry.get()
    password = password_entry.get()
    fgdb_path = fgdb_path_entry.get()
    zip_name = zip_name_entry.get()
    folder_name = folder_name_entry.get()

    # Create the full path for the zip file
    zip_path = os.path.join(os.path.dirname(fgdb_path), f"{zip_name}.zip")

    # Connect to your ArcGIS Online account
    g = GIS("https://www.arcgis.com", username, password)

    # Check if geodatabase path exists
    if not os.path.exists(fgdb_path):
        messagebox.showerror("Error", f"Geodatabase path not found: {fgdb_path}")
        return

    # Zip the geodatabase
    if not os.path.exists(zip_path):
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(fgdb_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path.relpath(file_path, os.path.dirname(fgdb_path)))
            print(f"Geodatabase zipped at {zip_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to zip the geodatabase: {e}")
            return

    # Find the folder object based on user input folder name
    folder_obj = None
    for folder in g.users.me.folders:
        if folder['title'] == folder_name:
            folder_obj = folder
            print(f"Folder found: {folder_name} (ID: {folder['id']})")
            break
    if not folder_obj:
        messagebox.showerror("Error", f"Folder '{folder_name}' not found.")
        return  # Exit if the folder does not exist

    # Define properties for the item
    serviceProp = {
        'type': 'File Geodatabase',
        'tags': 'sometag',
        'title': zip_name  # Use the user-defined name for the item
    }

    # Define publish properties
    pubProps = {
        "hasStaticData": 'true',
        "name": zip_name,
        "maxRecordCount": 2000,
        "layerInfo": {"capabilities": "Query"}
    }

    # Add the zipped geodatabase to the specified folder
    try:
        fgdb_item = g.content.add(item_properties=serviceProp, data=zip_path, folder=folder_obj['id'])
        print(f"Uploaded item: {fgdb_item.title} (Type: {fgdb_item.type})")
        # Publish the item
        fgdb_layer = fgdb_item.publish(publish_parameters=pubProps, file_type='filegeodatabase', overwrite=True)
        print(f"Published item: {fgdb_layer.title} (Type: {fgdb_layer.type})")
    except Exception as e:
        messagebox.showerror("Error", f"Error uploading or publishing the geodatabase: {e}")

# Create the main GUI window
root = tk.Tk()
root.title("Geodatabase Upload Tool")

# Create input fields for username, password, fgdb_path, zip name, and folder name
tk.Label(root, text="Username:").pack()
username_entry = tk.Entry(root)
username_entry.pack()

tk.Label(root, text="Password:").pack()
password_entry = tk.Entry(root, show="*")
password_entry.pack()

tk.Label(root, text="Geodatabase Path:").pack()
fgdb_path_entry = tk.Entry(root)
fgdb_path_entry.pack()

tk.Label(root, text="Layer Name:").pack()  # User-defined zip file name
zip_name_entry = tk.Entry(root)
zip_name_entry.pack()

tk.Label(root, text="Folder Name:").pack()
folder_name_entry = tk.Entry(root)
folder_name_entry.pack()

# Button to zip the geodatabase and upload
upload_button = tk.Button(root, text="Upload Geodatabase", command=zip_and_upload)
upload_button.pack()

# Run the GUI
root.mainloop()
