import numpy as np
import matplotlib.pyplot as plt

# def vec_corrcoef(X, Y):
#     Xm = np.mean(X)
#     Ym = np.mean(Y)
#     num = np.sum((X - Xm) * (Y - Ym))
#     den = np.sqrt(np.sum((X - Xm)**2) * np.sum((Y - Ym)**2))
#     return num / den

def norm(vector):
    return (vector[0]**2 + vector[1]**2)**0.5

N = 20

samples = 5000

speed = 1

out = []
for s in range(samples):

    # # 1D
    # # series = np.random.choice([-1,1], size=N)
    # # series = np.random.choice([1,2,3,4,5,6], size=N)
    # series = np.random.random_sample(size=N)
    # sum_series = np.sum(series)
    # out.append(sum_series)

    # agent.velocity_pub = agent.speed*sum_vel/norm(sum_vel)

    # 2D
    x_series = np.random.random_sample(size=N)*2 -1
    y_series = np.random.random_sample(size=N)*2 -1

    # normalise
    for i in range(len(x_series)):
        vector = np.array([x_series[i], y_series[i]])
        vector = speed*vector/norm(vector)
        x_series[i] = vector[0]
        y_series[i] = vector[1]

    x_sum_series = np.sum(x_series)
    y_sum_series = np.sum(y_series)
    sum_vector = np.array([x_sum_series, y_sum_series])
    # sum_vector = speed*sum_vector/norm(sum_vector)
    out.append(norm(sum_vector))

# plt.hist(out, bins='sqrt')

# mean
mean_out = np.sum(out)/len(out)

# # variance
# diff_out = out - mean_out
# var_out = np.sum(diff_out**2)/len(out)

# # standard deviation
# std_out = np.sqrt(var_out)

# print(mean_out/N)
print(mean_out/(np.sqrt(N)*speed))

# print(std_out/np.sqrt(N))
# # print(np.sqrt(N))

plt.ion()
plt.show()
