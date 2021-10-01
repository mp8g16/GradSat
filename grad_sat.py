class GradSat(object):
    """
        Glucose 3 SAT solver.
    """

    def __init__(self, bootstrap_with=None, use_timer=False, incr=False,
            with_proof=False):
        """
            Basic constructor.
        """

        self.glucose = None
        self.status = None
        self.prfile = None

    def solve(self, assumptions=[]):
        """
            Solve internal formula.
        """

        if self.glucose:
            if self.use_timer:
                 start_time = process_time()

            self.status = pysolvers.glucose3_solve(self.glucose, assumptions,
                    int(MainThread.check()))

            if self.use_timer:
                self.call_time = process_time() - start_time
                self.accu_time += self.call_time

            return self.status

    def solve_limited(self, assumptions=[], expect_interrupt=False):
        """
            Solve internal formula using given budgets for conflicts and
            propagations.
        """

        if self.glucose:
            if self.use_timer:
                 start_time = process_time()

            self.status = pysolvers.glucose3_solve_lim(self.glucose,
                    assumptions, int(MainThread.check()), int(expect_interrupt))

            if self.use_timer:
                self.call_time = process_time() - start_time
                self.accu_time += self.call_time

            return self.status

    def conf_budget(self, budget):
        """
            Set limit on the number of conflicts.
        """

        if self.glucose:
            pysolvers.glucose3_cbudget(self.glucose, budget)

    def prop_budget(self, budget):
        """
            Set limit on the number of propagations.
        """

        if self.glucose:
            pysolvers.glucose3_pbudget(self.glucose, budget)

    def interrupt(self):
        """
            Interrupt solver execution.
        """

        if self.glucose:
            pysolvers.glucose3_interrupt(self.glucose)

    def clear_interrupt(self):
        """
            Clears an interruption.
        """

        if self.glucose:
            pysolvers.glucose3_clearint(self.glucose)

    def propagate(self, assumptions=[], phase_saving=0):
        """
            Propagate a given set of assumption literals.
        """

        if self.glucose:
            if self.use_timer:
                 start_time = process_time()

            st, props = pysolvers.glucose3_propagate(self.glucose,
                    assumptions, phase_saving, int(MainThread.check()))

            if self.use_timer:
                self.call_time = process_time() - start_time
                self.accu_time += self.call_time

            return bool(st), props if props != None else []

    def set_phases(self, literals=[]):
        """
            Sets polarities of a given list of variables.
        """

        if self.glucose:
            pysolvers.glucose3_setphases(self.glucose, literals)

    def get_status(self):
        """
            Returns solver's status.
        """

        if self.glucose:
            return self.status

    def get_model(self):
        """
            Get a model if the formula was previously satisfied.
        """

        if self.glucose and self.status == True:
            model = pysolvers.glucose3_model(self.glucose)
            return model if model != None else []

    def get_core(self):
        """
            Get an unsatisfiable core if the formula was previously
            unsatisfied.
        """

        if self.glucose and self.status == False:
            return pysolvers.glucose3_core(self.glucose)

    def get_proof(self):
        """
            Get a proof produced when deciding the formula.
        """

        if self.glucose and self.prfile:
            self.prfile.seek(0)
            return [line.rstrip() for line in self.prfile.readlines()]

    def time(self):
        """
            Get time spent for the last call to oracle.
        """

        if self.glucose:
            return self.call_time

    def time_accum(self):
        """
            Get time accumulated for all calls to oracle.
        """

        if self.glucose:
            return self.accu_time

    def nof_vars(self):
        """
            Get number of variables currently used by the solver.
        """

        if self.glucose:
            return pysolvers.glucose3_nof_vars(self.glucose)

    def nof_clauses(self):
        """
            Get number of clauses currently used by the solver.
        """

        if self.glucose:
            return pysolvers.glucose3_nof_cls(self.glucose)

    def accum_stats(self):
        """
            Get accumulated low-level stats from the solver. This includes
            the number of restarts, conflicts, decisions and propagations.
        """

        if self.glucose:
            return pysolvers.glucose3_acc_stats(self.glucose)

    def enum_models(self, assumptions=[]):
        """
            Iterate over models of the internal formula.
        """

        if self.glucose:
            done = False
            while not done:
                self.status = self.solve(assumptions=assumptions)
                model = self.get_model()

                if model is not None:
                    self.add_clause([-l for l in model])  # blocking model
                    yield model
                else:
                    done = True

    def add_clause(self, clause, no_return=True):
        """
            Add a new clause to solver's internal formula.
        """

        if self.glucose:
            res = pysolvers.glucose3_add_cl(self.glucose, clause)

            if res == False:
                self.status = False

            if not no_return:
                return res

    def add_atmost(self, lits, k, no_return=True):
        """
            Atmost constraints are not supported by Glucose.
        """

        raise NotImplementedError('Atmost constraints are not supported by Glucose.')

    def append_formula(self, formula, no_return=True):
        """
            Appends list of clauses to solver's internal formula.
        """

        if self.glucose:
            res = None

            if type(formula) == CNFPlus and formula.atmosts:
                raise NotImplementedError('Atmost constraints are not supported by Glucose3')

            for clause in formula:
                res = self.add_clause(clause, no_return)

                if not no_return and res == False:
                    return res

            if not no_return:
                return res
