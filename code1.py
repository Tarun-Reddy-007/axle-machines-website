import os
from PyPDF2 import PdfReader
import zipfile
import shutil

def processor(skills,count,file_path):

    def convert_folder_to_zip(folder_path):
        parent_directory = os.path.dirname(folder_path)
        folder_name = os.path.basename(folder_path)
        zip_path = os.path.join(parent_directory, f"{folder_name}.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arcname)

    def remove_dots_from_file_names(folder_path):
        files = os.listdir(folder_path)
        for file_name in files:
            file_path = os.path.join(folder_path, file_name)
            file_name_no_ext, file_extension = os.path.splitext(file_name)
            new_file_name = file_name_no_ext.replace(".", "")
            new_file_name_with_ext = new_file_name + file_extension
            new_file_path = os.path.join(folder_path, new_file_name_with_ext)
            os.rename(file_path, new_file_path)

    def copy_file(source_file, destination_directory):
        shutil.copy(source_file, destination_directory)

    def create_folder(directory, folder_name):
        folder_path = os.path.join(directory, folder_name)
        os.makedirs(folder_path)

    def unzip_file(filex_path, extract_path):
        with zipfile.ZipFile(filex_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
            
    directory_path = 'D:/axlemachineswebsite frontend/html and flask/static/resumes/filters/'
    folder_name = 'file'+str(count)

    directory_path = 'D:/axlemachineswebsite frontend/html and flask/static/resumes/filters/'+'file'+str(count)+'/'
    for sk in skills:
        create_folder(directory_path, sk)

    create_folder('D:/axlemachineswebsite frontend/html and flask/static/resumes/Uploads/', 'file'+str(count))

    zip_file_path = file_path
    extract_directory = 'D:/axlemachineswebsite frontend/html and flask/static/resumes/Uploads/'+'file'+str(count)
    unzip_file(zip_file_path, extract_directory)

    directory_path = 'D:/axlemachineswebsite frontend/html and flask/static/resumes/Uploads/'
    folder_name = 'txt files'
    create_folder(directory_path, folder_name)

    ukfolder = 'D:/axlemachineswebsite frontend/html and flask/static/resumes/Uploads/'+'file'+str(count)
    directories = next(os.walk(ukfolder))[1]
    unknown_folder_name = directories[0]
    

    folder_path = 'D:/axlemachineswebsite frontend/html and flask/static/resumes/Uploads/'+'file'+str(count)+'/'+unknown_folder_name
    remove_dots_from_file_names(folder_path)

    files_directory = 'D:/axlemachineswebsite frontend/html and flask/static/resumes/Uploads/'+'file'+str(count)+'/'+unknown_folder_name
    txt_directory = 'D:/axlemachineswebsite frontend/html and flask/static/resumes/txt files'

    for filename in os.listdir(files_directory):

        if filename.endswith(".pdf"):
            file_path = os.path.join(files_directory, filename)
            txt_filename = os.path.splitext(filename)[0] + ".txt"
            txt_path = os.path.join(txt_directory, txt_filename)
            with open(file_path, "rb") as file:
                pdf_reader = PdfReader(file)
                text_content = ""
                for page in pdf_reader.pages:
                    text_content += page.extract_text()
            with open(txt_path, "w", encoding="utf-8") as txt_file:
                txt_file.write(text_content)
        else:
            print("Folder contains file formats other than pdf which were ignored in the process.")

    txt_directory = 'D:/axlemachineswebsite frontend/html and flask/static/resumes/txt files'
    for filename in os.listdir(txt_directory):
        if filename.endswith(".txt"):
            file_path = os.path.join(txt_directory, filename)

            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                words = content.split()

                wordsl=[]
                for i in words:
                    l=i.lower()
                    wordsl.append(l)

                for sk in skills:
                    if sk in wordsl:
                        li= filename.split(".")
                        li[1]="pdf"
                        filename=".".join(li)
                        pdf_path = os.path.join('D:/axlemachineswebsite frontend/html and flask/static/resumes/Uploads/'+'file'+str(count)+'/'+unknown_folder_name, filename)
                        destination_directory=os.path.join('D:/axlemachineswebsite frontend/html and flask/static/resumes/filters/'+'file'+str(count),sk)
                        copy_file(pdf_path, destination_directory)

    shutil.rmtree('D:/axlemachineswebsite frontend/html and flask/static/resumes/Uploads/txt files')
    shutil.rmtree('D:/axlemachineswebsite frontend/html and flask/static/resumes/Uploads/'+'file'+str(count))

    folder_path = 'D:/axlemachineswebsite frontend/html and flask/static/resumes/filters/'+'file'+str(count)
    convert_folder_to_zip(folder_path)
    shutil.rmtree('D:/axlemachineswebsite frontend/html and flask/static/resumes/filters/'+'file'+str(count))
