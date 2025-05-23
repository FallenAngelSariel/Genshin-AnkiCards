from pathlib import Path
from pydub import AudioSegment
from pydub.silence import detect_nonsilent


class FlacProcess:
    VALID_SAMPLE_RATES = {22050, 32000, 44100, 48000}
    VALID_BITRATES = {"32k", "64k", "96k", "128k", "192k", "256k", "320k"}

    def __init__(
        self,
        input_folder="OriginalSources",
        output_directory=None,
        sample_rate=32000,
        bitrate="256k",
        channels=1,
        silence_threshold=-50,
        min_silence_duration=700,
        padding_duration=300
    ):
        self.script_dir = Path(__file__).parent
        self.input_folder = input_folder
        self.input_dir = self.script_dir / self.input_folder
        self.output_dir = self.input_dir.parent if output_directory is None else Path(output_directory)
        self.output_dir_trimmed = self.output_dir / "Trimmed_audio"
        self.output_dir_compressed = self.output_dir / "Compressed_audio"
        self.output_dir_final = self.output_dir / "media"
        self.sample_rate = sample_rate
        self.bitrate = bitrate
        self.channels = channels
        self.silence_threshold = silence_threshold
        self.min_silence_duration = min_silence_duration
        self.padding_duration = padding_duration

        if not self.input_dir.exists():
            raise FileNotFoundError(f"Input directory {self.input_dir} does not exist.")


    def count_flac_files(self):
        '''count the number of FLAC files in the input directory'''
        return len(list(self.input_dir.glob("*.flac")))
        

    def strip_silence(self, audio_segment):
        '''remove silence of the beginning and end of an audio segment'''
        non_silence_sections = detect_nonsilent(
            audio_segment,
            min_silence_len=self.min_silence_duration,
            silence_thresh=self.silence_threshold
        )
        if not non_silence_sections:
            print("No no-silent segments detected.")
            return audio_segment
        
        start_time, end_time = non_silence_sections[0][0], non_silence_sections[-1][1]
        extended_end = min(end_time + self.padding_duration, len(audio_segment))
        return audio_segment[start_time:extended_end]
        

    def batch_strip_silence(self):
        '''Process all FALC files in the input directory to remove silence.'''
        flac_files = list(self.input_dir.glob("*.flac"))
        if not flac_files:
            print(f"No flac files found in {self.input_dir}")
            exit()
        self.output_dir_trimmed.mkdir(parents=True, exist_ok=True)
        
        for flac_file in flac_files:
            try:
                audio = AudioSegment.from_file(flac_file, format="flac")
                trimmed_audio = self.strip_silence(audio)
                output_path = self.output_dir_trimmed /flac_file.name
                trimmed_audio.export(output_path, format="flac")
                print(f"Processed silence removal: {flac_file.name} -> {output_path.name}")
            except Exception as e:
                print(f"Error processing {flac_file.name}: {str(e)}")


    def batch_compress_to_mp3(self):
        '''Compress or convert FLAC files to MP3 format.'''
        flac_files = list(self.output_dir_trimmed.glob("*.flac"))
        if not self.output_dir_trimmed.exists() or not flac_files:
            print(f"No trimmed FLAC files found in {self.output_dir_trimmed}. Please run silence_removal first ")
            return 
        self.output_dir_compressed.mkdir(parents=True, exist_ok=True)
        
        for flac_file in flac_files:
            try:
                audio = AudioSegment.from_file(flac_file, format="flac")
                processed_audio = audio.set_frame_rate(self.sample_rate).set_channels(self.channels)
                output_path = self.output_dir_compressed / f"{flac_file.stem}.mp3"
                processed_audio.export(output_path, format="mp3", bitrate=self.bitrate)
                print(f"Converted: {flac_file.name} -> {output_path.name}")
            except Exception as e:
                print(f"Error converting {flac_file.name}: {str(e)}")


    def trim_and_convert_flac(self):
        flac_files = list(self.input_dir.glob("*.flac"))
        if not flac_files:
            print(f"No FLAC file found in {self.input_dir}")
            return
        self.output_dir_final.mkdir(parents=True, exist_ok=True)
        
        for flac_file in flac_files:
            try:
                audio = AudioSegment.from_file(flac_file, format="flac")
                trim_audio = self.strip_silence(audio)
                processed_audio = trim_audio.set_frame_rate(self.sample_rate).set_channels(self.channels)
                output_path = self.output_dir_final / f"{flac_file.stem}.mp3"
                processed_audio.export(output_path, format="mp3", bitrate=self.bitrate)
                print(f"Trim & Compress Convert: {flac_file.name} -> {output_path.name}")
            except Exception as e:
                print(f"Error Compressing and converting {flac_file}: {str(e)}")

    def remove_pngfile(self, source_dir, target_dir):
        png_files = list(self.input_dir.glob("*.png"))
        if not png_files:
            print(f"No png file found in {self.input_dir}")
            return
        
        self.output_dir_final.mkdir(parents=True, exist_ok=True)
        for png_file in png_files:
            output_path = self.output_dir_final / png_file.name
            output_path.write_bytes(png_file.read_bytes())
            print(f"Copied: {png_file} -> {self.output_dir_final}")

class Batch_Modify_Filename:
    def __init__(self, input_folder="media"):
        self.script_dir = Path(__file__).parent
        self.input_folder = input_folder
        self.input_dir = self.script_dir / self.input_folder

    def add_prefix(self, prefix):
        if not self.input_dir.exists():
            print(f"Input directory {self.input_dir} does not exist.")
            exit()
        
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
        if not self.input_dir.exists():
            print(f"Input directory {self.input_dir} does not exist.")
            exit()

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

    flacprocess = FlacProcess(
        input_folder= "OriginalSources",
        sample_rate= 32000,
        bitrate= "128k",
        channels= 1,
        silence_threshold= -50,
        min_silence_duration= 700,
        padding_duration= 300
    )
    
    filename = Batch_Modify_Filename()

    flac_count = flacprocess.count_flac_files()
    print(f"\nfind {flac_count} .flac files in {flacprocess.input_dir}")
    
    
    print("\nAvailable functions:")
    print("1. Remove silence of the beginning and end")
    print("2. Compress Convert FLAC files to MP3")
    print("3. Integrate all process of FLAC files")
    print("4. Add prefix")
    print("5. Delete prefix")
    choice = input("Enter your choice: ")
    
    if choice == "1":
        flacprocess.batch_strip_silence()
    elif choice == "2":
        flacprocess.batch_compress_to_mp3()
    elif choice == "3":
        flacprocess.trim_and_convert_flac()
        flacprocess.remove_pngfile(flacprocess.input_dir, flacprocess.output_dir_final)
        filename.add_prefix(f"{filename.script_dir.name}_")
    elif choice == "4":
        filename.add_prefix(input("Input prefix: "))
    elif choice == "5":
        filename.delete_prefix(input("Input prefix: "))
    else:
        print("Invalid Choice.")




