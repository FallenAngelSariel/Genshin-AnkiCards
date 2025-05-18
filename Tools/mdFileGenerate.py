from pathlib import Path

class AnkiCardGenerator:
    def __init__(
        self,
        input_folder,
        output_directory=None,
    ):
        self.input_folder = input_folder
        self.script_path = Path(__file__).resolve()
        self.input_dir = self.script_path.parent / input_folder
        self.output_dir = self.input_dir.parent if output_directory is None else Path(output_directory)
        self.tags_name = self.input_dir.name.replace(" ", "")

        if not self.input_dir.exists():
            raise FileNotFoundError(f"Input directory {self.input_dir} does not exist.")
        
    def generate_cards(self):
        audio_files = {f.stem: f for f in self.input_dir.glob("*.mp3")}
        image_files = {f.stem: f for f in self.input_dir.glob("*.png")}
        all_files = set(audio_files.keys()).union(set(image_files.keys()))

        self.output_mdfile_path = self.output_dir / f"{self.input_dir.name}.md"
        with open(self.output_mdfile_path, "w", encoding='utf-8') as f:
            self.write_header(f)
            for file_stem in sorted(all_files):
                audio = audio_files.get(file_stem)
                image = image_files.get(file_stem)
                self.write_card(f,audio,image)
                print(f"Created card for: {file_stem}")
        print(f"Cards generated successfully in: {generator.output_mdfile_path}")
            

    def write_header(self, file):
        '''Write header'''
        file.write("TARGET DECK: Genshin\n")

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
        file.write(f"Tags: Genshin {self.tags_name}\n")
        file.write("END")



if __name__ == "__main__":
    folder_name = input("Enter folder name: ")
    generator = AnkiCardGenerator(folder_name)
    generator.generate_cards()
    





























