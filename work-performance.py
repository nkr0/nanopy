import timeit, nanopy

print(
    timeit.timeit('nanopy.work_generate("0" * 64)', globals=globals(), number=100) / 100
)
