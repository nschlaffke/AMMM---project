import re


class Provider:
    def __init__(self, cost_contract, cost_worker, available_workers, country):
        self.cost_contract = cost_contract
        self.cost_worker = cost_worker
        self.available_workers = available_workers
        self.country = country

    def get_cost_contract(self):
        return self.cost_contract

    def get_cost_worker(self):
        return self.cost_worker

    def get_available_workers(self):
        return self.available_workers

    def get_country(self):
        return self.country


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
            provider = Provider(cost_contract, cost_worker, available_workers, country)
            self.providers.append(provider)

    def extract_digits(self, str):
        digits = [int(digit) for digit in re.findall(r'\d+', str)]
        return digits if len(digits) > 1 else digits[0]

    def get_providers(self):
        return self.providers

class Solver:
    def __init__(self, instance):
        self.instance = instance
        self.solution = []
        self.candidates = instance.get_providers()

    def solve_heuristic(self, grasp=False):
        hired = 0
        while hired < self.instance.wr:
            candidates_filtered = self.filter_infeasible(self.candidates)
            candidates_cost = [(candidate, q(candidate)) for candidate in candidates_filtered]
            if grasp:
                candidate, number_of_workers, additional = self.get_grasp_candidate(candidates_cost)
                hired += number_of_workers

                self.solution.append((candidate, number_of_workers, additional))
            else:
                best_candidate, number_of_workers, additional = self.get_best_candidate(candidates_cost)
                hired += number_of_workers
                self.solution.append((best_candidate, number_of_workers, additional))



    def get_grasp_candidate(self, candidates_cost):
        pass

    def get_best_candidate(self, candidate_cost):
        return (1,2,3)

    def q(self, provider):
        pass

    def filter_infeasible(self):
        pass



