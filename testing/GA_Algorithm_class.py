from math import *
from numpy import *
import sys
import matplotlib.pyplot as plt
import scipy.interpolate as spl
import random as rnd


class GeneticAlgorithm:
    def __init__(self, led_data_list, points_list):

        #Constant simulation parameters
        self.led_list = array(led_data_list)
        self.pop_size = 100	    # Population size, must be a multiple of 4
        wl_incr = 2
        wl_min = points_list[0][0]
        wl_max = points_list[len(points_list) - 1][0]
        self.index_max = int((wl_max - wl_min)/wl_incr)
        self.led_qty = len(led_data_list)

        # Determine mode
        # 1-linear flat, 2-linear sloped, 3-not linear
        if len(points_list) == 2:
            if points_list[0][1] == points_list[1][1]:
                mode = 1
            else:
                mode = 2
        else:
            mode = 3
        
        # Data arrays
        self.wl = arange(wl_min, wl_max, wl_incr)   # Incremental wavelength values
        self.sd_target = zeros_like(self.wl)        # Target brightness distribution
        self.sd = zeros_like(self.wl)		    # Computed brightness distribution

        # Calculate target distribution
        index = 0
        while index < self.index_max:
            if mode == 1:
                self.sd_target[index] = points_list[0][1]
            elif mode == 2:
                endpoint_1 = points_list[0][1]
                endpoint_2 = points_list[1][1]
                m = (endpoint_1 - endpoint_2) / (wl_min - wl_max)
                b = endpoint_1 - m * wl_min
                self.sd_target[index] = m * self.wl[index] + b
            elif mode == 3:
                x_pts = []
                y_pts = []
                for i in points_list:
                    x_pts.append(points_list[i][0])
                    y_pts.append(points_list[i][1])
                x_points = array(x_pts)
                y_points = array(y_pts)
                spl_rep = spl.splrep(x_points, y_points, s=0)
                self.sd_target = spl.splev(self.wl, spl_rep, der=0)
            index = index + 1 
        
        

    ##############################################################################
    # FUNCTIONS
    ##############################################################################

    # 'fn_gaussian' calculates the relative power output from a given LED
    # at a specified wavelength.
    def fn_gaussian(self, wl, led, z):
        b = led[0]
        fwhm = led[1]
        x = wl
        a = z
        c = fwhm/sqrt(8*log(2))
        return a*exp(-((x-b)**2)/(2*c**2))

    # 'fn_fitness' iterates through a given spectral distribution and
    # calculates a net fitness value.
    def fn_fitness(self, dist, target):
        y = 0.0
        index = 0
        while index < self.index_max:
            y = y + (dist[index] - target[index])**2
            index = index + 1
        return y

    # 'fn_sort_by_fitness' sorts a population of chromosomes by their calculated
    # fitness with the most fit at the head of the list. Returns a dictionary
    # containing arrays holding the sorted chromosones and fitness values.
    def fn_sort_by_fitness(self, pop, fit):
        temp_pop = zeros((self.pop_size, self.led_qty), dtype=float)
        temp_fit = zeros(self.pop_size, dtype=float)
        
        for j in range((self.pop_size-1), -1, -1):
            m = argmax(fit)
            temp_pop[j] = pop[m]
            temp_fit[j] = fit[m]
            
            fit[m] = -1
        return {'pop':temp_pop, 'fit':temp_fit}

    # 'fn_distribution' calculates the spectral distribution for a chromosome
    # by summing the contributions from each LED in self.led_list.
    def fn_distribution(self, chromosome):
        dist = zeros_like(self.wl)
        k = 0
        for gene in chromosome:
            index = 0
            while index < self.index_max:
                brightness = self.fn_gaussian(self.wl[index],self.led_list[k],gene)
                dist[index] = dist[index] + brightness
                index = index + 1
            k = k + 1
        return dist

    # 'fn_pair_selection' uses a cost weighted random pairing method to
    # select mating pairs from the pool of surviving chromosomes
    def fn_pair_selection(self, cost):
        # Use the fitness value to compute a normalized cost for each chromosome.
        norm_cost = zeros(self.pop_size, dtype=float)
        for j in range(self.pop_size/2):
            norm_cost[j] = cost[j] - cost[self.pop_size/2]
        
        # Use the normalized costs to compute a mating probability for
        # each chromosome.
        mating_prob = zeros(self.pop_size, dtype=float)
        sum_cost = 0.0
        for j in range(self.pop_size/2):
            sum_cost = sum_cost + norm_cost[j]
        for j in range(self.pop_size/2):
            if abs(sum_cost) > 0.0:
                mating_prob[j] = abs(norm_cost[j] / sum_cost)
            else:
                print
                print "Simulation halted, results will not improve any further."
                return
        
        # Compute a cumulative mating probability for each chromosome.
        cum_prob = zeros(self.pop_size, dtype=float)
        for j in range(self.pop_size/2):
            k = 0
            while k <= j:
                cum_prob[j] = cum_prob[j] + mating_prob[k]
                k = k + 1
        
        # Create a list of unique mating pairs
        pairs = -1 * ones((self.pop_size/4, 2), int)
        for j in range(self.pop_size/4):
            num_selected = 0
            while num_selected < 2:
                threshold = rnd.random()
                for k in range(self.pop_size/2):
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
    def fn_crossover_1(self, pop, pairs):
        offspring_temp = zeros((self.pop_size/2, self.led_qty), dtype=float)
        parent_1 = zeros(self.led_qty, dtype=float)
        parent_2 = zeros(self.led_qty, dtype=float)
        child_1 = zeros(self.led_qty, dtype=float)
        child_2 = zeros(self.led_qty, dtype=float)
        
        for j in range(self.pop_size/4):
            parent_1 = pop[pairs[j,0]]
            parent_2 = pop[pairs[j,1]]
                    
            for k in range(0, self.led_qty):
                beta = rnd.random()
                child_1[k] = beta*parent_1[k] + (1-beta)*parent_2[k]
                child_2[k] =(1-beta)*parent_1[k] + beta*parent_2[k]
                
            offspring_temp[2*j] = child_1
            offspring_temp[2*j + 1] = child_2
     
        return offspring_temp

    # 'fn_mut_selection' selects random gene locations from the entire population of
    # chromosomes and returns a list of coordinates.  The most fit chromosome,
    # current_gen[0], is excluded from this process.
    def fn_mut_selection(self, l_num_mut, l_pop_size, l_led_qty):
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
            
    ##############################################################################
    # ALGORITHM
    ##############################################################################

    def optimize(self):

        num_gen = 2		        # Number of generations
        mut_rate = 0.2	        	# Mutation probability
        mut_max_init = 0.3              # Initial maximum allowable mutation

        current_gen = zeros((self.pop_size, self.led_qty), dtype=float)
        next_gen = zeros((self.pop_size, self.led_qty), dtype=float)
        fitness = zeros(self.pop_size, dtype=float)

        
        # Create an initial population with chromosomes containing a random brightness
        # value in the range [0.0,1.0] for each LED.
        for j in range(0, self.pop_size):
            for k in range(0, self.led_qty):
                current_gen[j,k] = rnd.random()
        
        for n in range(num_gen):
                
                # Step through the chromosomes in a population, calculate the spectral
                # distribution and fitness and add a plot of the distribution to an
                # existing figure.
                j = 0
                for chromosome in current_gen:
                        # Compute the spectral distribution for the chromosome
                        self.sd = self.fn_distribution(chromosome)
                        # Use the result and a target distribution to compute a fitness
                        # parameter for the jth chromosome
                        fitness[j] = self.fn_fitness(self.sd, self.sd_target)
                        self.sd = zeros_like(self.wl)             # Re-initialize the distribution
                        j = j + 1

                # Sort the current population by descending fitness value (increasing
                # cost).
                sorted = self.fn_sort_by_fitness(current_gen, fitness)
                current_gen = sorted['pop']
                fitness = sorted['fit']

                # Select the mating pairs from the surviving chromosomes
                mating_pairs = self.fn_pair_selection(fitness)

                # Generate offspring from mating pairs using one of the crossover schemes.
                offspring = zeros((self.pop_size, self.led_qty), dtype=float)
                offspring = self.fn_crossover_1(current_gen, mating_pairs)

                # Replace nonsurviving chromosomes with the new offspring to create a next
                # generation population.
                for j in range(self.pop_size/2):
                        next_gen[j] = current_gen[j]
                        next_gen[self.pop_size/2 + j] = offspring[j]

                # Introduce mutations into the next generation population reducing the
                # maximum allowable mutation size in later generations as the results
                # begin to converge.
                num_mut = int(round(self.pop_size * self.led_qty * mut_rate))
                mut_coord_list = self.fn_mut_selection(num_mut, self.pop_size, self.led_qty)
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

                # Prepare for the next iteration
                current_gen = next_gen
            
        return current_gen[0]
