import re


class Provider:
    def __init__(self, cost_contract, cost_worker, available_workers, country, provider_id):
        self.cost_contract = cost_contract
        self.cost_worker = cost_worker
        self.available_workers = available_workers
        self.country = country
        self.id = provider_id

    def get_cost_contract(self):
        return self.cost_contract

    def get_cost_worker(self):
        return self.cost_worker

    def get_available_workers(self):
        return self.available_workers

    def get_country(self):
        return self.country

    def get_id(self):
        return self.id


class Instance:
    def __init__(self, data_file):
        with open(data_file, 'r') as file:
            self.wr = self.extract_digits(file.readline())
            self.num_providers = self.extract_digits(file.readline())
            self.cost_worker = self.extract_digits(file.readline())
            self.available_workers = self.extract_digits(file.readline())
            self.cost_contract = self.extract_digits(file.readline())
            self.country = self.extract_digits(file.readline())
            self.cost_1 = self.extract_digits(file.readline())[1]
            self.cost_2 = self.extract_digits(file.readline())[1]
            self.cost_3 = self.extract_digits(file.readline())[1]

        self.providers = []
        for p in range(self.num_providers):
            cost_contract = self.cost_contract[p]
            cost_worker = self.cost_worker[p]
            available_workers = self.available_workers[p]
            country = self.country[p]
            provider = Provider(cost_contract, cost_worker, available_workers, country, p)
            self.providers.append(provider)

    @staticmethod
    def extract_digits(str):
        digits = [int(digit) for digit in re.findall(r'\d+', str)]
        return digits if len(digits) > 1 else digits[0]

    def get_providers(self):
        return self.providers


class Solver:
    def __init__(self, instance):
        self.instance = instance
        self.solution = []
        self.candidates = instance.get_providers()
        self.used_providers = set()
        self.used_countries = set()
        self.hired = 0
        self.cost = None

    def calculate_cost(self):
        cost = 0
        for best_candidate, number_of_workers, additional in self.solution:
            cost += best_candidate.cost_contract
            cost += (number_of_workers + additional) * best_candidate.cost_worker
            cost += self.calculate_cost_tax(number_of_workers + additional)
        return cost

    def solve_heuristic(self, grasp=False, alpha=0.5):
        while self.hired < self.instance.wr:
            candidates_filtered = self.filter_infeasible(self.candidates)
            candidates_cost = [(candidate, self.q(candidate)) for candidate in candidates_filtered]
            if grasp:
                candidate, number_of_workers, additional = self.get_grasp_candidate(candidates_cost, alpha)
                self.update_data(candidate, number_of_workers)
                self.solution.append((candidate, number_of_workers, additional))
            else:
                best_candidate, number_of_workers, additional = self.get_best_candidate(candidates_cost)
                self.update_data(best_candidate, number_of_workers + additional)
                self.solution.append((best_candidate, number_of_workers, additional))
        self.cost = self.calculate_cost()

    def update_data(self, best_candidate, number_of_workers):
        self.hired += number_of_workers
        self.used_providers.add(best_candidate.id)
        self.used_countries.add(best_candidate.country)

    def get_grasp_candidate(self, candidates_cost, alpha):
        candidates_sorted = sorted(candidates_cost, key=lambda cand_cost: cand_cost[1])
        q_max, q_min = candidates_sorted[0][1], candidates_sorted[-1][1]
        rtl = [candidate for candidates_sorted if candidate[1] ]
        return (1, 2, 3)

    def get_needed_workers(self):
        return self.instance.wr - self.hired

    def get_best_candidate(self, candidates_cost):
        additional_batch = 0
        candidates_sorted = sorted(candidates_cost, key=lambda cand_cost: cand_cost[1])
        best, cost = candidates_sorted[0]
        if best.available_workers <= self.get_needed_workers():
            number_of_workers = best.available_workers
            missing = self.get_needed_workers() - number_of_workers
            if missing > 0:
                additional_batch = min(missing, number_of_workers)
        else:
            number_of_workers = best.available_workers / 2

        return best, number_of_workers, additional_batch

    def q(self, provider):
        cost_contract = provider.cost_contract if not (provider.id in self.used_providers) else 0
        cost_worker = provider.cost_worker
        cost_tax = self.calculate_cost_tax(provider.available_workers)
        return cost_contract + cost_worker + cost_tax

    def max_from_provider(self, provider):
        additional_batch = 0
        if provider.available_workers <= self.get_needed_workers():
            number_of_workers = provider.available_workers
            missing = self.get_needed_workers() - number_of_workers
            if missing > 0:
                additional_batch = min(missing, number_of_workers)
        else:
            number_of_workers = provider.available_workers / 2

        return provider, number_of_workers, additional_batch

    def calculate_cost_tax(self, number_of_workers):
        if number_of_workers <= 5:
            return number_of_workers * self.instance.cost_1
        elif number_of_workers <= 10:
            cost = 5 * self.instance.cost_1
            number_of_workers -= 5
            cost += number_of_workers * self.instance.cost_2
            return cost
        else:
            cost = 5 * self.instance.cost_1
            cost += 5 * self.instance.cost_2
            number_of_workers -= 10
            cost += number_of_workers * self.instance.cost_3
            return cost

    def filter_infeasible(self, candidates):
        allowed_by_country = [candidate for candidate in candidates if self.allowed_country(candidate)]
        allowed_by_size = [candidate for candidate in allowed_by_country if self.allowed_by_size(candidate)]
        return allowed_by_size

    def allowed_country(self, candidate):
        if not (candidate.get_country() in self.used_countries):
            return True  # We didn't use this country
        elif candidate.id in self.used_providers:
            return True  # We used this country, but we used this provider
        else:
            return False

    def allowed_by_size(self, candidate):
        needed = self.instance.wr - self.hired
        if candidate.available_workers <= needed or candidate.available_workers / 2 <= needed:
            return True
        else:
            return False


instance = Instance("test.dat")
solver = Solver(instance)
solver.solve_heuristic()
print(solver.solution)