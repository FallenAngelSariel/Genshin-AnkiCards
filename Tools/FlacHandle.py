from pathlib import Path
from pydub import AudioSegment
from pydub.silence import detect_nonsilent

class FlacProcessor:
    VALID_SAMPLE_RATES = {22050, 32000, 44100, 48000}
    VALID_BITRATES = {"32k", "64k", "96k", "128k", "192k", "256k", "320k"}

    def __init__(
        self,
        input_directory,
        output_directory=None,
        sample_rate=32000,
        bitrate="256k",
        channels=1,
        silence_threshold=-50,
        min_silence_duration=500,
        padding_duration=300
    ):
        self.input_dir = Path(input_directory).resolve()
        self.output_dir = self.input_dir.parent if output_directory is None else Path(output_directory)
        self.output_dir_trimmed = self.output_dir / "Trimmed_audio"
        self.output_dir_compressed = self.output_dir / "Compressed_audio"
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
        

    def remove_silence(self, audio_segment):
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
        

    def batch_remove_silence(self):
        '''Process all FALC files in the input directory to remove silence.'''
        flac_files = list(self.input_dir.glob("*.flac"))
        if not flac_files:
            print(f"No FLAC files found in {self.input_dir}")
            return
        self.output_dir_trimmed.mkdir(parents=True, exist_ok=True)
        
        for flac_file in flac_files:
            try:
                audio = AudioSegment.from_file(flac_file, format="flac")
                trimmed_audio = self.remove_silence(audio)
                output_path = self.output_dir_trimmed /flac_file.name
                trimmed_audio.export(output_path, format="flac")
                print(f"Processed silence removal: {flac_file.name} -> {output_path}")
            except Exception as e:
                print(f"Error processing {flac_file.name}: {str(e)}")


    def batch_compress_and_convert(self):
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
                print(f"Converted: {flac_file.name} -> {output_path}")
            except Exception as e:
                print(f"Error converting {flac_file.name}: {str(e)}")

    def batch_trim_and_convert_files(self):
        flac_files = list(self.input_dir.glob("*.flac"))
        if not flac_files:
            print(f"No FLAC file found in {self.input_dir}")
            return
        self.output_dir_compressed.mkdir(parents=True, exist_ok=True)
        
        for flac_file in flac_files:
            try:
                audio = AudioSegment.from_file(flac_file, format="flac")
                trim_audio = self.remove_silence(audio)
                processed_audio = trim_audio.set_frame_rate(self.sample_rate).set_channels(self.channels)
                output_path = self.output_dir_compressed / f"{flac_file.stem}.mp3"
                processed_audio.export(output_path, format="mp3", bitrate=self.bitrate)
                print(f"Trim & Compress Convert: {flac_file.name} -> {output_path}")
            except Exception as e:
                print(f"Error Compressing and converting {flac_file}: {str(e)}")


    @staticmethod
    def run_interactive():
        '''run the processor in interactive mode with user input'''
        script_dir = Path(__file__).parent.resolve()
        
        input_path = input("Enter input path: ").strip()
        if input_path:
            final_input_path = script_dir / input_path / "OriginalVoice"
        else:
            final_input_path = script_dir / "OriginalVoice"
        if not final_input_path.exists():
            print(f"Input directory {final_input_path} does not exist. Exiting.")
            return


        processor = FlacProcessor(
            input_directory= final_input_path,
            sample_rate= 32000,
            bitrate= "128k",
            channels= 1,
            silence_threshold= -50,
            min_silence_duration= 600,
            padding_duration= 300
        )

        flac_count = processor.count_flac_files()
        if flac_count == 0:
            print(f"\nfind {flac_count} .flac files in {final_input_path}. Exit.")
            return 
        print(f"\nfind {flac_count} .flac files in {final_input_path}")


        print("\nAvailable functions:")
        print("1. Remove silence of the beginning and end")
        print("2. Compress and Convert FLAC files to MP3")
        print("3. Trim & Compress Convert FLAC files")
        choice = input("Enter your choice (1 or 2 or 3)\n")

        if choice == "1":
            processor.batch_remove_silence()
            print("\ndone!\n")
        elif choice == "2":
            processor.batch_compress_and_convert()
            print("\ndone!\n")
        elif choice == "3":
            processor.batch_trim_and_convert_files()
            print("\ndone!\n")
        else:
            print("Invalid Choice. Please select 1 or 2 or 3")

if __name__ == "__main__":
    FlacProcessor.run_interactive()














