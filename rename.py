import os

def rename_pdfs_in_roles_folder(base_folder='data'):
    # Dapatkan semua folder (role) di dalam base_folder
    roles = [d for d in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, d))]
    
    for role in roles:
        role_folder = os.path.join(base_folder, role)
        files = [f for f in os.listdir(role_folder) if f.lower().endswith('.pdf')]
        files.sort()  # Supaya urutan konsisten
        
        for idx, filename in enumerate(files, start=1):
            old_path = os.path.join(role_folder, filename)
            new_filename = f"{idx}_{role}.pdf"
            new_path = os.path.join(role_folder, new_filename)
            
            # Rename file
            os.rename(old_path, new_path)
            print(f"Renamed: {old_path} -> {new_path}")

if __name__ == "__main__":
    rename_pdfs_in_roles_folder()
