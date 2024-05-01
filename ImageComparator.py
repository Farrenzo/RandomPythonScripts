import os
import json
import pickle
import numpy as np
import pandas as pd
from typing import Literal

import cv2
from cv2 import cuda

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, Future

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
    gpu_mat:    cuda.GpuMat = field(default=None)

    def __post_init__(self):
        object.__setattr__(self, "sort_index", self.name)

    def __str__(self):
        return f"{self.name} | {self.file_size}"


class ImageComparator:
    """Compare images to get duplicates."""
    def __init__(self, folder_path:str, use_cuda: bool = True) -> None:
        """folder_path: Path to the folder containing images."""
        self.folders = {
            "meta"   :f"{folder_path}/meta",
            "cache"  :f"{folder_path}/meta/.cache",
        }
        self.create_subfolders(self.folders)
        self.files: dict[str, ImageData] = {}
        self.log_data = {}
        self.log_file = f"{self.folders['meta']}/similarities"
        self.image_data_pkl: str = f"{self.folders['cache']}/image_data.pkl"
        self.task_queue_pkl: str = f"{self.folders['cache']}/task_queue.pkl"

        self.file_load = False
        if not os.path.isfile(self.image_data_pkl):
            # Check for albums
            self.folders["images"] = [f"{folder_path}/Images"]
            if "Albums" in os.listdir(folder_path):
                for folder in os.listdir(f"{folder_path}/Albums"):
                    if os.path.isdir(f"{folder_path}/Albums/{folder}"):
                        self.folders["images"] += [f"{folder_path}/Albums/{folder}"]

            for image_folder in self.folders["images"]:
                self.fetch_all_image_files(image_folder)
        else:
            self.file_load = True
            self.files = self.pickle_and_save({}, self.image_data_pkl)

        total_pics = len(self.files)
        if total_pics == 0:
            return console.print(f"Found {total_pics} image files.")
        else:
            runs = ((total_pics-1)*total_pics)/2
            console.print(f"Found {total_pics} images. This operation will run {runs:,.0f} times.\n")

        self.errors: dict[str, ImageData] = {}
        self.prelim_results: dict[str, list] = {
            "pic1": [],
            "pic2": [],
            "similarity": [],
            "matches": [],
            "size_1": [],
            "size_2": [],
        }

        FLANN_INDEX_KDTREE = 1
        self.sift = cv2.SIFT.create()
        self.use_cuda = use_cuda
        if self.use_cuda:
            cuda.setDevice(0)
            self.stream  = cuda.Stream()
            self.matcher = cuda.DescriptorMatcher.createBFMatcher(cv2.NORM_L2)
        else:
            search_params = {"checks":50}
            index_params  = {"algorithm":FLANN_INDEX_KDTREE, "trees":5}
            self.flann    = cv2.FlannBasedMatcher(index_params, search_params)

    def run_all(self):
        if not self.file_load:
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

    def _task_runner(
        self,
        all_tasks:list,
        function: callable,
        chunk_size:int = 20,
        task_description:str = "task",
        quarterly:bool = False
    ) -> None:
        """Cut up a list of tasks into manageable chunks and run them concurrently."""
        if chunk_size > os.cpu_count():
            # Chunk must not exceed available CPU cores.
            raise ValueError("chunk_size is too high. Please reduce it.")

        if quarterly:
            self.quarters = [25, 50, 75, 100]
            self.task_runner = all_tasks
        total_tasks = len(all_tasks)
        # Set up the progress bar.
        with Progress(
            TimeElapsedColumn(),
            *Progress.get_default_columns(),
            console=console,
        ) as progress, ThreadPoolExecutor(max_workers=chunk_size) as executor:
                futures: list[Future] = []
                task = progress.add_task(
                    total = total_tasks,
                    description = task_description,
                )
                for item in all_tasks:
                    futures.append(
                        executor.submit(function, progress, task, item, quarterly)
                    )
                for future in futures:
                    future.result()

    def _image_reader(self, progress: Progress, task_id: TaskID, image: ImageData, quarterly:bool = False) -> None:
        """Reads an image; extracts keypoints and descriptors."""
        img = cv2.imread(image.file_path, cv2.IMREAD_GRAYSCALE)
        if img is not None:
            _, image.descriptor = self.sift.detectAndCompute(img, None)
        else:
            progress.console.print(f"Could not read image: {image.name}")
            self.errors[image.name] = image
        progress.update(task_id = task_id, description=f"Done reading image: {image.name}", advance=1)
        if quarterly:
            current_percentage = progress.tasks[task_id].completed / progress.tasks[task_id].total * 100
            if self.quarters and current_percentage >= self.quarters[0]:
                self.quarters.pop(0)
                self.pickle_and_save(self.files, self.image_data_pkl, "wb")

    def read_images(self):
        """Read images from a folder."""
        file_list = [image_data for _path, image_data in self.files.items()]
        self._task_runner(
            all_tasks = file_list,
            function=self._image_reader,
            task_description=f"reading images:",
            quarterly = True
        )
        for image in self.errors.keys():
            self.files.pop(image)
        self.pickle_and_save(self.files, self.image_data_pkl, "wb")
        console.log(f"Done reading {len(self.files)} images.")

    def _comparator(
        self,
        progress: Progress,
        task_id: TaskID,
        images: list[ImageData],
        quarterly:bool = False
    ) -> None:
        """Compare two images using the SIFT algorithm."""
        if not self.use_cuda:
            matches = self.flann.knnMatch(images[0].descriptor, images[1].descriptor, k=2)
        else:
            matches = self.matcher.knnMatchAsync(images[0].gpu_mat, images[1].gpu_mat, k=2)
            self.stream.waitForCompletion()
            matches = self.matcher.knnMatchConvert(matches)

        good_matches = [m for m, n in matches if m.distance < 0.7 * n.distance]
        similarity = len(good_matches) / len(matches) if matches else 0
        self.prelim_results["pic1"].append(images[0].file_path)
        self.prelim_results["pic2"].append(images[1].file_path)
        self.prelim_results["similarity"].append(f"{similarity:.6f}")
        self.prelim_results["matches"].append(len(good_matches))
        self.prelim_results["size_1"].append(images[0].file_size)
        self.prelim_results["size_2"].append(images[1].file_size)

        progress.update(advance = 1, task_id = task_id,
            description = f"Done {images[0].name} vs {images[1].name}"
        )
        self.task_runner.remove(images)
        if quarterly:
            current_percentage = progress.tasks[task_id].completed / progress.tasks[task_id].total * 100
            if self.quarters and current_percentage >= self.quarters[0]:
                self.quarters.pop(0)
                self.pickle_and_save(self.prelim_results, self.log_file, "wb", "json")
                if not self.use_cuda:
                    self.pickle_and_save(self.task_runner, self.task_queue_pkl, "wb")

    def compare_images(self) -> None:
        """Set up the images for comparison."""
        image_tasks: "list[list[ImageData, ImageData]]" = []
        images = [image_path for image_path in self.files.keys()]

        if not self.use_cuda:
            if not os.path.isfile(self.task_queue_pkl):
                for i in range(len(images)):
                    for j in range(i+1, len(images)):
                        image_tasks += [
                            [self.files[images[i]], self.files[images[j]]]
                        ]
                self.pickle_and_save(image_tasks, self.task_queue_pkl, "wb")
            else:
                image_tasks = self.pickle_and_save({}, self.task_queue_pkl)
        else:
            for _, image_data in self.files.items():
                gpu_mat = cuda.GpuMat()
                gpu_mat.upload(image_data.descriptor)
                image_data.gpu_mat = gpu_mat
                # Cannot pickle the GpuMat object.
                image_data.descriptor = None

            for i in range(len(images)):
                for j in range(i + 1, len(images)):
                    image_tasks += [
                        [self.files[images[i]], self.files[images[j]]]
                    ]

        self._task_runner(
            all_tasks = image_tasks,
            function=self._comparator,
            task_description="comparing images",
            quarterly = True
        )
        self.pickle_and_save(self.prelim_results, self.log_file, "wb", "json")
        self.pickle_and_save(self.prelim_results, self.log_file, "wb", "csv")

    def pickle_and_save(
        self,
        log_obj: dict,
        log_file_path:str,
        mode:   Literal["wb", "rb"]       = "rb",
        option: Literal["pickle", "csv", "json"] = "pickle"
    ) -> None:
        """Store temporary data in a pickle file."""
        if option == "pickle":
            with open(log_file_path, mode) as pickle_file:
                if mode == "rb":
                    return pickle.load(pickle_file)
                else:
                    pickle.dump(log_obj, pickle_file, pickle.HIGHEST_PROTOCOL)
                    console.log(f"Saved image data to: {log_file_path}")
        if option == "json":
            """Save results into a CSV file."""
            with open(f"{log_file_path}.json", "w") as json_file:
                json.dump(log_obj, json_file, indent=4, sort_keys=True)
        if option == "csv":
            df = pd.DataFrame(log_obj)
            df.to_csv(f"{log_file_path}.csv", index=False)
            console.log(f"Saved comparison results to: {log_file_path}")
    
    def create_subfolders(self, paths: dict):
        for _, path in paths.items():
            if not os.path.isdir(path):
                os.mkdir(path)
