from math import *
from numpy import *
import sys
import matplotlib.pyplot as plt
import scipy.interpolate as spl
import random as rnd

##############################################################################
# CONSTANTS AND SIMULATION PARAMETERS
##############################################################################

# 'led_list' contains LED parameters [center wavelength, FWHM] for
# parts available in our range of interest; most of these are from
# from Roithner. This is essentially a template from which all of
# the 'chromosomes' will be derived for an initial population. Later on,
# the length of this list and hence the chromosomes may be varied by an
# outer algorithm that is separately optimizing for an acceptable
# spectral distribution with a minimum number of LEDs. Because the
# chromosomes will only contain the relative brightness value for
# each different LED, we will need to index into this list to get
# the center wavelength and FWHM when performing the fitness calculations.

led_list = array([
[350, 15],
[355, 15],
[360, 15],
[365, 15],
[370, 15],
[375, 15],
[385, 15],
[390, 15],
[395, 15],
[400, 15],
[405, 15],
[410, 15],
[415, 15],
[430, 25],
[450, 25],
[470, 30],
[490, 30],
[505, 30],
[525, 30],
[545, 40],
[565, 30]
], float)

# Constant simulation parameters
pop_size = 100               # Population size, must be a multiple of 4
pop_size = 4 * int(round(pop_size/4))    # Just in case...
num_gen = 50                # Number of generations
mut_rate = 0.2              # Mutation probability
mut_max_init = 0.3          # Initial maximum allowable mutation
wl_min = 350.0              # Minimum wavelength considered
wl_incr = 2.0               # Wavelength increment
wl_max = 550.0 + wl_incr    # Maximum wavelength considered
index_max = int((wl_max - wl_min)/wl_incr)
led_qty = len(led_list)     # Number of genes in each chromosome
mode = 1                    # 1-linear flat, 2-linear sloped, 3-not linear
rnd.seed(0)               # Provide seed in order to produce same random sequence every time

##############################################################################
# FUNCTIONS
##############################################################################

# 'fn_gaussian' calculates the relative power output from a given LED
# at a specified wavelength.
def fn_gaussian(wl,led,z):
    b = led[0]
    fwhm = led[1]
    x = wl
    a = z
    c = fwhm/sqrt(8*log(2))
    return a*exp(-((x-b)**2)/(2*c**2))

# 'fn_fitness' iterates through a given spectral distribution and
# calculates a net fitness value.
def fn_fitness(dist,target):
    y = 0.0
    index = 0
    while index < index_max:
        y = y + (dist[index] - target[index])**2
        index = index + 1
    return y

# 'fn_sort_by_fitness' sorts a population of chromosomes by their calculated
# fitness with the most fit at the head of the list. Returns a dictionary
# containing arrays holding the sorted chromosones and fitness values.
def fn_sort_by_fitness(pop, fit):
    temp_pop = zeros((pop_size, led_qty), dtype=float)
    temp_fit = zeros(pop_size, dtype=float)
    
    for j in range((pop_size-1), -1, -1):
        m = argmax(fit)
        temp_pop[j] = pop[m]
        temp_fit[j] = fit[m]
        
        fit[m] = -1
    return {'pop':temp_pop, 'fit':temp_fit}

# 'fn_distribution' calculates the spectral distribution for a chromosome
# by summing the contributions from each LED in led_list.
def fn_distribution(chromosome):
    dist = zeros_like(wl)
    k = 0
    for gene in chromosome:
        index = 0
        while index < index_max:
            brightness = fn_gaussian(wl[index],led_list[k],gene)
            dist[index] = dist[index] + brightness
            index = index + 1
        k = k + 1
    return dist

# 'fn_pair_selection' uses a cost weighted random pairing method to
# select mating pairs from the pool of surviving chromosomes
def fn_pair_selection(cost):
    # Use the fitness value to compute a normalized cost for each chromosome.
    norm_cost = zeros(pop_size, dtype=float)
    for j in range(pop_size/2):
        norm_cost[j] = cost[j] - cost[pop_size/2]
    
    # Use the normalized costs to compute a mating probability for
    # each chromosome.
    mating_prob = zeros(pop_size, dtype=float)
    sum_cost = 0.0
    for j in range(pop_size/2):
        sum_cost = sum_cost + norm_cost[j]
    for j in range(pop_size/2):
        if abs(sum_cost) > 0.0:
            mating_prob[j] = abs(norm_cost[j] / sum_cost)
        else:
            print
            print "Simulation halted, results will not improve any further."
            # Plot the final generation in a separate subplot.
            sd = fn_distribution(current_gen[0])
            subplot = 2
            fn_add_plot(subplot, wl, sd)
            plt.show()
            sys.exit()
    
    # Compute a cumulative mating probability for each chromosome.
    cum_prob = zeros(pop_size, dtype=float)
    for j in range(pop_size/2):
        k = 0
        while k <= j:
            cum_prob[j] = cum_prob[j] + mating_prob[k]
            k = k + 1
    
    # Create a list of unique mating pairs
    pairs = -1 * ones((pop_size/4, 2), int)
    for j in range(pop_size/4):
        num_selected = 0
        while num_selected < 2:
            threshold = rnd.random()
            for k in range(pop_size/2):
                if cum_prob[k] >= threshold:
                    if k not in pairs[j]:
                        pairs[j,num_selected] = k
                        num_selected = num_selected + 1
                    else:
                        pass
                    break
    return pairs

# 'fn_crossover_1 does a simple 1-point crossover.  It accepts arrays
# containing the current generation of chromosome and the indices to
# the chromosomes for mating pairs. It returns an array containing the
# chromosomes for the resulting offspring.
def fn_crossover_1(pop, pairs):
    offspring_temp = zeros((pop_size/2, led_qty), dtype=float)
    parent_1 = zeros(led_qty, dtype=float)
    parent_2 = zeros(led_qty, dtype=float)
    child_1 = zeros(led_qty, dtype=float)
    child_2 = zeros(led_qty, dtype=float)
    
 
    for j in range(pop_size/4):
        parent_1 = pop[pairs[j,0]]
        parent_2 = pop[pairs[j,1]]
        crosspoint = int(rnd.random() * led_qty)
        beta = rnd.random()
        
        for k in range(0, crosspoint+1):
            child_1[k] = parent_1[k]
            child_2[k] = parent_2[k]
        
        for k in range(crosspoint+1, led_qty):
            child_1[k] = parent_2[k]
            child_2[k] = parent_1[k]
        
        # For Blending
        child_1[crosspoint] = parent_1[crosspoint] - beta*(parent_1[crosspoint] - parent_2[crosspoint])
        child_2[crosspoint] = parent_2[crosspoint] + beta*(parent_1[crosspoint] - parent_2[crosspoint])
            
        offspring_temp[2*j] = child_1
        offspring_temp[2*j + 1] = child_2
    return offspring_temp

# 'fn_mut_selection' selects random gene locations from the entire population of
# chromosomes and returns a list of coordinates.  The most fit chromosome,
# current_gen[0], is excluded from this process.
def fn_mut_selection(l_num_mut, l_pop_size, l_led_qty):
    coord_list = zeros((l_num_mut, 2), dtype=int)
    for j in range(l_num_mut):
        coord_list[j,0] = rnd.randrange(1, l_pop_size)
        coord_list[j,1] = rnd.randrange(0, l_led_qty)
    return coord_list

# 'fn_add_plot' adds a plot of brightness vs wavelength to one of the subplots
# in the existing figure.
def fn_add_plot(l_subplot, l_x, l_y):
    if l_subplot == 1:
        ax1.plot(l_x,l_y)
        ax1.set_xlim([350, 550])
        ax1.set_ylim([0, 1.0])
    elif l_subplot == 2:
        ax2.plot(l_x,l_y)
        ax2.set_xlim([350, 550])
        ax2.set_ylim([0, 1.0])
    else:
        ax3.plot(l_x,l_y)
    
##############################################################################
# MAIN BODY OF PROGRAM
##############################################################################

# Data arrays
wl = arange(wl_min, wl_max, wl_incr)    # Incremental wavelength values
sd_target = zeros_like(wl)              # Target brightness distribution
sd = zeros_like(wl)                     # Computed brightness distribution
gen_number = zeros(num_gen)
best_cost = zeros_like(gen_number)
current_gen = zeros((pop_size, led_qty), dtype=float)
next_gen = zeros((pop_size, led_qty), dtype=float)
fitness = zeros(pop_size, dtype=float)

# Target distribution to be used in computing the fitness of each chromosone.
# The mode parameter will be used to select between flat, linearly sloped and
# u-shaped targets.
index = 0
while index < index_max:
    if mode == 1:
        sd_target[index] = 0.5
    elif mode == 2:
        endpoint_1 = 0.8
        endpoint_2 = 0.5
        m = (endpoint_1 - endpoint_2) / (wl_min - wl_max)
        b = endpoint_1 - m * wl_min
        sd_target[index] = m * wl[index] + b
    elif mode == 3:
        x_points = array([350.0,400.0, 450.0, 500.0, 550.0])
        y_points = array([1.0, 0.6, 0.5, 0.55, 0.8])
        spl_rep = spl.splrep(x_points, y_points, s=0)
        sd_target = spl.splev(wl, spl_rep, der=0)
    index = index + 1

# Create an initial population with chromosomes containing a random brightness
# value in the range [0.0,1.0] for each LED.
for j in range(0, pop_size):
    for k in range(0, led_qty):
        current_gen[j,k] = rnd.random()

# Create a matplotlib figure for plotting the spectral distributions.
fig1 = plt.figure(figsize = (8,12))

ax1 = fig1.add_subplot(311)
ax1.grid(linestyle=':', linewidth=1)
ax1.set_xlabel('Wavelength (nm)')
ax1.set_ylabel('Amplitude')
fn_add_plot(1, wl, sd_target)

ax2 = fig1.add_subplot(312)
ax2.grid(linestyle=':', linewidth=1)           
ax2.set_ylabel('Amplitude')
ax2.set_xlabel('Wavelength (nm)')
fn_add_plot(2, wl, sd_target)

ax3 = fig1.add_subplot(313)
ax3.grid(linestyle=':', linewidth=1)           
ax3.set_ylabel('Cost Function')
ax3.set_xlabel('Generation')

print

# Loop over multiple generations
for n in range(num_gen):
    
    # Step through the chromosomes in a population, calculate the spectral
    # distribution and fitness and add a plot of the distribution to an
    # existing figure.
    j = 0
    for chromosome in current_gen:
        # Compute the spectral distribution for the chromosome
        sd = fn_distribution(chromosome)
        # Use the result and a target distribution to compute a fitness
        # parameter for the jth chromosome
        fitness[j] = fn_fitness(sd, sd_target)
        sd = zeros_like(wl)             # Re-initialize the distribution
        j = j + 1

    # Sort the current population by descending fitness value (increasing
    # cost).
    sorted = fn_sort_by_fitness(current_gen, fitness)
    current_gen = sorted['pop']
    fitness = sorted['fit']

    # Select the mating pairs from the surviving chromosomes
    mating_pairs = fn_pair_selection(fitness)

    # Generate offspring from mating pairs using one of the crossover schemes.
    offspring = zeros((pop_size, led_qty), dtype=float)
    offspring = fn_crossover_1(current_gen, mating_pairs)

    # Replace nonsurviving chromosomes with the new offspring to create a next
    # generation population.
    for j in range(pop_size/2):
        next_gen[j] = current_gen[j]
        next_gen[pop_size/2 + j] = offspring[j]

    # Introduce mutations into the next generation population reducing the
    # maximum allowable mutation size in later generations as the results
    # begin to converge.
    num_mut = int(round(pop_size * led_qty * mut_rate))
    mut_coord_list = fn_mut_selection(num_mut, pop_size, led_qty)
    mut_max = mut_max_init
    if n > 10:
        mut_max = mut_max_init / 2.0
    elif n > 20:
        mut_max = mut_max_init / 4.0
    elif n > 30:
        mut_max = mut_max_init / 8.0
    elif n > 40:
        mut_max = mut_max_init / 16.0
    for coord in mut_coord_list:
        mut_dir = int(round(rnd.random()))
        if mut_dir == 0:
            mut_dir = -1
        else:
            mut_dir = 1
        value = next_gen[coord[0], coord[1]]
        mut_value = value + mut_dir * mut_max * rnd.random()
        if mut_value < 0.0:
            mut_value = 0.0
        elif mut_value > 1.0:
            mut_value = 1.0
        next_gen[coord[0], coord[1]] = mut_value

    # Plot the highest ranked chromosome of each generation in the same subplot.
    sd = fn_distribution(current_gen[0])
    subplot = 1
    fn_add_plot(subplot, wl, sd)

    # Save the best cost for each generation for plotting.
    gen_number[n] = n
    best_cost[n] = fitness[0]

    # Print the best result for each generation.
    print "Gen", n, "finished, best cost result =", fitness[0]

    # Prepare for the next iteration
    current_gen = next_gen

# Plot relative output vs wavelength for final generation.
sd = fn_distribution(current_gen[0])
subplot = 2
fn_add_plot(subplot, wl, sd)

# Plot best cost trend versus generation number
subplot = 3
fn_add_plot(subplot, gen_number, best_cost)

plt.show()
print
print "Final LED settings:"
print current_gen[0]


##############################################################################
# TO DO LIST
##############################################################################

#   - eliminate duplicates from the mutation coordinate list
#   - explore some more sophisticated crossover methods
#   - add additional modes for sloped linear and u-shaped profiles
