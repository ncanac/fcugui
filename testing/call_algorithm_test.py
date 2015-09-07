from GA_Algorithm_01 import *

led_list = [[350, 15],
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
[565, 30]]

point_list = [[350,.5],[550,.5]]

algorithm = GeneticAlgorithm(led_list, point_list)

print algorithm.optimize()


