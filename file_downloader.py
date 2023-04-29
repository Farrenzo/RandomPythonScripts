import time
import aiohttp
import asyncio
import aiofiles

from os import rename
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


class FileDownloader:
    def __init__(self, links:dict, concurrent_downloads:bool=True) -> None:
        """Download files from a dicitonary.

        param links: The files to download.
        type  links: Dict
        param concurrent_downloads: Weather to download one by one or alltogether.
        type  concurrent_downloads: Bool.
        :rtype: Dict
        """
        self.description :str = "[yellow][b]Downloading {0} | {1}[/b] | {2}"
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
                file_info.append(progress.add_task(f"[blue]Queued [b]{file_name}[/b]", total=file_info[2]))

            if concurrent_downloads:
                asyncio.run(self.download_concurrently(progress, download_links))
            else:
                self.download_individually(progress, download_links)

    def _size_notation(self, n:int, np:int = 2) -> str:
        """Return a string showing a number in B/KiB/MiB/GiB format.
        
        Raises ValueError if "n" not in [0, 1PiB).
    
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

    async def _file_downloader(
        self, 
        url:str,
        file_path: str,
        binary_mode: str,
        task_id: TaskID,
        progress: Progress,
        semaphore = asyncio.Semaphore(3),
        header: dict={},
    ) -> None:
        start = time.perf_counter()
        download = 0
        timeout = aiohttp.ClientTimeout(total=3000)
        async with aiohttp.ClientSession(timeout=timeout) as session, semaphore:
            async with session.get(url, headers=header) as response, aiofiles.open(file_path + ".PART", binary_mode) as local_file:
                file_size = response.content_length
                if binary_mode == "ab":
                    file_size += getsize(file_path + ".PART")

                progress.update(
                    task_id,
                    total   = file_size,
                    advance = getsize(file_path + ".PART"),
                )
                async for data in response.content.iter_chunked(KiB):
                    await local_file.write(data)
                    download += len(data)
                    bit_rate = f"{((download//(time.perf_counter() - start)) / MiB):.2f} Mb/s"
                    progress.update(
                        task_id,
                        advance=len(data),
                        description = self.description.format(
                            self._size_notation(response.content_length),
                            file_path[file_path.rfind('/')+1:],
                            bit_rate
                        )
                    )
        progress.update(
            task_id,
            description = "[green][b]Done {0} | {1}[/b] | {2}".format(
                self._size_notation(response.content_length),
                file_path[file_path.rfind('/')+1:],
                bit_rate
            )
        )
        # Clear the part file after completion.
        rename(file_path + ".PART", file_path)

    def download_individually(self, progress: Progress, links:dict) -> None:
        """Downloading files one by one"""
        for _, file_info in links.items():
            asyncio.run(self._file_downloader(
                progress    = progress,
                url         = file_info[0],
                file_path   = file_info[1],
                binary_mode = file_info[3],
                header      = file_info[4],
                task_id     = file_info[5],
            ))

    async def download_concurrently(self, progress: Progress, links:dict) -> None:
        """Download as many files as you set your semaphore to be"""
        await asyncio.gather(
            *(
                self._file_downloader(
                    progress    = progress,
                    url         = file_info[0],
                    file_path   = file_info[1],
                    binary_mode = file_info[3],
                    header      = file_info[4],
                    task_id     = file_info[5],
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

FileDownloader(linky)
