from pathlib import Path
import re

class MdFileProcessor:
    
    def __init__(
        self, 
        input_folder = "media"
        ):
        self.script_path = Path(__file__).parent
        self.input_folder = input_folder
        self.input_dir = self.script_path / self.input_folder


    def find_markdown_files(self) -> list[Path]:
        '''return a list of all markdown files in the working directory'''
        return list(self.script_path.glob("*.md"))


    def add_delete(self, mdfile_path: Path):
        '''Add 'DELETE' line before each line starting with '<!--ID'.'''
        try:
            with open(mdfile_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            new_lines = []
            for line in lines:
                if line.strip().startswith('<!--ID'):
                    new_lines.append("DELETE\n")
                new_lines.append(line)
            with open(mdfile_path, 'w', encoding='utf-8') as file:
                file.writelines(new_lines)
        except Exception as e:
            print(f"Error in adding delete: {str(e)}")
        

    def deleteIDs(self, mdfile_path: Path):
        '''Delete each "<!--ID: -->" Line '''
        try:
            with open(mdfile_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            new_lines = []
            for line in lines:
                if not re.match(r'^\s*<!--ID:.*?-->\s*$', line):
                    new_lines.append(line)
            with open(mdfile_path, 'w', encoding='utf-8') as file:
                file.writelines(new_lines)
        except Exception as e:
            print(f"Error in deleteIDs: {str(e)}")


    def select_delfile(self) -> Path:
        '''Display files with numbers and let user select one'''
        print("Available markdown files: ")
        files = self.find_markdown_files()
        for i, file in enumerate(files, 1):
            print(f"{i}. {file.name}")

        try:
            choice = int(input(f"Enter the number of the files to process (1-{len(files)}): "))
            if 1<= choice <= len(files):
                return files[choice-1]
        except ValueError:
            print("Please enter a valid number.")


    def update_media_path(self, mdfile_path:Path):
        '''Update media path in markdown file'''
        audio_files = list(self.input_dir.glob("*.mp3"))
        image_files = list(self.input_dir.glob("*.png"))

        new_lines = []
        try:
            with open(mdfile_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            for line in lines:
                line_stripped = line.strip()
                if re.match(r'^!\[\[.*?\]\]$', line_stripped):
                    media_name = line_stripped[3:-2].split('/')[-1].split('|')[0]
                    for audio_file in audio_files:
                        if media_name in audio_file.name:
                            audio_relative_path = f"Genshin/Furina/{self.input_folder}/{audio_file.name}"
                            new_lines.append(f"![[{audio_relative_path}]]\n")
                            
                    for image_file in image_files:
                        if media_name in image_file.name:
                            image_relative_path = f"Genshin/Furina/{self.input_folder}/{image_file.name}"
                            new_lines.append(f"![[{image_relative_path}]]\n")
                else:
                    new_lines.append(line)
                    
            output_path = mdfile_path.parent / f"{mdfile_path.stem}.md" 
            with open(output_path, 'w', encoding='utf-8') as file:
                file.writelines(new_lines)
        except Exception as e:
            print(f"Error in update media path: {str(e)}")



if __name__ == "__main__":
    processor = MdFileProcessor()
    markdown_files = processor.find_markdown_files()

    print("1. Add DELETE")
    print("2. Delete IDs")
    print("3. Update media path")
    Function_selection = input("\nSelect a function(1-3): ")
    


    if not markdown_files:
        print("No markdown files found in the current directory.")
        exit()
    if Function_selection == "1":
        selected_file = processor.select_delfile()
        processor.add_delete(selected_file)
    elif Function_selection == "2":
        selected_file = processor.select_delfile()
        processor.deleteIDs(selected_file)
    elif Function_selection == "3":
        selected_file = processor.select_delfile()
        processor.update_media_path(selected_file)



















