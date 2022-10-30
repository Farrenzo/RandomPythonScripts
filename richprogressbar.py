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

console = Console(record=True)
with Progress(
    SpinnerColumn(),
    *Progress.get_default_columns(),
    TimeElapsedColumn(),
    console=console
) as progress:
    for key, value in some_dict.items():
        task = progress.add_task(f"[green]Running {key}", total=value)
        sleeper = 0
        while sleeper != value:
            progress.advance(task, 1)
            sleeper += 1
            time.sleep(1)
