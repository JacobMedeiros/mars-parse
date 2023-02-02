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
                # If entry has number, i.e. 01. Bass Drum, omit number
                name = entry.name.split(' ')
                if re.search('[0-9]', name[0]) and len(name)>1:
                    drum = True
                    entry_name = ' '.join(name[1:])
                else:
                    entry_name = entry.name
                print('\t' *(i+1) + f'Copying {entry_name}')
                inner_dest_dir = os.path.join(dest_dir, entry_name)
                recursive_copy(entry.path, inner_dest_dir, progress, i+1, notes=notes, drum=drum)

            elif entry.is_file():
                src_path = os.path.join(src_dir, entry.name)
                wav_name = entry.name
                if not drum:
                    for note in notes:
                        if re.search(f'{note.upper()}[0-7]', wav_name):
                            shutil.copy(src_path, dest_dir)
                elif re.search('.DS_Store', wav_name) is None:
                    shutil.copy(src_path, dest_dir)

@app.command()
def main(src_dir: str = typer.Argument(..., help='Source directory of Pack'), 
         dest_dir: str = typer.Argument(..., help='Destination of parsed wav pack'),
         notes: Optional[List[str]] = typer.Argument(None, help='Note(s) to copy')):
    wav_path = ''
    with Progress(SpinnerColumn(), TextColumn('[progress.description]{task.description}'), transient=True) as progress:
        with os.scandir(src_dir) as packs:
            # Find wav path
            for pack in packs:
                pack_dest = os.path.join(dest_dir, pack.name)
                print(f'Copying {pack.name}')
                if not os.path.exists(pack_dest):
                    os.mkdir(pack_dest)
                with os.scandir(pack.path) as entries:
                    for entry in entries:
                        if entry.name.lower() == 'wav' and entry.is_dir():
                            drum = False
                            wav_path = entry.path
                            with os.scandir(wav_path) as wav_entries:
                                for wav_entry in wav_entries:
                                    if re.search('individual', wav_entry.name.lower()):
                                        drum = True
                                        wav_path = wav_entry.path

                            recursive_copy(wav_path, pack_dest, progress=progress, i=0, notes=notes, drum = drum)


    

def run() -> None:
    app()