import time
import aiohttp
import asyncio
import aiofiles

from os import rename
from requests import get
from os.path import exists, getsize

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn, TaskID

import warnings
warnings.simplefilter("ignore")

KiB = 1024
MiB = KiB*KiB
GiB = MiB*MiB
TiB = GiB*GiB
PiB = TiB*TiB
console = Console(record=False)


def _size_notation(n:int, np:int = 2) -> str:
    """Return a string showing a number in B/KiB/MiB/GiB format.
        Raises ValueError if "n" not in [0, 1TiB).
 
    param n: The number to convert.
    type n: Integer
    param np: Number of decimal places. Default = 2.
    type np: Integer
    :rtype: String
    """
    if   n < 0:
        raise ValueError(f"Number must be >= 0.")
    elif n < KiB:
        return f"{n} B"
    elif n < MiB:
        return f"{n/KiB:.{np}f} KB"
    elif n < GiB:
        return f"{n/MiB:.{np}f} MB"
    elif n < TiB:
        return f"{n/GiB:.{np}f} GB"
    elif n < PiB:
        return f"{n/TiB:.{np}f} TB"
    raise ValueError(f"File too large, >= 1 Petabyte ({PiB}).")


def download_files(links:dict, concurrent_downloads:bool=True) -> dict:
    """Download files from a dicitonary.

    param links: The files to download.
    type  links: Dict
    param concurrent_downloads: Weather to download one by one or alltogether.
    type  concurrent_downloads: Bool.
    :rtype: Dict
    """
    download_links = {}
    # Get a proper dictionary of files to download.
    for file_name, file_info in links.items():
        # Make sure file there is a file size to check.
        if len(file_info) < 3: file_info.append(28)
        file_url, file_path, file_size = file_info
        # If file already exists, skip it.
        if exists(file_path) and getsize(file_path) == file_size:
            continue
        # If file was partially downloaded, start with the part file.
        elif exists(file_path + ".PART"):
            part_file = getsize(file_path + ".PART")
            download_links.update(
                {
                    file_name:[
                        file_url,
                        file_path,
                        file_size,
                        "ab",
                        {'Range': f"bytes=-{file_size - part_file}"}
                    ]
                }
            )
        # If file didn't exist before.
        else:
            download_links.update(
                {
                    file_name:[
                        file_url,
                        file_path,
                        file_size,
                        "wb",
                        {}
                    ]
                }
            )

    # Set up the progress bar.    
    with Progress(
        SpinnerColumn(),
        *Progress.get_default_columns(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        for file_name, file_info in download_links.items():
            file_info.append(progress.add_task(f"[green]Queued [b]{file_name}[/b]", total=file_info[2]))

        if concurrent_downloads:
            asyncio.run(download_concurrently(progress, download_links))
        else:
            download_individually(progress, download_links)


def download_individually(progress: Progress, links:dict) -> None:
    """Downloading files one by one"""
    def _file_downloader(
        file_url:str,
        file_path:str,
        binary_mode: str,
        task_id: TaskID,
        header:dict = {},
    ):
        start = time.perf_counter()
        if binary_mode == "ab":
            progress.update(task_id, advance=getsize(file_path))
        with open(file_path, binary_mode) as local_file, get(file_url, stream=True, headers=header) as remote_file:
            download = 0
            progress.update(total=int(remote_file.headers['Content-length']))
            for chunk in remote_file.iter_content(chunk_size=KiB):
                local_file.write(chunk)
                download += len(chunk)
                bit_rate = f"{((download//(time.perf_counter() - start)) / MiB):.2f} Mb/s"
                progress.update(
                    task_id,
                    advance=len(chunk),
                    description=(
                            f"[green][b]Downloading {_size_notation(int(remote_file.headers['Content-length']))} | " 
                           +f"{file_path[file_path.rfind('/')+1:]}[/b] | {bit_rate}"
                        )
                )

    for _, file_info in links.items():
        file_url, file_path, file_size, write_mode, header, task_id = file_info
        _file_downloader(
            file_url=file_url,
            file_path = file_path + ".PART",
            binary_mode=write_mode,
            task_id=task_id,
            header=header
        )
        rename(file_path + ".PART", file_path)


async def download_concurrently(progress: Progress, links:dict) -> None:
    async def _async_downloader(
        url:str,
        header: dict,
        file_path: str,
        binary_mode: str,
        task_id: TaskID,
        semaphore: asyncio.Semaphore,
    ) -> None:
        start = time.perf_counter()
        if binary_mode == "ab":
            progress.update(task_id, advance=getsize(file_path + ".PART"))
        download = 0
        timeout = aiohttp.ClientTimeout(total=3000)
        async with aiohttp.ClientSession(timeout=timeout) as session, semaphore:
            async with session.get(url, headers=header) as response, aiofiles.open(file_path + ".PART", binary_mode) as local_file:
                ## TO DO: Update progress bar to size of full download.
                async for data in response.content.iter_chunked(KiB):
                    await local_file.write(data)
                    download += len(data)
                    bit_rate = f"{((download//(time.perf_counter() - start)) / MiB):.2f} Mb/s"
                    progress.update(
                        task_id,
                        advance=len(data),
                        description=(
                            f"[green][b]Downloading {_size_notation(response.content_length)} | " 
                           +f"{file_path[file_path.rfind('/')+1:]}[/b] | {bit_rate}"
                        )
                    )
        # Clear the part file after completion.
        rename(file_path + ".PART", file_path)

    semaphore = asyncio.Semaphore(2)
    await asyncio.gather(
        *(
            _async_downloader(
                url = file_info[0],
                semaphore = semaphore,
                file_path = file_info[1],
                binary_mode = file_info[3],
                header = file_info[4],
                task_id = file_info[5],
            ) for _, file_info in links.items()
        )
    )


linky = {
    "totes_not_a_virus.nickelback.mp3.exe": [
        "https://www.thisisamericanwebsite.ru",
        "C:/WINDOWS/ARE/YOU/PAYING/ATTENTION/SYSTEM32/totes_not_a_virus.nickelback.mp3.exe",
        42069
    ]
}

download_files(linky)
# Notes: the size of the progress bar does not update itself to
# the size of the full download if a .PART file exists. We need
# to get the size of the full file, and the part file, and update
# the progress bar accordingly.
