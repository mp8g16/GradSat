from pysat.solvers import Solver
from pysat.formula import CNF
from pysat.examples.genhard import PHP
from pysat.examples.genhard import CB
from pysat.examples.genhard import GT
from pysat.examples.genhard import PAR
import matplotlib.pyplot as plt

#necessary for grad_solve
import random
import re
import torch
import time

solvers = ['cadical',
           'glucose30',
           'glucose41',
           'lingeling',
           'maplechrono',
           'maplecm',
           'maplesat',
           'minicard',
           'minisat22',
           'minisat-gh']

def test_solvers():
    cnf = CNF(from_clauses=[[1, 2, 3], [-1, 2], [-2]])

    for name in solvers:
        with Solver(name=name, bootstrap_with=cnf) as solver:
            solver.solve()
            stats = solver.accum_stats()
            assert 'conflicts' in stats, 'No conflicts for {0}'.format(name)
            assert 'decisions' in stats, 'No decisions for {0}'.format(name)
            assert 'propagations' in stats, 'No propagations for {0}'.format(name)
            assert 'restarts' in stats, 'No restarts for {0}'.format(name)           


def gradsat(equation):
    #if cnf is passed convert to nand equation
    if isinstance(equation,list):
        not_sign = lambda val : ['','-'][(1-val//abs(val))//2]
        first_pass = ["|".join([f"{not_sign(val)}[{str(abs(val))}]"
                      for val in clause])
                      for clause in equation]
        equation = '&'.join([f"({clause})" for clause in first_pass])

    #sanitise input string
    chars = {'0','1','2','3','4','5','6','7','8','9','[',']','(',')','&','-','|'}
    equation = ''.join([char for char in equation if char in chars])

    #create variables for all variables in string, generate evaluation equation
    vars = re.findall("\[\d*\]",equation)
    vars = list(dict.fromkeys(vars))
    var_dict = {int(val[1:-1]):ind for ind, val in enumerate(vars)}
    params = (torch.ones(len(var_dict))/2).requires_grad_(True)
    equation = re.sub("\[\d*\]","BoolVal(params[var_dict\g<0>])", equation)
    #Create BoolVal class which extends Boolean logic from discrete
    #to continuous domain.
    class BoolVal:
        def __init__(self,x):
            self.val = x
        
        def __and__(self,other):
            return BoolVal(self.val*other.val)
            
        def __or__(self, other):
            return BoolVal(self.val+other.val-self.val*other.val)
        
        def __neg__(self):
            return BoolVal(1-self.val)

        def error(self):
            return (1-self.val)**2

    for _ in range(len(var_dict)):
        #calculate expression gradient at centre and correct parameter
        params.grad = None
        output = eval(equation)
        output.error().backward()
        
        direction = torch.sign(params.grad)
        not_set = 1-(2*params-1)**2
        set_val = not_set*torch.abs(direction)
        ind = int(torch.argmax(torch.abs(params.grad*not_set)))
        """
        print(output.val)
        print(params.data)
        print(params.grad)
        print(direction)
        print(ind)"""
        
        #update value
        if set_val[ind] == 1:
            params.data[ind] = (1-direction[ind])/2
        else:
            ind = int(torch.argmax(torch.abs(not_set)))
            params.data[ind] = 0

        #print("\n\n")
    #check answer    
    output = eval(equation)
    if output.error() == 0:
        solution = params.data.tolist()
        results = [int((2*solution[val]-1)*key) for key, val in var_dict.items()]
        return sorted(results, key=abs)
 

def gen_cnf(size):
    vars = [int((1/2-ind%2)*(2+ind-ind%2)) for ind in range(2*size)]
    new_cnf = [[vars[random.randint(0,2*size-1)] for _ in range(3)] 
               for _ in range(size)]
    return new_cnf
    
def standard_solvers(name, cnf):
    g = Solver(name=name, bootstrap_with=cnf, with_proof=True)
    solvable = g.solve()
    if solvable:
        return g.get_model()
    
def cnf_test():
    #cnf = gen_cnf(5)
    cnf = [[20, 15, 19], [-19, -14, 13], [6, 18, -5], [-13, -5, -1], [3, -18, -3], [-2, 1, 8], [-11, -8, 13], [-12, 20, 18], [-2, 9, 6], [-8, -16, -7], [15, 6, 17], [18, -8, 17], [19, 19, -6], [-7, 10, 20], [-12, -16, -19], [-6, -9, -4], [-1, 5, 8], [-7, 5, 7], [10, -18, -6], [1, 18, -5]]
    result = gradsat(cnf)
    print(result)
    print(standard_solvers("glucose30", cnf))

def sat_tester(start_size = 1,
               final_size = 4,
               step_size = 1,
               batch_size = 1):
               
    test_size = []
    grad_test_score = []
    gluc_test_score = []
    for size in range(start_size, final_size+1, step_size):
        print(f"Starting tests for size {size}")
        test_size += [size]
        grad_sample_score = []
        gluc_sample_score = []

        #run test up to test_size
        for _ in range(batch_size):
            #generate random 3CNF of given size
            #cnf = cnf = gen_cnf(size)
            cnf = GT(size).clauses
            
            #runs gradsat solver
            time_start = time.time()
            result_grad = gradsat(cnf)
            time_taken = time.time()-time_start
            grad_sample_score += [time_taken*1000]
            
            #runs glucose solver
            time_start = time.time()
            result_gluc = standard_solvers("glucose30", cnf)
            time_taken = time.time()-time_start
            gluc_sample_score += [time_taken*1000]

            #check both returns answers
            check1 = result_gluc is None and result_grad is not None
            check2 = result_gluc is not None and result_grad is None
            if check1 or check2:
                print(f"CNF:    {cnf}")
                print(f"GradSat:    {result_grad}")
                print(f"Glucose:    {result_gluc}")
                raise ValueError("GradSat and Glucose disgreed")
            
        #average sample values
        grad_test_score += [sum(grad_sample_score)/len(grad_sample_score)]
        gluc_test_score += [sum(gluc_sample_score)/len(gluc_sample_score)]

    #plot results
    plt.plot(test_size, grad_test_score, label = "MySat")
    plt.plot(test_size, gluc_test_score, label = "Glucose")
    plt.xlabel("Number of 3Sat clauses")
    plt.ylabel("Average Time (ms)")
    plt.legend()
    plt.show()
    
if __name__ =="__main__":
    #print(gen_cnf(3))
    #cnf_test()
    sat_tester(start_size = 2,
               final_size = 12,
               step_size = 1,
               batch_size = 10)