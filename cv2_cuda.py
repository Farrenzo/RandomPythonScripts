import time

import cv2
from cv2 import cuda, SIFT

pathy = "C:/Documents/Images"
files = [
    "a01.jpg", "a02.jpg", 
    "b01.jpg", "b02.jpg", 
    "c01.jpg", "c02.jpg", 
    "d01.jpg", "d02.jpg", 
    "e01.jpg", "e02.jpg", 
    "f01.jpg", "f02.jpg"
]

start = time.time()
print("Reading images...")
images = {
    file: cv2.imread(f"{pathy}/{file}", cv2.IMREAD_GRAYSCALE) for file in files
}
print(f"Finished at reading images {time.time() - start:.2f} seconds.")

cuda.setDevice(0)
sift = SIFT.create()

upload_time = time.time()
gpu_descriptions: list[cuda.GpuMat] = []
for file in files:
    _, descriptors = sift.detectAndCompute(images[file], None)
    gpu_mat = cuda.GpuMat()
    gpu_mat.upload(descriptors)
    gpu_descriptions+= [gpu_mat]
print(f"Finished at uploading images {time.time() - upload_time:.2f} seconds.")

stream  = cuda.Stream()
matcher = cuda.DescriptorMatcher.createBFMatcher(cv2.NORM_L2)
print("Looping through the matcher...")
for i in range(len(gpu_descriptions)):
    for j in range(i + 1, len(gpu_descriptions)):
        gpu_match = matcher.knnMatchAsync(gpu_descriptions[i], gpu_descriptions[j], k=2, stream=stream)
        stream.waitForCompletion()
        matches = matcher.knnMatchConvert(gpu_match)
        good_matches = [m for m, n in matches if m.distance < 0.7 * n.distance]
        similarity = len(good_matches) / len(matches) if matches else 0
        print(f"Match between {files[i]} and {files[j]}: {similarity:.6f}")

print(f"Finished at matching images {time.time() - start:.2f} seconds.")
