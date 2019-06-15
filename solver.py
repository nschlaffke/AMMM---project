import re
import numpy as np
from timeit import default_timer as timer


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
        step_back = -1
        while self.hired < self.instance.wr:
            candidates_filtered = self.filter_infeasible(self.candidates)
            if len(candidates_filtered) == 0:
                print("step back")
                provider, batch, add = self.solution[step_back]
                self.solution[-1] = provider, batch, 0
                self.hired -= add
                step_back -= 1
                continue
            step_back = -1
            candidates_cost = [(candidate, self.q(candidate)) for candidate in candidates_filtered]
            if grasp:
                candidate, number_of_workers, additional = self.get_grasp_candidate(candidates_cost, alpha)
                self.update_data(candidate, number_of_workers + additional)
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
        additional_batch = 0
        candidates_sorted = sorted(candidates_cost, key=lambda cand_cost: cand_cost[1])
        q_max = candidates_sorted[0][1]
        q_min = candidates_sorted[-1][1]
        rtl = [candidate for candidate in candidates_sorted if candidate[1] <= q_min + alpha * (q_max - q_min)]
        best, cost = rtl[np.random.randint(low=0, high=len(rtl))]
        if best.available_workers <= self.get_needed_workers():
            number_of_workers = best.available_workers
            missing = self.get_needed_workers() - number_of_workers
            if missing > 0:
                additional_batch = min(missing, number_of_workers)
        else:
            number_of_workers = best.available_workers / 2

        return best, number_of_workers, additional_batch

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
        allowed_by_country = [candidate for candidate in candidates if self.allowed_country_provider(candidate)]
        allowed_by_size = [candidate for candidate in allowed_by_country if self.allowed_by_size(candidate)]
        return allowed_by_size

    def allowed_country_provider(self, candidate):
        if not (candidate.get_country() in self.used_countries) and not (candidate.id in self.used_providers):
            return True  # We didn't use this country
        else:
            return False

    def allowed_by_size(self, candidate):
        needed = self.instance.wr - self.hired
        if candidate.available_workers <= needed or candidate.available_workers / 2 <= needed:
            return True
        else:
            return False

    @staticmethod
    def can_substitute(new_provider, old_provider_pack):

        old_provider, old_reg_batch, old_add_batch = old_provider_pack
        summary_provided = old_reg_batch + old_add_batch
        if new_provider.available_workers <= summary_provided <= new_provider.available_workers * 2:
            return True
        elif new_provider.available_workers / 2 == summary_provided:
            return True
        else:
            return False

    def perform_local_search(self):
        if self.cost is None:
            raise Exception("No base solution")

        start = timer()
        while True:
            if timer() - start > 30*5:
                break
            current_cost = self.cost
            improved = False
            for used_provider in self.solution:
                if improved:
                    break
                for potential_provider in self.instance.providers:
                    if potential_provider.id in self.used_providers:
                        continue
                    if potential_provider.country in self.used_countries:
                        continue
                    if not self.can_substitute(potential_provider, used_provider):
                        continue
                    self.solution.remove(used_provider)
                    old_provider, reg_batch, add_batch = used_provider
                    self.hired -= (reg_batch + add_batch)

                    potential_provider_as_candidate = self.max_from_provider(potential_provider)
                    self.solution.append(potential_provider_as_candidate)
                    new_cost = self.calculate_cost()

                    if new_cost < current_cost:
                        improved = True
                        self.cost = new_cost

                        self.used_countries.remove(old_provider.country)
                        self.used_countries.add(potential_provider.country)

                        self.used_providers.remove(old_provider.id)
                        self.used_providers.add(potential_provider.id)
                        break
                    else:
                        self.solution.remove(potential_provider_as_candidate)
                        self.solution.append(used_provider)
                    self.hired += (reg_batch + add_batch)
            if not improved:
                break
