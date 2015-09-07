import sys
import matplotlib.pyplot as plt
import scipy.interpolate as spl
from GA_Algorithm_02 import *

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
wl_min = 350.0              # Minimum wavelength considered
wl_incr = 2.0               # Wavelength increment
wl_max = 550.0 + wl_incr    # Maximum wavelength considered
mode = 3                    # 1-linear flat, 2-linear sloped, 3-not linear

##############################################################################
# FUNCTIONS
##############################################################################


# 'fn_add_plot' adds a plot of brightness vs wavelength to one of the subplots
# in the existing figure.
##def fn_add_plot(l_subplot, l_x, l_y):
##    if l_subplot == 1:
##        ax1.plot(l_x,l_y)
##        ax1.set_xlim([350, 550])
##        ax1.set_ylim([0, 1.0])
##    elif l_subplot == 2:
##        ax2.plot(l_x,l_y)
##        ax2.set_xlim([350, 550])
##        ax2.set_ylim([0, 1.0])
##    else:
##        ax3.plot(l_x,l_y)
    
##############################################################################
# MAIN BODY OF PROGRAM
##############################################################################

# Data arrays
wl = arange(wl_min, wl_max, wl_incr)
sd_target = zeros_like(wl)              # Target brightness distribution


# Target distribution to be used in computing the fitness of each chromosone.
# The mode parameter will be used to select between flat, linearly sloped and
# u-shaped targets.
index = 0
while index < len(sd_target):
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

# Create a matplotlib figure for plotting the spectral distributions.
##fig1 = plt.figure(figsize = (8,12))
##
##ax1 = fig1.add_subplot(311)
##ax1.grid(linestyle=':', linewidth=1)
##ax1.set_xlabel('Wavelength (nm)')
##ax1.set_ylabel('Amplitude')
##fn_add_plot(1, wl, sd_target)
##
##ax2 = fig1.add_subplot(312)
##ax2.grid(linestyle=':', linewidth=1)           
##ax2.set_ylabel('Amplitude')
##ax2.set_xlabel('Wavelength (nm)')
##fn_add_plot(2, wl, sd_target)
##
##ax3 = fig1.add_subplot(313)
##ax3.grid(linestyle=':', linewidth=1)           
##ax3.set_ylabel('Cost Function')
##ax3.set_xlabel('Generation')

print fn_ga_algorithm(led_list, sd_target, wl_min, wl_incr, wl_max)

# Plot relative output vs wavelength for final generation.
##sd = fn_distribution(current_gen[0])
##subplot = 2
##fn_add_plot(subplot, wl, sd)
##
### Plot best cost trend versus generation number
##subplot = 3
##fn_add_plot(subplot, gen_number, best_cost)
##
##plt.show()
##print
##print "Final LED settings:"
##print current_gen[0]


##############################################################################
# TO DO LIST
##############################################################################

#   - eliminate duplicates from the mutation coordinate list
#   - explore some more sophisticated crossover methods
#   - add additional modes for sloped linear and u-shaped profiles
