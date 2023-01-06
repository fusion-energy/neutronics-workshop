import numpy as np 
import matplotlib.pyplot as plt

def create_xy_array(number_of_points):
    return (np.random.rand(2*number_of_points).reshape(-1,2) *2)-1

def plot_circle(xy):
    if len(xy) > 5000: 
        raise ValueError("Be aware of using large arrays for plotting. This function prevents the use of arrays larger then n=5000 to prevent you crashing your computer.")
    fig = plt.figure(figsize=(10,10))
    for i in range(xy.shape[0]):
        if np.sqrt(xy[i,0]**2+xy[i,1]**2) >1:
            color = 'b' 
        else: 
            color = 'r'
        plt.plot(xy[i,0], xy[i,1], f'{color}o')
        plt.xlabel("X-coordinate")
        plt.ylabel("Y-coordinate")
    return

def calculate_pi(xy): 
    r = np.sqrt(xy[:,0]**2+xy[:,1]**2)
    print(f"For {len(xy):2e} data points, $\pi$ has been estimated as: {round(4*(sum(r<1)/len(xy)),5)}")

def calculate_scatter_angle(current_angle, scatter_angle_mean, scatter_angle_width, distribution='uniform'):
    if distribution == 'uniform': 
        scatter_angle = scatter_angle_mean + np.random.uniform(scatter_angle_mean -  scatter_angle_width, scatter_angle_mean + scatter_angle_width)
    elif distribution == 'gauss': 
        scatter_angle = scatter_angle_mean + np.random.normal(scatter_angle_mean -  scatter_angle_width, scatter_angle_mean + scatter_angle_width)
    return scatter_angle+current_angle

def calculate_step(scatter_angle): 
    x_step = np.cos(scatter_angle)
    y_step = np.sin(scatter_angle)
    print(scatter_angle, x_step, y_step)
    return x_step, y_step

def calculate_scatter_event(current_angle, scatter_angle_mean, scatter_angle_width, mean_free_path, mean_free_path_width, distribution='uniform'): 
    new_angle = calculate_scatter_angle(current_angle, scatter_angle_mean, scatter_angle_width, distribution)
    if distribution == 'uniform': 
        scatter_length = np.random.uniform(mean_free_path-mean_free_path_width, mean_free_path+mean_free_path_width)
    elif distribution == 'gauss': 
        scatter_length = np.random.normal(mean_free_path-mean_free_path_width, mean_free_path+mean_free_path_width)
    x_step, y_step = calculate_step(new_angle)
    return x_step, y_step, scatter_length, new_angle

def calculate_scatter_angle(current_angle, scatter_angle_mean, scatter_angle_width, distribution='uniform'):
    if distribution == 'uniform': 
        scatter_angle = scatter_angle_mean + np.random.uniform(scatter_angle_mean -  scatter_angle_width, scatter_angle_mean + scatter_angle_width)
    elif distribution == 'gauss': 
        scatter_angle = scatter_angle_mean + np.random.normal(scatter_angle_mean -  scatter_angle_width, scatter_angle_mean + scatter_angle_width)
    return scatter_angle+current_angle

def calculate_step(scatter_angle): 
    x_step = np.cos(np.deg2rad(scatter_angle))
    y_step = np.sin(np.deg2rad(scatter_angle))
    return x_step, y_step

def calculate_scatter_length(path, width): 
    if width == 0: return path 
    else: 
        width = np.random.randint(path-width, path+width)
        if width <= 1: 
            return 1
        else:
            return width

def calculate_scatter_event(current_angle, scatter_angle_mean, scatter_angle_width, mean_free_path, mean_free_path_width, distribution='uniform'): 
    new_angle = calculate_scatter_angle(current_angle, scatter_angle_mean, scatter_angle_width, distribution)
    scatter_length = calculate_scatter_length(mean_free_path, mean_free_path_width)
    x_step, y_step = calculate_step(new_angle)
    return x_step, y_step, scatter_length, new_angle

def create_particle_track(track_lifetime, scatter_angle_mean, scatter_angle_width, mean_free_path, mean_free_path_width, distribution_type): 
    x = [0] 
    y = [0]
    scatter_length, x_step, y_step, current_angle = mean_free_path, 1, 0, 0
    for i in range(track_lifetime): 
        if scatter_length == 0: 
            x_step, y_step, scatter_length, current_angle = calculate_scatter_event(current_angle, scatter_angle_mean, scatter_angle_width, mean_free_path, mean_free_path_width, distribution=distribution_type)
        x.append(x[-1]+x_step)
        y.append(y[-1]+y_step)
        scatter_length -= 1
    return np.stack((np.array(x), np.array(y)), axis=1)

def plot_track(track): 
    if not isinstance(track, list): 
        track = [track]
    
    fig = plt.figure(figsize=(10,10))
    for i in range(len(track)):
        plt.plot(track[i][:,0], track[i][:,1], label =f"Track {i+1}")
    #plt.legend()
    plt.ylabel("Y-Coordinate")
    plt.xlabel("X-Coorsinate")
    return