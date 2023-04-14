from pydub import AudioSegment
import os
import subprocess
import sys
from pathlib import Path
from subprocess import Popen
from datetime import datetime

split_audio_folder = "raw"  # initialy empty
processed_audio_folder = "results"  # initialy empty
input_file = "htdemucs/base_song/vocals.wav"
output_file = "htdemucs/base_song/vocals.out.wav"

speaker = "mori"
model_path = "models/G_4000.pth"
config_path = "models/config.json"

# num_parts = 8
overlap_seconds = 1
seconds_per_part = 30

def main():
    timestamp = datetime.now()
    split_audio_file(input_file, split_audio_folder, seconds_per_part, overlap_seconds)
    infer_audio_files(split_audio_folder, processed_audio_folder)
    crossfade_audio_files(processed_audio_folder, output_file, overlap_seconds)
    duration = datetime.now() - timestamp
    print(f"Elapsed duration: {duration}")

def split_audio_file(input_file_path, output_folder_path, seconds_per_part, overlap_seconds):
    audio = AudioSegment.from_file(input_file_path)
    audio_length = len(audio)
    num_parts = (audio_length // (seconds_per_part*1000)) + 1
    part_length = audio_length // num_parts
    overlap_length = overlap_seconds * 1000
    for i in range(num_parts):
        start = i * part_length
        end = start + part_length
        start -= overlap_length
        end += overlap_length
        if i == 0:
            start = 0
        if i == num_parts - 1:
            end = audio_length
        part = audio[start:end]
        part.export(os.path.join(output_folder_path, f"part_{i + 1}.wav"), format="wav")

def infer_audio_files(input_folder_path, output_folder_path):
    input_files = sorted(os.listdir(input_folder_path))
    for file_name in input_files:
        args = [
            'svc', 'infer',
            '-s', speaker,
            '-m', model_path,
            '-c', config_path,
            '-o', f"{output_folder_path}\\inf_{file_name}",
            '-fm', 'crepe',
            '--transpose=0',
			'--no-auto-predict-f0',
            f"{input_folder_path}\\{file_name}"
        ]
        p = subprocess.Popen(args)
        p.wait()

def crossfade_audio_files(input_folder_path, output_file_path, overlap_seconds):
    input_files = sorted(os.listdir(input_folder_path))
    combined_audio = AudioSegment.from_file(os.path.join(input_folder_path, input_files[0]))
    for file_name in input_files[1:]:
        part = AudioSegment.from_file(os.path.join(input_folder_path, file_name))
        combined_audio = combined_audio.append(part, crossfade=overlap_seconds * 2 * 1000)
    combined_audio.export(output_file_path, format="wav")

if __name__ == '__main__':
    main()