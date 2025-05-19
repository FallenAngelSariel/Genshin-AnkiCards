from pathlib import Path
import re

class MdFileGenerate:
    
    def __init__(
        self, 
        input_folder = "media",

        prefix = ""
        ):
        self.script_dir = Path(__file__).parent
        self.input_folder = input_folder
        self.input_dir = self.script_dir / self.input_folder
        self.attachment_dir = self.script_dir  / "attachments"
        self.prefix = prefix
        self.character_name = self.script_dir.name.replace(" ", "")

        if not self.input_dir.exists():
            raise FileNotFoundError(f"Input directory {self.input_dir} does not exist.")

    def write_header(self, file):
        '''Write header'''
        file.write(f"TARGET DECK: Genshin::{self.character_name}\n")

    def write_card(self, file, audio_file, image_file):
        '''Write a single card'''
        file.write("\n\n--- \n")
        file.write("START\n")
        file.write("Basic\n")
        file.write("Front:\n")
        if audio_file:
            audio_path = f"{self.input_folder}/{audio_file.name}"
            file.write(f"![[{audio_path}]]\n")
        if image_file:
            image_path = f"{self.input_folder}/{image_file.name}"
            file.write(f"![[{image_path}]]\n\n")

        file.write("Back:\n\n\n")
        file.write(f"Tags: Genshin::{self.character_name}\n")
        file.write("END")

    def generate_cards(self):
        audio_files = {f.stem: f for f in self.input_dir.glob("*.mp3")}
        image_files = {f.stem: f for f in self.input_dir.glob("*.png")}
        all_files = set(audio_files.keys()).union(set(image_files.keys()))

        output_path = self.input_dir.parent / f"{self.script_dir.name}.md"
        with open(output_path, "w", encoding='utf-8') as f:
            self.write_header(f)
            for file_stem in sorted(all_files):
                audio = audio_files.get(file_stem)
                image = image_files.get(file_stem)
                self.write_card(f,audio,image)
                print(f"Created card for: {file_stem}")
        print(f"Cards generated successfully in: {output_path}")

    def count_cards(self,file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                count = 0
                for line in lines:
                    if line.startswith('END'):
                        count = count + 1
        except Exception as e:
            print(f"Error in count_cards: {str(e)}")
        return count
                

    def find_markdown_files(self) -> list[Path]:
        '''return a list of all markdown files in the working directory'''
        return list(self.script_dir.glob("*.md"))


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


    def select_file(self) -> Path:
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
#        pasted_image =  list(self.attachment_dir.glob("*.png"))
        new_lines = []
        try:
            with open(mdfile_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            for line in lines:
                line_stripped = line.strip()
                
                if re.match(r'^!\[\[attachments/.*?\]\]$', line_stripped):
                    new_lines.append(line)
        
                elif re.match(r'^!\[\[.*?\]\]$', line_stripped):
                    media_name = line_stripped[3:-2].split('/')[-1].split('|')[0]

                    for audio_file in audio_files:
                        if audio_file.name[:len(self.prefix)] == self.prefix:
                            if media_name == audio_file.name[len(self.prefix):]:
                                audio_relative_path = f"{self.input_folder}/{audio_file.name}"
                                new_lines.append(f"![[{audio_relative_path}]]\n")
                        elif media_name[:len(self.prefix)] == self.prefix:
                            if media_name[len(self.prefix):] == audio_file.name:
                                audio_relative_path = f"{self.input_folder}/{audio_file.name}"
                                new_lines.append(f"![[{audio_relative_path}]]\n")
                        elif media_name == audio_file.name:
                            audio_relative_path = f"{self.input_folder}/{audio_file.name}"
                            new_lines.append(f"![[{audio_relative_path}]]\n")
                            
                    for image_file in image_files:
                        if image_file.name[:len(self.prefix)] == self.prefix:
                            if media_name in image_file.name[len(self.prefix):]:
                                image_relative_path = f"{self.input_folder}/{image_file.name}"
                                new_lines.append(f"![[{image_relative_path}]]\n")
                        elif media_name[:len(self.prefix)] == self.prefix:
                            if media_name[len(self.prefix):] in image_file.name:
                                image_relative_path = f"{self.input_folder}/{image_file.name}"
                                new_lines.append(f"![[{image_relative_path}]]\n")
                        elif media_name == image_file.name:
                            image_relative_path = f"{self.input_folder}/{image_file.name}"
                            new_lines.append(f"![[{image_relative_path}]]\n")
                else:
                    new_lines.append(line)
                    
            output_path = mdfile_path.parent / f"{mdfile_path.stem}.md" 
            with open(output_path, 'w', encoding='utf-8') as file:
                file.writelines(new_lines)
        except Exception as e:
            print(f"Error in update media path: {str(e)}")

    
    def update_tags(self, mdfile_path:Path):
        try:
            with open(mdfile_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                new_lines = []
                for line in lines:
                    line_stripped = line.strip()
                    if line_stripped.startswith("Tags: "):
                        parts = line_stripped.split(' ')
                        new_tags = "Tags: " + parts[1] + "::" + parts[2] + "\n"
                        new_lines.append(new_tags)
                    else:
                        new_lines.append(line)

            output_path = mdfile_path.parent / f"{mdfile_path.stem}.md"
            with open(output_path, 'w', encoding='utf-8') as file:
                file.writelines(new_lines)
        except Exception as e:
            print(f"Error in update_tags: {str(e)}")




class ui:
    def __init__(self):
        pass



if __name__ == "__main__":
    processor = MdFileGenerate(prefix="Furina_")
    markdown_files = processor.find_markdown_files()

    print("1. Count Cards")
    print("2. Delete IDs")
    print("3. Update media path")
    print("4. Update Tags")
    print("5. Generate cards")
    Function_selection = input("\nSelect a function(1-5): ")


    if Function_selection == "1":
        selected_file = processor.select_file()
        num = processor.count_cards(selected_file)
        print(num)
    elif Function_selection == "2":
        selected_file = processor.select_file()
        processor.deleteIDs(selected_file)
    elif Function_selection == "3":
        selected_file = processor.select_file()
        processor.update_media_path(selected_file)
    elif Function_selection == "4":
        selected_file = processor.select_file()
        processor.update_tags(selected_file)
    elif Function_selection == "5":
        processor.generate_cards()



















