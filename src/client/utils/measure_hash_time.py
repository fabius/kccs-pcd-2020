import time, hashlib, statistics

print("generating list")
# strings with 20 digits
my_strings = [str(i) for i in range(10000000000000000000, 10000000000001000000)]

def measure_time(strings: list) -> float:
    print("measuring")
    start = time.process_time_ns()
    for num in strings:
        hashlib.sha1(num.encode()).hexdigest()
    end = time.process_time_ns() - start
    return end


if __name__ == "__main__":
    timings = [measure_time(my_strings) for i in range(0, 10)]
    average = statistics.median(timings)
    print(f"median of timings: {average} nanoseconds per 1.000.000 hashes"
          f" = {average/1000000}ns per hash")