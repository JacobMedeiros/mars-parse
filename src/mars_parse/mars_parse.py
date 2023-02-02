#!/usr/bin/env python
import os
import re
import typer
from typing import List, Optional
from rich.progress import Progress, SpinnerColumn, TextColumn
import shutil

app = typer.Typer()

def recursive_copy(src_dir, dest_dir, progress, i=0, *, notes=['C'], drum=False):
    """
    This is the core function that recursively copies all files of given notes. Maintains hierachy.
    Inputs:
        scr_dir (str):      Source directory path of copy  
        dest_dir (str):     Directory path to copy to 
        progress (rich.progress.Progress):      Progress object to pass through
        i        (int):     Iterable for tracking tabs
        notes    (list(str)):   List of notes to regex search
    Returns:
        None
    """
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)
    with os.scandir(src_dir) as entries:
        for entry in entries:
            if entry.is_dir():
                # Update progress bar
                progress.add_task(description=(' ' *i + f'Copying {entry.name}'), total=None)
                inner_dest_dir = os.path.join(dest_dir, entry.name)
                recursive_copy(entry.path, inner_dest_dir, progress, i+1, notes=notes, drum=drum)

            elif entry.is_file():
                src_path = os.path.join(src_dir, entry.name)
                wav_name = entry.name
                if not drum:
                    for note in notes:
                        if re.search(f'_{note.upper()}[0-7]', wav_name):
                            shutil.copy(src_path, dest_dir)
                else:
                    shutil.copy(src_path, dest_dir)

@app.command()
def main(src_dir: str = typer.Argument(..., help='Source directory of Pack'), 
         dest_dir: str = typer.Argument(..., help='Destination of parsed wav pack'),
         notes: Optional[List[str]] = typer.Argument(None, help='Note(s) to copy'),
         drum: bool = typer.Option(False, help="Pack is drum machine, copy all individual hits")):
    wav_path = ''
    with os.scandir(src_dir) as entries:
        # Find wav path
        for entry in entries:
            if entry.name.lower() == 'wav' and entry.is_dir():
                wav_path = entry.path
                break
        # Now create list of all directories
        print(wav_path)

    # Drum machine file structure is different
    if drum:
        with os.scandir(wav_path) as entries:
            # Find individual Drum Hits
            for entry in entries:
                if re.search('individual', entry.name.lower()):
                    wav_path = os.path.join(wav_path, entry.name)

    # Now iterate through all files and copy specified notes
    with Progress(SpinnerColumn(), TextColumn('[progress.description]{task.description}'), transient=True) as progress:
            recursive_copy(wav_path, dest_dir, progress=progress, i=0, notes=notes, drum =drum)
    print(drum)
    

def run() -> None:
    app()