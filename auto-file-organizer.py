import os
import shutil

def organize_files_by_type(directory):
    """
    Organizes files in the specified directory into subdirectories based on file types:
    - Images: jpg, jpeg, png, gif, bmp, tiff, svg, webp, ico
    - Videos: mp4, avi, mkv, mov, wmv, flv, webm, m4v, 3gp
    - PDFs: pdf
    - Documents: doc, docx, txt, rtf, odt, xls, xlsx, ppt, pptx, csv
    
    :param directory: The path to the directory to organize.
    """
    if not os.path.isdir(directory):
        print(f"The specified path '{directory}' is not a valid directory.")
        return

    # Define file type categories
    file_categories = {
        'Images': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp', '.ico'},
        'Videos': {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp'},
        'PDFs': {'.pdf'},
        'Documents': {'.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx', '.csv'}
    }

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        
        if os.path.isfile(file_path):
            # Get the file extension
            _, ext = os.path.splitext(filename)
            ext = ext.lower()
            
            if ext:  # Only process files with an extension
                # Determine which category the file belongs to
                category = None
                for cat_name, extensions in file_categories.items():
                    if ext in extensions:
                        category = cat_name
                        break
                
                # If file type is recognized, move it to appropriate folder
                if category:
                    # Create the category directory if it doesn't exist
                    category_dir = os.path.join(directory, category)
                    if not os.path.exists(category_dir):
                        os.makedirs(category_dir)
                    
                    # Move the file to the corresponding category directory
                    destination = os.path.join(category_dir, filename)
                    shutil.move(file_path, destination)
                    print(f"Moved '{filename}' to '{category}' folder")
                else:
                    print(f"Skipped '{filename}' - unrecognized file type")
    
    print("File organization complete.")

if __name__ == "__main__":
    # Example usage
    target_directory = input("Enter the directory path to organize: ").strip()
    organize_files_by_type(target_directory)