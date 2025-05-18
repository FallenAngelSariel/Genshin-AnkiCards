from pathlib import Path

class MdFileProcessor:
    def __init__(
        self, 
        ):
        self.script_path = Path(__file__).parent

    def find_markdown_files(self) -> list[Path]:
        '''return a list of all markdown files in the working directory'''
        return list(self.script_path.glob("*.md"))

    def add_delete(self, file_path: Path):
        '''Add 'DELETE' line before each line starting with '<!--ID'.'''
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            new_lines = []
            for line in lines:
                if line.strip().startswith('<!--ID'):
                    new_lines.append("DELETE\n")
                new_lines.append(line)
        
            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(new_lines)
        except Exception as e:
            print(f"Error {str(e)}")

        
    def deleteIDs(self, file_path: Path):


    def select_delfile(self) -> Path:
        '''Display files with numbers and let user select one'''
        print("Available markdown files: ")
        files = self.find_markdown_files()
        for i, file in enumerate(files, 1):
            print(f"{i}. {file.name}")

        try:
            choice = int(input(f"Enter the number of the files to process (1-{len(files)}):  "))
            if 1<= choice <= len(files):
                return files[choice-1]
        except ValueError:
            print("Please enter a valid number.")



if __name__ == "__main__":
    processor = MdFileProcessor()
    markdown_files = processor.find_markdown_files()

    Function_selection = input("Select functions(1 or 2 or ...):")
    print("1. Delete IDs")


    if not markdown_files:
        print("No markdown files found in the current directory.")
        exit()
    if Function_selection == "1":
        selected_file = processor.select_delfile()
        success = processor.add_delete(selected_file)
    elif Function_selection == "2":
        print(f"\nSuccessfully processed: {selected_file.name}")



















