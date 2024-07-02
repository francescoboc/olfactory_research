import multiprocessing as mp
import numpy as np
import random, sys, time

def flip_coin(n):    
    time.sleep(0.1)
    # initialise the random number generator
    seed = random.randrange(sys.maxsize)
    rng = random.Random(seed)
    # do stuff and obtain result
    if rng.random()>0.5: res = 1
    else: res = 0
    return res, seed

# # total number of runs
# n_runs = 100
# # initialise parallel pool
# pool = mp.Pool(processes = 4)
# # initialise empty lists for results
# results, seeds = [], []
# for result in pool.map(flip_coin, range(n_runs)):
#     # save result and the seed that generated that result
#     results.append(result[0])
#     seeds.append(result[1])
# # close parallel pool
# pool.close(); pool.join() 

nproc = 2

times = []
for i in range(10):
    startTime = time.time()

    # desired number of ones
    n_ones = 1e2
    # counter to keep track of the ones
    counter = 0
    # initialise parallel pool
    pool = mp.Pool(processes = nproc)
    # empty list for seeds
    seeds = []
    while counter < n_ones:
        # for result in pool.map(flip_coin, range(int(n_ones))):
        for result in pool.map(flip_coin, range(int(nproc))):
            print('running')
            # if we got a 1, increase counter and save seed
            if result[0] == 1: 
                counter += 1
                seeds.append(result[1])
    # close parallel pool
    pool.close(); pool.join() 

    # limit = 1e6
    # n_ones = 1e2
    # counter = 0
    # results, seeds = [], []
    # pool = mp.Pool(processes = nproc)
    # for res, seed in pool.imap_unordered(flip_coin, range(int(limit))):
    #     if res == 1:
    #         counter += 1
    #         seeds.append(seed)
    #         if counter == n_ones:
    #             break
    # pool.terminate(); pool.join() 

    endTime = time.time()
    elapsedTime = endTime - startTime
    print("Elapsed Time = %s" % elapsedTime)
    times.append(elapsedTime)

print()
print('first method')
# print('second method')
print(np.mean(times))


