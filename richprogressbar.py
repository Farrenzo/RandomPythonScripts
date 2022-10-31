import time
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn

some_dict = {
    "down_01":16,
    "down_02":14,
    "down_03":12,
    "down_04":33,
    "down_05":36,
    "down_06":38,
    "down_07":17,
    "down_08":41,
    "down_09":44,
    "down_10":24,
}

def syncronous_run(data_dict:dict) -> None:
    """Will take 4 mins 35 seconds (275) to complete."""
    console = Console(record=True)
    with Progress(
        SpinnerColumn(),
        *Progress.get_default_columns(),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        tasks = {key:progress.add_task(f"[green]Running {key}", total=value)
            for key, value in data_dict.items()
        }
        # Runs one by one, but each advances once in turns
        # while not progress.finished:
        #     for key, value in data_dict.items():
        #         if progress._tasks[tasks[key]].completed != progress._tasks[tasks[key]].total:
        #             progress.advance(tasks[key], 1)
        #             time.sleep(1)
        
        # Runs one task after the other.
        for key, value in data_dict.items():
            while progress._tasks[tasks[key]].completed != progress._tasks[tasks[key]].total:
                progress.advance(tasks[key], 1)
                time.sleep(1)

syncronous_run(data_dict=some_dict) #00:04:35

import asyncio
async def asynch_advance(progress: Progress, task_id: int) -> None:
    while progress._tasks[task_id].completed != progress._tasks[task_id].total:
        progress.update(task_id, advance=1)
        await asyncio.sleep(1)

async def asynchronous_run(dict_to_run: dict) -> None:
    console = Console(record=False)
    with Progress(
        SpinnerColumn(),
        *Progress.get_default_columns(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        tasks = {
            key:progress.add_task(f"[green]Running [b]{key}[/b]", total=value)
                for key, value in dict_to_run.items()
        }
        await asyncio.gather(*(
            asynch_advance(progress, task_id) for task_name, task_id in tasks.items()
        ))
    
start = time.perf_counter()
asyncio.run(asynchronous_run(dict_to_run=dict_165))
finish = time.perf_counter()
print(f"Done in {finish - start} seconds.")
