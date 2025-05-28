from pathlib import Path
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
from typing import Callable

PATH_VOICE_ORIGINAL = "Voice_Original"
PATH_VOICE = "Voice"
PATH_STORY = "Story"

class Preprocess:
    VALID_SAMPLE_RATES = {22050, 32000, 44100, 48000}
    VALID_BITRATES = {"32k", "64k", "96k", "128k", "192k", "256k", "320k"}

    def __init__(
        self,
        sample_rate=32000,
        bitrate="256k",
        channels=1,
        silence_threshold=-50,
        min_silence_duration=700,
        padding_duration=300
    ):
        self.sample_rate = sample_rate
        self.bitrate = bitrate
        self.channels = channels
        self.silence_threshold = silence_threshold
        self.min_silence_duration = min_silence_duration
        self.padding_duration = padding_duration

        self.allow_folders = {PATH_VOICE_ORIGINAL, PATH_VOICE, PATH_STORY}
        self.functions = [
            {"name": "Full Preparations", "action": lambda prep, input_dir_path: (
                prep.prepare_audio_assets(input_dir_path),
                prep.copy_pngfile(input_dir_path, input_dir_path.parent/PATH_VOICE),
                prep.add_prefix(prefix=f"{input_dir_path.parent.name}_", input_dir_path=input_dir_path.parent/PATH_VOICE)
            )},
            {'name': "add prefix", "action": lambda prep, input_dir_path: 
                prep.add_prefix(prefix=f"{input_dir_path.parent.name}_", input_dir_path=input_dir_path)
            },
            {'name': "Delete prefix", "action": lambda prep, input_dir_path:
                prep.delete_prefix(prefix=input("enter delete prefix: "), input_dir_path=input_dir_path)
            },
            {'name': "Change subfix", "action":lambda prep, input_dir_path:
                prep.change_subfix(input_dir_path)    
            }
        ]

    @staticmethod
    def is_valid_directory(path:Path):
        if not path.exists():
            print(f"{path} Does not exist.")
            exit()

    def _process_audio(
        self,
        input_dir_path: Path,
        output_subdir: str,
        file_extension: str,
        *process_funcs: Callable[[AudioSegment],AudioSegment],
        output_format: str = "flac"
    ) -> None:
        '''chulimuluzhongdeyinpinwenjian'''
        self.is_valid_directory(input_dir_path)
        output_dir_path = input_dir_path.parent / output_subdir
        output_dir_path.mkdir(parents=True, exist_ok=True)

        input_files = list(input_dir_path.glob(f"*.{file_extension}"))
        for input_file in input_files:
            try:
                audio = AudioSegment.from_file(input_file, format=file_extension)
                processed_audio = audio
                for func in process_funcs:
                    processed_audio = func(processed_audio)

                output_path = output_dir_path / f"{input_file.stem}.{output_format}"
                processed_audio.export(output_path, format=output_format)
            except Exception as e:
                print(f"Error Processing {input_file}: {str(e)}")

    def trim_edge_silence(self, audio_segment):
        '''remove silence of the beginning and end of an audio segment'''
        non_silence_sections = detect_nonsilent(
            audio_segment,
            min_silence_len=self.min_silence_duration,
            silence_thresh=self.silence_threshold
        )
        if not non_silence_sections:
            print(f"{audio_segment}No no-silent segments detected.")
            return audio_segment
        
        start_time, end_time = non_silence_sections[0][0], non_silence_sections[-1][1]
        extend_start = max(start_time - self.padding_duration, 0)
        extended_end = min(end_time + self.padding_duration, len(audio_segment))
        return audio_segment[extend_start:extended_end]

    def batch_trim_edge_silence(self, input_dir_path):
        '''Process all FALC files in the input directory to remove silence.'''
        self._process_audio(
            input_dir_path,
            "Trim",
            "flac",
            self.trim_edge_silence
        )

    def compress(self, audio_segment):
        processed_audio = audio_segment.set_frame_rate(self.sample_rate).set_channels(self.channels)
        return processed_audio

    def batch_compress_to_mp3(self, input_dir_path):
        '''Compress or convert FLAC files to MP3 format.'''
        self._process_audio(
            input_dir_path,
            "CompressToMP3",
            "flac",
            self.compress,
            "mp3"
        )

    def prepare_audio_assets(self, input_dir_path):
        ''' '''
        self._process_audio(
            input_dir_path,
            PATH_VOICE,
            "flac",
            self.trim_edge_silence,
            self.compress,
            output_format="mp3"
        )

    def copy_pngfile(self, input_dir_path, output_dir_path):
        self.is_valid_directory(input_dir_path)
        png_files = list(input_dir_path.glob("*.png"))
        if not png_files:
            print(f"No png file found in {input_dir_path}")
            return
        
        output_dir_path.mkdir(parents=True, exist_ok=True)
        for png_file in png_files:
            output_path = output_dir_path / png_file.name
            output_path.write_bytes(png_file.read_bytes())
        print(f"Total copy pngfile: {len(png_files)}")

    def add_prefix(self, prefix, input_dir_path):
        self.is_valid_directory(input_dir_path)
        media_files = list(input_dir_path.glob("*.mp3")) + list(input_dir_path.glob("*.png"))
        if not media_files:
            print(f"No mp3 or png files in {input_dir_path}")
            return
        
        for file in media_files:
            new_name = f"{prefix}{file.name}"
            output_path = file.with_name(new_name)
            file.rename(output_path)
        print(f"Total add_prefix files: {len(media_files)}")

    def delete_prefix(self, prefix, input_dir_path):
        self.is_valid_directory(input_dir_path)

        media_files = list(input_dir_path.glob(f"{prefix}*.mp3")) + list(input_dir_path.glob(f"{prefix}*.png"))
        if not media_files:
            print(f"No mp3 and png files with '{prefix}' in {input_dir_path}")
            return
        
        for file in media_files:
            new_name = file.name[len(prefix):]
            output_path = file.with_name(new_name)
            file.rename(output_path)
        print(f"Total Delete_prefix files: {len(media_files)}")

    def change_subfix(self, input_dir_path:Path):
        self.is_valid_directory(input_dir_path)
        png_files = list(input_dir_path.glob("*.png"))
        count = 0
        for png_file in png_files:
            file_subfix = png_file.stem.split(" ")[-1].split(".")[0]
            if file_subfix == "I":
                count += 1
                new_name = png_file.with_name(png_file.name.replace(" I", "_1"))
                png_file.rename(new_name)
            elif file_subfix == "II":
                count += 1
                new_name = png_file.with_name(png_file.name.replace(" II", "_2"))
                png_file.rename(new_name)
            elif file_subfix == "III":
                count += 1
                new_name = png_file.with_name(png_file.name.replace(" III", "_3"))
                png_file.rename(new_name)
        print(f"Total change_subfix files: {count}")
    
    def select_folder(self):
        print("searching folders...")
        script_dir_path = Path(__file__).parent

        folders = [folder for folder in script_dir_path.iterdir()
                   if folder.is_dir() and folder.name in self.allow_folders]
        if not folders:
            print("No folders to be selected.")
            exit()

        for i, folder in enumerate(folders, 1):
            print(f"{i}.{folder.name}")
        choice = int(input("select a folder: "))
        if 1 <= choice <= len(folders):
            return folders[choice-1]
        else:
            print("please enter a valid number")
            return None

    def print_functions(self):
        print("\nAvailable functions:")
        for i, func in enumerate(self.functions, 1):
            print(f"{i}. {func['name']}")

    def select_function(self) -> int:
        self.print_functions()
        try:
            choice = int(input("Selecte a function: "))
            if 1<= choice <= len(self.functions):
                return choice-1
            else:
                print("Please enter a valid number")
                return None
        except ValueError:
            print(f"select function: {ValueError}")
    


if __name__ == "__main__":
    prep = Preprocess(
        sample_rate= 32000,
        bitrate= "128k",
        channels= 1,
        silence_threshold= -50,
        min_silence_duration= 700,
        padding_duration= 300
    )

    selected_folder = prep.select_folder()
    if selected_folder:
        selected_function_index = prep.select_function()
        if selected_function_index is not None:
            selected_func = prep.functions[selected_function_index]["action"]
            selected_func(prep, selected_folder)




