from __future__ import absolute_import
from __future__ import print_function
import torch
import matplotlib.pyplot as plt
import re
import time
import random
from pysat.solvers import Glucose3
from pysat.examples.genhard import PHP
from pysat.examples.genhard import CB
    
def nand_sat(equation):
    #sanitise input string
    chars = {'0','1','2','3','4','5','6','7','8','9','[',']','(',')','*'}
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
        
        def __mul__(self,other):
            return BoolVal(1-self.val*other.val)
        
        def error(self):
            return (1-self.val)**2

    #calculate expression gradient at centre and correct parameters
    params.grad = None
    output = eval(equation)
    output.error().backward()
    params.data = (1-torch.sign(params.grad))/2
    
    #check answer
    output = eval(equation)
    if output.error() == 0:
        return params.data.bool().tolist()

def sat_tester(start_size = 1,
               final_size = 4,
               step_size = 1,
               batch_size = 1,
               verbose = False):
    
    class SatNode:
        def __init__(self, parent=None, var = None):
            self.parent = parent
            self.var = str(var)
            
        def eval(self, var_dict):
            if hasattr(self, "children"):
                return not (self.children[0].eval(var_dict)&
                            self.children[1].eval(var_dict))
            elif self.var:
                return var_dict[self.var]

        def __str__(self):
            if hasattr(self, "children"):
                return f"({str(self.children[0])}*{str(self.children[1])})"
            elif self.var:
                return f"[{self.var}]"
            else:
                return "[Nan]"

        def __repr__(self):
            return str(self)
            
        def gen_children(self):
            self.children = [SatNode(parent=self), SatNode(parent=self)]
            return self.children

        def pick_vars(self, var_dict):
            self.var = random.choice(list(var_dict.keys()))
            return self.var
        
        def cnf(self, solver):
            pass
  
    test_size = []
    test_score = []
    test_score_processor = []
    for size in range(start_size, final_size+1, step_size):
        print(f"Starting tests for size {size}")
        test_size += [size]
        sample_score = []
        sample_score_processor = []

        #run test up to test_size
        for _ in range(batch_size):
            #generate random Nand tree of correct size
            var_dict = {str(var): None for var in range(size)}
            root = SatNode()
            nodes = [root]
            end_nodes = nodes
            
            #create random nodes
            for _ in range(size):
                choice = random.choice(end_nodes)
                children = choice.gen_children()
                end_nodes = end_nodes + children
                end_nodes.remove(choice)
                nodes = nodes + children
            
            # associate each end node with a variable
            for node in end_nodes:
                node.pick_vars(var_dict)

            #runs sat solver
            equation = str(root)
            time_start = time.time()
            time_start_processor = time.process_time()
            result = nand_sat(equation)
            time_taken = time.time()-time_start
            time_taken_processor = time.process_time()-time_start_processor
            sample_score += [time_taken*1000]
            sample_score_processor += [time_taken*1000]
            
            #if verbose print log
            if verbose:
                print(f"Nands:  {equation}")
                print(f"Result:  {result}\n")

            #checks result against tree            
            if result:
                #If test_checker is set to true the result is  randomly
                #modified in order to verify that the checking
                #procedure is functioning
                test_checker = False
                
                if test_checker:
                    result = [random.random()>0.5 for _ in result] 
                    print(f"Modified result {result}\n")

                vars = re.findall("\[\d*\]",equation)
                vars = list(dict.fromkeys(vars))
                var_dict = {str(val[1:-1]):result[ind] for ind, val in enumerate(vars)}
                val = root.eval(var_dict)

                if not val:
                    print(f"Nands:  {equation}")
                    print(f"Result:  {result}")
                    raise ValueError("The provided solution was incorrect")
            
        #average sample values
        test_score += [sum(sample_score)/len(sample_score)]
        test_score_processor += [sum(sample_score_processor)/len(sample_score_processor)]
        
        
    #plot results
    plt.plot(test_size, test_score, label = "real time")
    #plt.plot(test_size, test_score_processor, label = "processor time")
    plt.xlabel("Number of NAND gates")
    plt.ylabel("Average Time (ms)")
    #plt.legend()
    plt.show()
    
if __name__ == "__main__":
    cnf_test()
    """
    sat_tester(start_size = 20,
               final_size=200,
               batch_size = 100,
               verbose = False)
    """
    
    #test_string = "(([0]*[2])*([0]*[1]))*(([1]*[1])*([2]*[2]))"
    #val = nand_sat(test_string)
    #print(val)