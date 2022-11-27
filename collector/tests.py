

def list_split(listA, n):
    for x in range(0, len(listA), n):
        every_chunk = listA[x: n+x]

        if len(every_chunk) < n:
            every_chunk = every_chunk + [None for y in range(n-len(every_chunk))]
        yield every_chunk
import numpy as np

listA = [11, 18, 19, 21, 29]

splits = np.array_split(listA, 3)

for array in splits:
    print(list(array))
# Create your tests here.
