from timeit import default_timer as timer
from datetime import timedelta
from solver import *

INSTANCE_NAME = "test.dat"
LOCAL_SEARCH = False
ALPHA = 0.5

instance = Instance(INSTANCE_NAME)
solver = Solver(instance)
start = timer()
solver.solve_heuristic(grasp=LOCAL_SEARCH, alpha=ALPHA)
#solver.perform_local_search()
end = timer()



print("Runtime %s s\nQuality %s" % (timedelta(seconds=end-start), solver.cost))