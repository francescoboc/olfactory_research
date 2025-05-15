import matplotlib.pyplot as plt
import importlib
from utils import *

def create_subplot_grid(row_count, col_count, figure_creators, trust_values, ):
    # Check that the number of columns matches the length of trust_values
    if len(trust_values) != col_count:
        raise ValueError("Number of trust values must match the number of columns.")
    
    # Check that the number of rows matches the length of figure_creators
    if len(figure_creators) != row_count:
        raise ValueError("Number of figure creators must match the number of rows.")

    # Create the figure with specified size (adjusted for visual clarity)
    fig = plt.figure(figsize=(col_count * 2.5, row_count * 2.5))

    # Use gridspec for more control over the layout, with extra space for colorbars
    gs = fig.add_gridspec(row_count, col_count + 1, width_ratios=[1] * col_count + [0.05])

    # Create axes for subplots and a separate axis for colorbars
    axes = [[fig.add_subplot(gs[row_idx, col_idx]) for col_idx in range(col_count)] for row_idx in range(row_count)]
    color_axes = [fig.add_subplot(gs[row_idx, -1]) for row_idx in range(row_count)]  # Colorbar axis

    # Generate the subplots
    for row_idx, creator in enumerate(figure_creators):
        for col_idx, trust in enumerate(trust_values):
            ax = axes[row_idx][col_idx]
            _, _ = creator(ax, trust, colormaps[row_idx], clims[row_idx])  # Generate the plot 
            
            # Remove unnecessary ticks and labels for cleaner layout
            if row_idx != row_count - 1:  ax.tick_params(labelbottom=False)
            else: ax.set_xlabel('x')  
            if col_idx != 0:  ax.tick_params(labelleft=False)
            else: ax.set_ylabel('y')  

        # Add colorbars
        sm = plt.cm.ScalarMappable(cmap=plt.colormaps[colormaps[row_idx]])
        sm.set_clim(*clims[row_idx])
        cbar = plt.colorbar(sm, cax=color_axes[row_idx], label=labels[row_idx]) 

        if row_idx==0:
            current_ticks = cbar.get_ticks()  # Get existing ticks
            print(current_ticks)

            if 0.0 in current_ticks:
                current_ticks = np.delete(current_ticks, 0)
                current_ticks = np.delete(current_ticks, -1)
                updated_ticks = np.append(current_ticks, 1.0) 
                cbar.set_ticks(updated_ticks)  # Set the updated ticks
            print(updated_ticks)

    plt.tight_layout()  
    show_and_check_ipython()

# Trust values for each row
trust_values = [0.1, 0.3, 0.5, 0.7, 0.9]

# Plotting script files
scripts = ['plot_first_passage', 'plot_successrate']

# Dynamically import the plot function from each script
creators = [importlib.import_module(script).create_plot for script in scripts]

# we need the min and max FPT from lowest trust plot in order to have a consistent colormap
dummy_fig, dummy_ax = plt.subplots()
min_fpt, max_fpt = creators[0](dummy_ax, trust_values[0], 'viridis', (0,1))
plt.close(dummy_fig)

colormaps = ['plasma', 'cividis']
labels = ['Average normalised FPT', 'Average succcess rate']
clims=[(1, max_fpt), (0.0, 1.0)]

# Create a grid with one row for each trust value and one column for each creator
create_subplot_grid(len(creators), len(trust_values), creators, trust_values)
