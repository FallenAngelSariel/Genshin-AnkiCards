from pathlib import Path
import re
from typing import TextIO
class MdFileGenerate:
    
    def __init__(self):
        self.script_dir = Path(__file__).parent

    def write_header(self, file:TextIO):
        '''Write header'''
        file.write(f"TARGET DECK: Genshin::{self.script_dir.name.replace(' ','')}\n")

    def write_card(self, file:TextIO, audio_file:Path=None, image_files:list[Path]=None):
        '''Write a single card'''
        file.write("\n\n--- \n")
        file.write("START\n")
        file.write("Basic\n")
        file.write("Front:\n")
        if audio_file:
            audio_path = f"{audio_file.parent.name}/{audio_file.name}"
            file.write(f"![[{audio_path}]]\n")
        if image_files:
            for image_file in image_files:
                image_path = f"{image_file.parent.name}/{image_file.name}"
                file.write(f"![[{image_path}]]\n\n")

        file.write("Back:\n\n\n")
        file.write(f"Tags: Genshin::{self.script_dir.name}\n")
        file.write("END")

    def generate_VoiceCards(self, input_dir):
        audio_files = {f.stem: f for f in input_dir.glob("*.mp3")}
        image_files = {f.stem: f for f in input_dir.glob("*.png")}
        all_files = set(audio_files.keys()).union(set(image_files.keys()))

        output_path = input_dir.parent / f"{self.script_dir.name}.md"
        if not output_path.exists():
            with open(output_path, "w", encoding='utf-8') as f:
                self.write_header(f)
                for file_stem in sorted(all_files):
                    audio = audio_files.get(file_stem)
                    image = image_files.get(file_stem)
                    self.write_card(f,audio,[image])
            print(f"successfully created {self.count_cards(output_path)} Voicecards")
        else:
            existing_cards = set()
            with open(output_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if re.match('^!\[\[.*?\]\]$', line.strip()):
                        stem = line.strip()[3:-2].split('/')[-1].split(".")[0]
                        existing_cards.add(stem)
            new_files = all_files - existing_cards
            if new_files:
                with open(output_path, 'a', encoding='utf-8') as f:
                    for file_stem in sorted(new_files):
                        audio = audio_files.get(file_stem)
                        image = image_files.get(file_stem)
                        self.write_card(f, audio, [image])
                    print(f"Added {len(new_files)} new cards to existing file")
            else:
                print("No new cards to add")
                print(f"total cards: {self.count_cards(output_path)}")

    def generate_StoryCards(self, input_dir:Path):
        if not input_dir.exists():
            print("StoryCards' input_dir does not exist.")
            return
        image_groups = {}
        for image_file in input_dir.glob("*.png"):
            stem = image_file.stem
            root_name = re.sub(r"\d+$", '', stem)
            if root_name not in image_groups:
                image_groups[root_name] = []
            image_groups[root_name].append(image_file)

        for root_name in image_groups:
            image_groups[root_name].sort(key=lambda x:
                int(re.search(r'(\d+)$', x.stem).group(1) if re.search(r'(\d+)$', x.stem) else 0))

        output_path = self.script_dir / f"{self.script_dir.name}_Story.md"
        if not output_path.exists():
            with open(output_path, 'w', encoding='utf-8') as f:
                self.write_header(f)
                for root_name in sorted(image_groups.keys()):
                    self.write_card(f, None, image_groups[root_name])
            print(f"successfully created {len(image_groups)} StoryCards")
        
        else:
            existing_cards = set()
            with open(output_path, 'r', encoding='utf-8') as f:
                current_card_images = []
                for line in f:
                    line = line.strip()
                    if line == "START":
                        current_card_images = []
                    elif re.match("^!\[\[.*?\]\]$", line) and "Front:" in previous_lines:
                        image = line[3:-2].split('/')[-1].split('|')[0]
                        current_card_images.append(image)
                    elif line == "END":
                        if current_card_images:
                            first_image = current_card_images[0]
                            root_name = re.sub(r'\d+$', '', Path(first_image).stem)
                            existing_cards.add(root_name)
                    previous_lines = line

            new_groups = {}
            for root_name in image_groups:
                if root_name not in existing_cards:
                    new_groups[root_name] = image_groups[root_name]
            
            if new_groups:
                with open(output_path, 'a', encoding='utf-8') as f:
                    for root_name in sorted(new_groups.keys()):
                        self.write_card(f ,None, new_groups[root_name])
                print(f"Added {len(new_groups)} new grouped StoryCards to existing file")
            else:
                print("No new StoryCards to add.")
                print(f"Total Cards: {self.count_cards(output_path)}")

    def count_cards(self,file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                count = 0
                for line in lines:
                    if line.startswith('END'):
                        count += 1
        except Exception as e:
            print(f"Error in count_cards: {str(e)}")
        return count


    def add_DELETE(self, mdfile_path:Path):
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


    def update_media_path(self, mdfile_path:Path, input_dir:Path, prefix:str):
        '''Update media path in markdown file'''
        audio_files = list(input_dir.glob("*.mp3"))
        image_files = list(input_dir.glob("*.png"))
#        pasted_image =  list(self.attachment_dir.glob("*.png"))
        new_lines = []
        try:
            with open(mdfile_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            for line in lines:
                line_stripped = line.strip()
                
                if line_stripped.startswith("^![[attachments/"):
                    new_lines.append(line)
        
                elif re.match(r'^!\[\[.*?\]\]$', line_stripped):
                    media_name = line_stripped[3:-2].split('/')[-1].split('|')[0]

                    for audio_file in audio_files:
                        if audio_file.name[:len(prefix)] == prefix:
                            if media_name == audio_file.name[len(prefix):]:
                                audio_relative_path = f"{input_dir.name}/{audio_file.name}"
                                new_lines.append(f"![[{audio_relative_path}]]\n")
                        elif media_name[:len(prefix)] == prefix:
                            if media_name[len(prefix):] == audio_file.name:
                                audio_relative_path = f"{input_dir.name}/{audio_file.name}"
                                new_lines.append(f"![[{audio_relative_path}]]\n")
                        elif media_name == audio_file.name:
                            audio_relative_path = f"{input_dir.name}/{audio_file.name}"
                            new_lines.append(f"![[{audio_relative_path}]]\n")
                            
                    for image_file in image_files:
                        if image_file.name[:len(prefix)] == prefix:
                            if media_name in image_file.name[len(prefix):]:
                                image_relative_path = f"{input_dir.name}/{image_file.name}"
                                new_lines.append(f"![[{image_relative_path}]]\n")
                        elif media_name[:len(prefix)] == prefix:
                            if media_name[len(prefix):] in image_file.name:
                                image_relative_path = f"{input_dir.name}/{image_file.name}"
                                new_lines.append(f"![[{image_relative_path}]]\n")
                        elif media_name == image_file.name:
                            image_relative_path = f"{input_dir.name}/{image_file.name}"
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



class mdFileGenerate_UI:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.functions = [
            {"name": "Count Cards", "action": lambda gene: (
                print(gene.count_cards(self.select_file(self.script_dir)))
            )},
            {"name": "Generate VoiceCards", "action": lambda gene:
                gene.generate_VoiceCards(self.select_folder(self.script_dir))
            },
            {"name": "Generate StoryCards", "action": lambda gene:
                gene.generate_StoryCards(self.select_folder(self.script_dir))
            }
        ]

    def select_folder(self, path:Path):
        print("\nFolders:")
        folders = [folder for folder in path.iterdir() if folder.is_dir()]
        if not folders:
            print("No folders to be selected. Exit.")
            exit()
        else:
            for i, folder in enumerate(folders, 1):
                print(f"{i}. {folder.name}")
            try:
                choice = int(input("Select a folder: "))
                if 1<= choice <= len(folders):
                    return folders[choice-1]
                else:
                    print("Please enter a valid number.")
                    return None
            except ValueError:
                print(f"Please enter a valid number. {ValueError}")
                return None


    def select_file(self, path:Path) -> Path:
        '''Display files with numbers and let user select one'''
        print("\nAvailable markdown files: ")
        files = list(path.glob("*.md"))
        for i, file in enumerate(files, 1):
            print(f"{i}. {file.name}")
        try:
            choice = int(input(f"Enter the number of the files to process: "))
            if 1<= choice <= len(files):
                return files[choice-1]
            else:
                return None
        except ValueError:
            print("Please enter a valid number.")
            return None

    def print_functions(self):
        print("\nAvailable functions:")
        for i, func in enumerate(self.functions, 1):
            print(f"{i}. {func['name']}")

    def select_function(self):
        try:
            choice = int(input("Select a function:"))
            if 1<= choice <= len(self.functions):
                return choice-1
            else:
                print("Please enter a valid number")
                return None
        except ValueError:
            print(f"select_function: {ValueError}")


if __name__ == "__main__":
    gene = MdFileGenerate()
    ui = mdFileGenerate_UI()

    ui.print_functions()
    function_index = ui.select_function()
    if function_index is not None:
        selected_function = ui.functions[function_index]["action"](gene)






