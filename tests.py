from timeit import default_timer as timer
from datetime import timedelta
from solver import *
from data_generator import *

#generator = InstanceGenerator(10000)
#generator.instance_to_file("900.dat")

INSTANCE_NAME = "Data/35ka.dat"
LOCAL_SEARCH = True
ALPHA = 0.9

instance = Instance(INSTANCE_NAME)
solver = Solver(instance)

start = timer()
solver.solve_heuristic(grasp=LOCAL_SEARCH, alpha=ALPHA)
print("Greedy finished")
solver.perform_local_search()
end = timer()

print("Runtime %s s\nQuality %s" % (timedelta(seconds=end - start), solver.cost))
