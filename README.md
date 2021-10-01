# GradSat
 
The GradSat algorithm has the potential to be an efficient algorithm for solving the boolean satisfiability problem. This probably doesn't work, but I haven't unfix-ably broken it yet.

What is P vs NP and 3SAT

P vs NP is a Millennium prize problem which asks if every NP-complete problem can be solved with a polynomial time algorithm. The property of being NP-complete is a combination of two properties: NP and  NP-hard. NP stands for nondeterministic polynomial time. There are a set of problems for which the answer can be checked in polynomial time, such as a soduku. Easy to check someone's answer but sometimes hard to find it. A deterministic turing machine is a computer which can only compute along one deterministic line of instructions. Mutliple tasks must be run one after another, or share time, but not concurrently. A nondeterministic turing machine can effectively create multiple threads which may be run concurrently. This means that any NP problem may be solved in polynomial time by a nondeterministic turing machine as it can create as many threads as there are possible answers. If each answer can be checked in polynomial time then as each thread runs concurrently all answers are checked in polynomial time, making the problem nondeterministic polynomial, or NP. If a problem is NP-hard, then by definition any problem which is NP can be converted into this problem in polynomial time. Despite the name, an NP-hard problem is not necessarily NP. This is often viewed with the concept of an oracle, a mythical algorithm which may solve an NP-hard problem in polynomial time. If any NP problem may be converted to an NP-Hard problem in polynomial time, then through the use of an oracle the problem may be converted, solved, and then converted back all in polynomial time. This would mean that the existence of an oracle for any NP-Hard problem would generate a polynomial time algorithm for any NP problem. NP-Complete is thus a problem which can both be solved in polynomial time on a nondeteriministic turing machine, and which can be converted into an NP problem in polynomial time. Disproving P vs NP would show that no NP-hard problem has a polynomial time algorithm for a deterministic turing machine. A common example of an NP-complete problem is the boolean satisfiabillity problem. Given a logic circuit with n inputs and one output can you find an input which generates an output of 1 (true). THis could be done by checking all inputs, but the number of possible inputs to check would increase exponentially (non polynomially) as the number of inputs increased, so the time complexity becomes NP. 3SAT is a representation of this problem (also np-complete) which constrains the logic circuits to the anding/union/production of many three input or gates whose inputs may be inverted. Because of its simplistic computer representation and constrained framing, 3SAT is a popular np-complete problem to test algorithms on, and the one that GradSat attempts to solve.



What is GradSat

GradSat argues that conceptually, all current 3SAT solvers are conceptually similar to trying to find the shortest distance between two locations, but only using foot paths and roads. As they may only change the binary input discretely, they pay only step along constrained paths. GradSat represents logic gates through a continuous polynomial, which allows it to test values between 0 and 1. It may effectively step of the path and cut across the field to get to a location faster.

Firstly, represent the values of True and False as  1 and 0.

 | a b | a AND b | a x b | a NAND b | 1 - a x b |
 |-----|---------|-------|----------|-----------|
 | 0 0 |    0    |   0   |     1    |     1     |
 | 0 1 |    0    |   0   |     1    |     1     |
 | 1 0 |    0    |   0   |     1    |     1     |
 | 1 1 |    1    |   1   |     0    |     0     |
 
 
 By representing the NAND gate through addition and multiplication, as it is a universal logic gate, all logic gates may be represented through the composition of this polynomial.
 
 NOT a = a NAND a = 1-a^2 (or very reasonably just 1 - a)
 a OR b = (NOT a) NAND (NOT b) = 1 - (1-a^2)(1-b^2) (again, or just 1-(1-a)(1-b))
 
 In this way, values of (a,b) such as (0.7, 0.2) may be checked, rather than being constrained to 1 and 0. The next stage of the algorithm is to notice that the logic gate representations provided are monotonic with respect to their inputs. Their partial derivatives are either >=0 or <=0. This means that when each input is constrained to the range [0,1] then the maxima and minima must occur when each input value is either 0 or 1, and those maxima and minimar are 1 and 0. Equally, the composite of monotonic functions must be monotonic. This means that any stationary point which exists within the range but not at the binary points must be a saddle point if there exists a valid input which outputs a 1. From this reasoning, gradient ascent may be applied to quickly find a maximal input if one exists, solving the 3SAT problem.
 
 The algorithm
 
 Take as input a 3SAT logic circuit. This is commonly represented as a list of length three lists, with the length three lists containing the input parameters (often as integers) and a representation of negation (negative integers).
 
 Convert this representation to a continuous polynomial (the simplifications suggested for OR gates and NOT gates do not break the monotonicity condition, so  shouldn't affect it, but I don't know).
 
 Set all inputs to 0.5 and calculate the gradient. The parameter whose partial derivative has the greatest non zero magnitude is set to 0 if the derivative is negative or 1 if the derivative is positive. If all partial derivatives are 0 then an arbitrary input parameter is set to 1. This process is repeated with the new input vector until all parameters are either 0 or 1.
 
 If the output of the final input vector is 1, then the 3SAT problem is satisfiable by that input. If it is 0 then the 3SAT problem is deemed unsatisfied. The Time Complexity to compute the polynomial is proportional to the number of logic gates, which is proportional to the input size, so is O(n). The time complexity to calculate the gradient is proportional to the time complexity of the polynomial evaluation so is also O(n). This algorithms loops proportionaly to the number of inputs, making the entire algorithm O(n^2).
 
 Though it would be silly to think that this algorithm would completely solve p vs np, if the conditions of its failure can be predicted it may still prove to be a an effective heuristic solution.
