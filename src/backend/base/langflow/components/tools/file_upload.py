from langflow.custom import Component
from langflow.io import Output
from langflow.io import FileInput
import os
import shutil
from pathlib import Path

from langflow.schema.message import Message

class FileUploadComponent(Component):
    display_name = "File Upload"
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
    
    outputs = [Output(display_name="Message", name="file_path", method="save_file")]


    def save_file(self) -> Message:
        home_dir = Path.home()
        destination_dir = home_dir / ".fileUploads"
        source_file_path = self.file
        if not os.path.exists(source_file_path):
            return Message(text="No file is uploaded or the file does not exist.")
        if not os.path.exists(destination_dir):
            try:
                os.makedirs(destination_dir, exist_ok=True)
            except PermissionError as e:
                return Message(text="Permission denied: Cannot create directory.")
            except Exception as e:
                return Message(text=f"Error creating directory: {e}")
        file_name = os.path.basename(source_file_path)
        destination_file = os.path.join(destination_dir, file_name)
        
        try:
            shutil.copy(source_file_path, destination_file)
            return Message(text=destination_file)
        
        except PermissionError as e:
            return Message(text="Permission denied: Cannot read or write the file.")
        
        except IOError as e:
            return Message(text=f"Error copying the file: {e}")
        
        except Exception as e:
            return Message(text=f"Unexpected error: {e}")