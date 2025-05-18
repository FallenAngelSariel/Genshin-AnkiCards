from pathlib import Path


class Batch_Modify_Filename:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.input_dir = self.script_dir / "media"

        if not self.input_dir.exists():
            print(f"Input directory {self.input_dir} does not exist.")
            exit()

    def add_prefix(self, prefix):
        media_files = list(self.input_dir.glob("*.mp3")) + list(self.input_dir.glob("*.png"))
        if not media_files:
            print(f"No mp3 and png files in {self.input_dir}")
            return
        
        for file in media_files:
            new_name = f"{prefix}{file.name}"
            output_path = file.with_name(new_name)
            file.rename(output_path)
            print(f"Add prefix: {file.name} -> {new_name}")

    def delete_prefix(self, prefix):
        media_files = list(self.input_dir.glob(f"{prefix}*.mp3")) + list(self.input_dir.glob(f"{prefix}*.png"))
        if not media_files:
            print(f"No mp3 and png files with '{prefix}' in {self.input_dir}")
            return
        
        for file in media_files:
            if file.name.startswith(f"{prefix}"):
                new_name = file.name[len(prefix):]
                output_path = file.with_name(new_name)
                file.rename(output_path)
                print(f"Delete Prefix: {file.name} -> {new_name}")
        

if __name__ == "__main__":
    modifier = Batch_Modify_Filename()
    print("Choose what you want(1 or 2 or ...):")
    print("1. Add prefix")
    print("2. Delete prefix")
    selection = input("selection: ")
    if selection == "1":
        modifier.add_prefix(input("Input prefix: "))
    elif selection == "2":
        modifier.delete_prefix(input("Input prefix: "))








