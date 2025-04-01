from langflow.custom import Component
from langflow.io import Output
from langflow.io import FileInput
import os
import shutil
from pathlib import Path
import tempfile

from langflow.schema.message import Message

class FileUploadComponent(Component):
    display_name = "File Uploader"
    description = "Custom File Upload Component for all type of Files."
    name = "FileUploadComponent"
    icon="file-text"
    TEXT_FILE_TYPES = [
    "txt",
    "md",
    "mdx",
    "csv",
    "json",
    "yaml",
    "yml",
    "xml",
    "html",
    "htm",
    "pdf",
    "docx",
    "py",
    "sh",
    "sql",
    "js",
    "ts",
    "tsx",
    "jsx",
    "css",
    "scss",
    "less",
    "php",
    "java",
    "c",
    "cpp",
    "h",
    "hpp",
    "cs",
    "vb",
    "xlsx",
    "xls",
    "pptx",
    "ppt",
    "doc",
    "odt",]

    IMG_FILE_TYPES = ["jpg", "jpeg", "png", "bmp", "image"]

    inputs = [
        FileInput(
            name="file",
            display_name="File",
            file_types=TEXT_FILE_TYPES + IMG_FILE_TYPES + ["xlsx"],
            info="Files to be sent with the message.",
        ),
    ]
    
    outputs = [Output(display_name="File Path", name="file_path", method="save_file")]


    def save_file(self) -> Message:
        
        if not hasattr(self, 'file') or self.file is None:
            return Message(text="No file was uploaded. Please upload a file.")
        
       
        source_file_path = self.file
        
       
        if not source_file_path or not isinstance(source_file_path, (str, bytes, os.PathLike, int)):
            return Message(text="Invalid file path. Please try uploading again.")
            
        if not os.path.exists(source_file_path):
            return Message(text=f"File does not exist at path: {source_file_path}")
        
        
        temp_dir = Path(tempfile.gettempdir()) / "langflow_uploads"
        
        
        if not os.path.exists(temp_dir):
            try:
                os.makedirs(temp_dir, exist_ok=True)
            except PermissionError as e:
                return Message(text=f"Permission denied: Cannot create directory {temp_dir}.")
            except Exception as e:
                return Message(text=f"Error creating directory {temp_dir}: {e}")
        
        file_name = os.path.basename(source_file_path)
        temp_file = os.path.join(temp_dir, file_name)
        
        try:
            
            shutil.copy(source_file_path, temp_file)
            
           
            return Message(text=f"{temp_file}")
        
        except PermissionError as e:
            return Message(text=f"Permission denied: Cannot read or write the file. Error: {e}")
        
        except IOError as e:
            return Message(text=f"Error copying the file: {e}")
        
        except Exception as e:
            return Message(text=f"Unexpected error: {e}")