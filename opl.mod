/*********************************************
 * OPL 12.8.0.0 Model
 * Author: admin
 * Creation Date: 10/4/2019 at 8:33:28
 *********************************************/
//DATA
int num_providers = ...;
int wr = ...;
int cost_1 = ...;
int cost_2 = ...;
int cost_3 = ...;

range P = 1..num_providers;

int available_workers[p in P]=...;
int cost_contract [p in P]=...;
int cost_worker [p in P]=...;
int country [p in P]=...;

//Decision Variables
dvar int+ hired_reg[p in P];
dvar int+ hired_add[p in P];
dvar int+ h_1 [p in P];
dvar int+ h_2 [p in P]; 
dvar int+ h_3 [p in P];
dvar boolean z [p in P];
dvar boolean h [p in P];
dvar boolean a [p in P];
dvar boolean provides[p in P];


minimize sum(p in P) 
(
	provides[p]*cost_contract[p] + // Contract cost for using a provider
	(hired_reg[p] + hired_add[p]) * cost_worker[p] + // Cost for every worker
	(h_1[p]*cost_1 + h_2[p]*cost_2 + h_3[p]*cost_3) // Taxes 
);

subject to{

//The sum of hired workers needs to be equal to wr
sum(p in P) 
	(hired_reg[p] + hired_add[p]) == wr;

//hired_reg[p] > 0 => provides[p] = 1

forall(p in P) 
	available_workers[p]*provides[p] >= hired_reg[p];

//We cannot hire from two providers from the same country
forall(p1,p2 in P: p1 != p2 && country[p1] == country[p2])
  provides[p1] + provides[p2] <= 1;
  
//We can hire 0, half or all the workers from the regular batch from a particular provider
forall(p in P) {
  a[p] + h[p] + z[p] == 1;
  hired_reg[p] == available_workers[p] * (0*z[p] + 0.5*h[p] + 1*a[p]);
}

// We can use additional batch only when we hire all the workers
forall(p in P)
  hired_add[p] <= available_workers[p] * a[p];

forall(p in P)
  h_1[p] + h_2[p] + h_3[p] == hired_reg[p] + hired_add[p];
  
forall(p in P)
  h_1[p] <= 5;
  
forall(p in P)
  h_2[p] <= 5;

}
execute {
 	for (var p in P) {
 		write("Provider " + p + "(used = " + (provides[p]) + "): " + hired_reg[p]);
 		write(" workers required (availability is " + available_workers[p] + ")");
 		writeln("\tcost_worker = " + cost_worker[p] + "\tcost_contract " + cost_contract[p]);
 		
	}
}