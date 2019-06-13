import numpy as np


class InstanceGenerator:
    def __init__(self, instance_size):
        self.num_providers = instance_size
        self.cost_worker = self.get_worker_costs()
        self.available_workers = self.get_workers()
        self.wr = self.get_wr()
        self.country = self.get_countries()
        self.cost_contract = self.get_cost_contract()
        self.cost_1 = 10
        self.cost_2 = 20
        self.cost_3 = 30  # cost1 < cost2 < cost3

    def get_even(self, numbers):
        return [number + 1 if number % 2 else number for number in numbers]

    def get_cost_contract(self):
        return np.random.randint(low=500, high=2500, size=self.num_providers)

    def get_worker_costs(self):
        return np.random.randint(low=100, high=1000, size=self.num_providers)

    def get_wr(self):
        return sum(self.available_workers) // 2

    def get_workers(self):
        return self.get_even(np.random.randint(low=10, high=50, size=self.num_providers))

    def get_countries(self):
        num_countries = self.num_providers * 0.9
        return np.random.randint(low=1, high=1 + num_countries, size=self.num_providers)

    def instance_to_file(self, file_name):
        file = open(file_name, 'w')
        file.write("wr=%s;\n" % self.wr)
        file.write("nProviders=%s;\n" % self.num_providers)

        cost_worker_opl = self.generate_opl_array(self.cost_worker)
        file.write("cost_worker=%s;\n" % cost_worker_opl)

        available_workers_opl = self.generate_opl_array(self.available_workers)
        file.write("available_workers=%s;\n" % available_workers_opl)

        cost_contract_opl = self.generate_opl_array(self.cost_contract)
        file.write("cost_contract=%s;\n" % cost_contract_opl)

        country_opl = self.generate_opl_array(self.country)
        file.write("country=%s;\n" % country_opl)

        file.write("cost_1=%s;\n" % self.cost_1)
        file.write("cost_2=%s;\n" % self.cost_2)
        file.write("cost_3=%s;\n" % self.cost_3)

    @staticmethod
    def generate_opl_array(array):
        str_array = [str(x) for x in array]
        string = ' '.join(str_array)
        return '[' + string + ']'


#generator = InstanceGenerator(70000)
generator = InstanceGenerator(100)
generator.instance_to_file("test.dat")
