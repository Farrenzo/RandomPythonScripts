import os
import cv2
import pickle
import numpy as np
import pandas as pd
from typing import Literal

from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor

from rich.console import Console
from rich.progress import Progress, TimeElapsedColumn, TaskID
console = Console(log_time=True, log_path=False)


@dataclass(order=True)
class ImageData:
    """Dataclass for storing image data."""
    name:       str
    file_path:  str
    file_size:  int
    descriptor: np.ndarray = field(default=None)

    def __post_init__(self):
        object.__setattr__(self, "sort_index", self.name)

    def __str__(self):
        return f"{self.name}"


class ImageComparator:
    """Compare images to get duplicates."""
    def __init__(self, folder_path:str) -> None:
        """folder_path: Path to the folder containing images."""
        self.folders = {
            "meta"   :f"{folder_path}/meta",
            "cache"  :f"{folder_path}/meta/.cache",
        }
        self.create_subfolders(self.folders)
        self.files: dict[str, ImageData] = {}

        file_load = False
        if not os.path.isfile(f"{self.folders['cache']}/image_data.pkl"):
            # Check for albums
            self.folders["images"] = [f"{folder_path}/Images"]
            if "Albums" in os.listdir(folder_path):
                for folder in os.listdir(f"{folder_path}/Albums"):
                    if os.path.isdir(f"{folder_path}/Albums/{folder}"):
                        self.folders["images"] += [f"{folder_path}/Albums/{folder}"]

            for image_folder in self.folders["images"]:
                self.fetch_all_image_files(image_folder)
        else:
            file_load = True
            self.files = self.pickler({}, f"{self.folders['cache']}/image_data.pkl")

        total_pics = len(self.files)
        if total_pics == 0:
            return console.print(f"Found {total_pics} image files.")
        else:
            runs = ((total_pics-1)*total_pics)/2
            console.print(f"Found {total_pics} images. This operation will run {runs:,.0f} times.\n")

        self.pickle_path = f"{self.folders['cache']}/task_queue.pkl"
        self.log_file = f"{self.folders['meta']}/similarities.csv"
        self.log_data = {}

        self.errors: dict[str, ImageData] = {}
        self.prelim_results = {
            "pic1": [],
            "pic2": [],
            "similarity": [],
            "matches": [],
            "size_1": [],
            "size_2": [],
        }

        FLANN_INDEX_KDTREE = 1
        self.sift = cv2.SIFT_create()
        search_params = {"checks":50}
        index_params  = {"algorithm":FLANN_INDEX_KDTREE, "trees":5}
        self.flann = cv2.FlannBasedMatcher(index_params, search_params)

        if not file_load:
            self.read_images()
        self.compare_images()

    def fetch_all_image_files(self, folder_path: str):
        """Gather all images into a list of ImageData objects."""
        self.files.update({
            os.path.join(folder_path, file): ImageData(
                name = file,
                file_path = os.path.join(folder_path, file),
                file_size = os.stat(os.path.join(folder_path, file)).st_size,
            )
            for file in os.listdir(folder_path)
            if file.lower().endswith(
                ('.jpeg', '.jpg', '.png', '.bmp', '.gif')
            )
        })

    def _task_chunker(
        self,
        all_tasks:list,
        function: callable,
        chunk_size:int = 20,
        task_description:str = "task",
    ) -> None:
        """Cut up a list of tasks into manageable chunks and run them concurrently."""
        if chunk_size > os.cpu_count():
            # Chunkc must not exceed available CPU cores.
            raise ValueError("chunk_size is too high. Please reduce it.")

        start = 0
        pickled_tasks = all_tasks.copy()
        total_tasks = len(all_tasks)
        while total_tasks > 0:
            finish = (
                (start + chunk_size) if (start + chunk_size) < len(all_tasks)
                else start + total_tasks
            )
            console.print(f"Working on {task_description} {start} to {finish} of {len(all_tasks)}")
            to_do = all_tasks[start:finish]
            # Set up the progress bar.
            with Progress(
                TimeElapsedColumn(),
                *Progress.get_default_columns(),
                console=console,
            ) as progress:
                with ThreadPoolExecutor(max_workers=chunk_size) as executor:
                    futures = []
                    task = progress.add_task(
                        total = len(to_do),
                        description = task_description,
                    )
                    for item in to_do:
                        futures.append(
                            executor.submit(function, progress, task, item)
                        )
                    for future in futures:
                        future.result()
            start += chunk_size
            total_tasks -= chunk_size
            if function.__name__ == "_comparator":
                self.save_results(
                    log_file_path = self.log_file,
                    pd_log_data = self.prelim_results
                )
                pickled_tasks = [i for i in pickled_tasks if i not in to_do]
                self.pickler(
                    pickled_tasks,
                    self.pickle_path,
                    "wb"
                )

    def _image_reader(self, progress: Progress, task_id: TaskID, image: ImageData) -> None:
        """Reads an image; extracts keypoints and descriptors."""
        img = cv2.imread(image.file_path, cv2.IMREAD_GRAYSCALE)
        if img is not None:
            _, image.descriptor = self.sift.detectAndCompute(img, None)
        else:
            progress.console.print(f"Could not read image: {image.name}")
            self.errors[image.name] = image
        progress.update(task_id = task_id, description=f"Done reading image: {image.name}", advance=1)

    def read_images(self):
        """Read images from a folder."""
        file_list = [image_data for image_path, image_data in self.files.items()]
        self._task_chunker(
            all_tasks = file_list,
            function=self._image_reader,
            task_description=f"reading images:"
        )

        for image in self.errors.keys():
            self.files.pop(image)
        console.log(f"Done reading {len(self.files)} images.")

        self.pickler(
            self.files, 
            f"{self.folders['cache']}/image_data.pkl",
            "wb"
        )

    def _comparator(self, progress: Progress, task_id: TaskID, images: list[ImageData]) -> None:
        """Compare two images using the SIFT algorithm."""
        matches = self.flann.knnMatch(images[0].descriptor, images[1].descriptor, k=2)
        good_matches = [m for m, n in matches if m.distance < 0.7 * n.distance]
        similarity = len(good_matches) / len(matches) if matches else 0

        self.prelim_results["pic1"].append(images[0].file_path)
        self.prelim_results["pic2"].append(images[1].file_path)
        self.prelim_results["similarity"].append(similarity)
        self.prelim_results["matches"].append(len(good_matches))
        self.prelim_results["size_1"].append(images[0].file_size)
        self.prelim_results["size_2"].append(images[1].file_size)

        progress.update(
            advance = 1,
            task_id = task_id,
            description = f"Done {images[0].name} vs {images[1].name} "
        )

    def compare_images(self) -> None:
        """Set up the images for comparison."""
        if not os.path.isfile(self.pickle_path):
            image_tasks: "list[list[ImageData, ImageData]]" = []
            images = [image_path for image_path in self.files.keys()]
            for i in range(len(images)):
                for j in range(i+1, len(images)):
                    image_tasks += [
                        [self.files[images[i]], self.files[images[j]]]
                    ]
            self.pickler(image_tasks, self.pickle_path, "wb")
        else:
            image_tasks = self.pickler({}, self.pickle_path)

        self._task_chunker(
            all_tasks = image_tasks,
            function=self._comparator,
            task_description="comparing images"
        )

    def pickler(self, obj: dict, log_file_path:str, mode: Literal["wb", "rb"] = "rb"):
        """Store temporary data in a pickle file."""
        with open(log_file_path, mode) as pickle_file:
            if mode == "rb":
                return pickle.load(pickle_file)
            else:
                pickle.dump(obj, pickle_file, pickle.HIGHEST_PROTOCOL)

    def save_results(self, pd_log_data: dict, log_file_path:str = None):
        """Save results into a CSV file."""
        df = pd.DataFrame(pd_log_data)
        df.to_csv(log_file_path, index=False)
        console.log(f"Saved comparison results to: {log_file_path}")
    
    def create_subfolders(self, paths: dict):
        for _, path in paths.items():
            if not os.path.isdir(path):
                os.mkdir(path)

## To do:
# - Add a listener for Ctrl+C that will terminate the operation while saving the location.
