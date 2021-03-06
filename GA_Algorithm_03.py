from math import *
from numpy import *
import sys
import matplotlib.pyplot as plt
import scipy.interpolate as spl
import random as rnd


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
    while index < len(dist):
        y = y + (dist[index] - target[index])**2
        index = index + 1
    return y

# 'fn_sort_by_fitness' sorts a population of chromosomes by their calculated
# fitness with the most fit at the head of the list. Returns a dictionary
# containing arrays holding the sorted chromosones and fitness values.
def fn_sort_by_fitness(pop, fit, pop_size, led_qty):
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
def fn_distribution(chromosome, wl, led_list):
    dist = zeros_like(wl)
    k = 0
    for gene in chromosome:
        index = 0
        while index < len(dist):
            brightness = fn_gaussian(wl[index],led_list[k],gene)
            dist[index] = dist[index] + brightness
            index = index + 1
        k = k + 1
    return dist

# 'fn_pair_selection' uses a cost weighted random pairing method to
# select mating pairs from the pool of surviving chromosomes
def fn_pair_selection(cost, pop_size, current_gen, sd, wl):
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

# 'fn_crossover_1' blends parents gene by gene.  It accepts arrays
# containing the current generation of chromosome and the indices to
# the chromosomes for mating pairs. It returns an array containing the
# chromosomes for the resulting offspring.
def fn_crossover_1(pop, pairs, pop_size, led_qty):
    offspring_temp = zeros((pop_size/2, led_qty), dtype=float)
    parent_1 = zeros(led_qty, dtype=float)
    parent_2 = zeros(led_qty, dtype=float)
    child_1 = zeros(led_qty, dtype=float)
    child_2 = zeros(led_qty, dtype=float)
    
 
    for j in range(pop_size/4):
        parent_1 = pop[pairs[j,0]]
        parent_2 = pop[pairs[j,1]]
        beta = rnd.random()*1.4 - 0.2
                
        for k in range(0, led_qty):
            child_1[k] = beta*parent_1[k] + (1-beta)*parent_2[k]
            child_2[k] =(1-beta)*parent_1[k] + beta*parent_2[k]
            
        offspring_temp[2*j] = child_1
        offspring_temp[2*j + 1] = child_2
    return offspring_temp

# 'fn_mut_selection' selects random gene locations from the entire population of
# chromosomes and returns a list of coordinates.  The most fit chromosome,
# current_gen[0], is excluded from this process.
def fn_mut_selection(l_num_mut, l_pop_size, l_led_qty):
    coord_list = zeros((l_num_mut, 2), dtype=int)
    coord_temp = zeros( 2, dtype=int)
    j = 0

    while j < l_num_mut:
        coord_temp[0] = rnd.randrange(1, l_pop_size)
        coord_temp[1] = rnd.randrange(0, l_led_qty)
        found = 0

        for index in range(j):
            if coord_list[index,0] == coord_temp[0]:
                if coord_list[index,1] == coord_temp[1]:
                    found = 1
                    break

        if not(found):
            coord_list[j,0] = coord_temp[0]
            coord_list[j,1] = coord_temp[1]
            j += 1

    return coord_list

# 'fn_mut_adj' adjusts the maximum mutation rate based on how many 
# generations have passed.
def fn_mut_adj( l_gen ):
    
    if l_gen < 10:
        new_mut = math.exp(-1)
    elif l_gen < 20:
        new_mut = math.exp(-1 - math.log10(l_gen-9))
    elif l_gen < 30:
        new_mut = math.exp(-1 - math.log(l_gen-17))
    elif l_gen < 40:
        new_mut = math.exp(-1 - math.log(l_gen-15))
    else:
        new_mut = math.exp(-1 - math.log(l_gen-10))
        
    return new_mut

##############################################################################
# ALGORITHM
##############################################################################


##def fn_ga_algorithm(led_list, sd_target, wl_min, wl_incr, wl_max):
##    
##    pop_size = 100		# Population size, must be a multiple of 4
##    num_gen = 2			# Number of generations
##    mut_rate = 0.2		# Mutation probability
##    mut_max_init = 0.3		# Initial maximum allowable mutation
##    led_qty = len(led_list)	# Number of genes in each chromosome
##    
##    # Data arrays
##    wl = arange(wl_min, wl_max, wl_incr)		  # Incremental wavelength values
##    sd = zeros_like(wl)                                   # Computed brightness distribution
##    current_gen = zeros((pop_size, led_qty), dtype=float)
##    next_gen = zeros((pop_size, led_qty), dtype=float)
##    fitness = zeros(pop_size, dtype=float)
##    #gen_number = zeros(num_gen)
##    
##    # Create an initial population with chromosomes containing a random brightness
##    # value in the range [0.0,1.0] for each LED.
##    for j in range(0, pop_size):
##        for k in range(0, led_qty):
##            current_gen[j,k] = rnd.random()
##    
##    for n in range(num_gen):
##	    
##	    # Step through the chromosomes in a population, calculate the spectral
##	    # distribution and fitness and add a plot of the distribution to an
##	    # existing figure.
##	    j = 0
##	    for chromosome in current_gen:
##		    # Compute the spectral distribution for the chromosome
##		    sd = fn_distribution(chromosome, wl, led_list)
##		    # Use the result and a target distribution to compute a fitness
##		    # parameter for the jth chromosome
##		    fitness[j] = fn_fitness(sd, sd_target)
##		    sd = zeros_like(wl)             # Re-initialize the distribution
##		    j = j + 1
##
##	    # Sort the current population by descending fitness value (increasing
##	    # cost).
##	    sorted = fn_sort_by_fitness(current_gen, fitness, pop_size, led_qty)
##	    current_gen = sorted['pop']
##	    fitness = sorted['fit']
##
##	    # Select the mating pairs from the surviving chromosomes
##	    mating_pairs = fn_pair_selection(fitness, pop_size, current_gen, sd, wl)
##
##	    # Generate offspring from mating pairs using one of the crossover schemes.
##	    offspring = zeros((pop_size, led_qty), dtype=float)
##	    offspring = fn_crossover_1(current_gen, mating_pairs, pop_size, led_qty)
##
##	    # Replace nonsurviving chromosomes with the new offspring to create a next
##	    # generation population.
##	    for j in range(pop_size/2):
##		    next_gen[j] = current_gen[j]
##		    next_gen[pop_size/2 + j] = offspring[j]
##
##	    # Introduce mutations into the next generation population reducing the
##	    # maximum allowable mutation size in later generations as the results
##	    # begin to converge.
##	    num_mut = int(round(pop_size * led_qty * mut_rate))
##	    mut_coord_list = fn_mut_selection(num_mut, pop_size, led_qty)
##	    
##	    for coord in mut_coord_list:
##                mut_dir = int(round(rnd.random()))
##		if mut_dir == 0:
##		    mut_dir = -1
##		else:
##		    mut_dir = 1
##		value = next_gen[coord[0], coord[1]]
##		mut_max = fn_mut_adj( coord[1] )
##		mut_value = value + mut_dir * mut_max * rnd.random()
##		if mut_value < 0.0:
##		    mut_value = 0.0
##		elif mut_value > 1.0:
##		    mut_value = 1.0
##		next_gen[coord[0], coord[1]] = mut_value
##
##	    # Prepare for the next iteration
##	    current_gen = next_gen
##	
##    return fn_distribution(current_gen[0], wl, led_list), current_gen[0]
