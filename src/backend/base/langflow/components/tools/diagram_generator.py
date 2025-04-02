import os
import re
import tempfile
from langflow.custom.custom_component.component import Component
from langflow.inputs.inputs import MessageInput
from langflow.schema.message import Message
from langflow.template.field.base import Output
from plantuml import PlantUML
 
 
class DiagramGenerator(Component):
    display_name = "Diagram Generator"
    description = "A component to generate plantuml diagrams from plantuml code."
    inputs = [
        MessageInput(
            name="plantuml_code",
            display_name="PlantUML Code",
            info="Takes UML Code as input.",
            tool_mode=True
        )
    ]
 
    outputs = [
        Output(display_name="Result", name="result", method="generate_diagram_image"),
    ]
 
    def extract_plantuml_diagrams(self):
        """Extract PlantUML diagram code blocks from content"""
        pattern = r'(?P<full_block>(?P<code>@startuml.*?@enduml))'
        matches = re.finditer(pattern, str(self.plantuml_code), re.DOTALL)
        diagrams = set()
        for idx, match in enumerate(matches):
            full_block = match.group('full_block')
            code = match.group('code').strip()
            if not code.startswith('@startuml'):
                code = '@startuml\n' + code
            if not code.endswith('@enduml'):
                code += '\n@enduml'
            placeholder = f"[DIAGRAM_{idx}]"
            #return Message(text=code)
            tup = (code, full_block)
            diagrams.add(tup)
        return diagrams
 
 
    def generate_diagram_image(self) -> Message:
        """Generate PNG image from PlantUML code"""
        diagrams = self.extract_plantuml_diagrams()
        if len(diagrams) == 0:
            return Message(text="No Diagram code is found")
        temp_file_path = None
        temp_dir=tempfile.mkdtemp()
        plantuml_server = PlantUML(url='http://www.plantuml.com/plantuml/png/')
        num = 0
        for i in diagrams:
            num+=1
            with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.puml', encoding='utf-8', dir=temp_dir) as temp_file:
                temp_file.write(i[0].encode("utf-8").decode("unicode_escape"))
                temp_file_path = temp_file.name
            filename = f"{num}.png"
            output_path = os.path.join(temp_dir, filename)
            plantuml_server.processes_file(filename=temp_file_path, outfile=output_path)
        return Message(text=temp_dir)