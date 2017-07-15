from aimacode.logic import PropKB
from aimacode.planning import Action
from aimacode.search import (
    Node, Problem,
)
from aimacode.utils import expr
from lp_utils import (
    FluentState, encode_state, decode_state,
)
from my_planning_graph import PlanningGraph

from functools import lru_cache


class AirCargoProblem(Problem):
    def __init__(self, cargos, planes, airports, initial: FluentState, goal: list):
        """

        :param cargos: list of str
            cargos in the problem
        :param planes: list of str
            planes in the problem
        :param airports: list of str
            airports in the problem
        :param initial: FluentState object
            positive and negative literal fluents (as expr) describing initial state
        :param goal: list of expr
            literal fluents required for goal test
        """
        self.state_map = initial.pos + initial.neg
        self.initial_state_TF = encode_state(initial, self.state_map)
        Problem.__init__(self, self.initial_state_TF, goal=goal)
        self.cargos = cargos
        self.planes = planes
        self.airports = airports
        self.actions_list = self.get_actions()
        
        # Make a lookup dict for goal states in the state_map
        # Indexed by goal fluent
        # Contains index of item in state_map
        self.goal_lookup = { cur_goal_item : self.state_map.index(cur_goal_item)
                             for cur_goal_item in goal }

    def get_actions(self):
        """
        This method creates concrete actions (no variables) for all actions in the problem
        domain action schema and turns them into complete Action objects as defined in the
        aimacode.planning module. It is computationally expensive to call this method directly;
        however, it is called in the constructor and the results cached in the `actions_list` property.

        Returns:
        ----------
        list<Action>
            list of Action objects
        """

        # TODO create concrete Action objects based on the domain action schema for: Load, Unload, and Fly
        # concrete actions definition: specific literal action that does not include variables as with the schema
        # for example, the action schema 'Load(c, p, a)' can represent the concrete actions 'Load(C1, P1, SFO)'
        # or 'Load(C2, P2, JFK)'.  The actions for the planning problem must be concrete because the problems in
        # forward search and Planning Graphs must use Propositional Logic

        def load_actions():
            """Create all concrete Load actions and return a list

            :return: list of Action objects
            """
            loads = []
            # TODO create all load ground actions from the domain Load action
            
            # Form triplets of cargo, planes, airports
            cta_list = [(cur_cargo, cur_plane, cur_airport)
                        for cur_airport in self.airports
                        for cur_plane in self.planes
                        for cur_cargo in self.cargos]
            
            
            # Build all possible actions
            for cargo, plane, air in cta_list:
                
                # Positive preconditions
                # (no negative preconditions)
                pos_prec = [expr("At({}, {})".format(cargo, air)),
                            expr("At({}, {})".format(plane, air))]
                
                add_effect = [expr("In({}, {})".format(cargo, plane))]
                rem_effect = [expr("At({}, {})".format(cargo, air))]
               
                # Empty list for negative preconditions
                # Build complete Action
                cur_load = Action(expr("Load({}, {}, {})".format(cargo, 
                                                                 plane, 
                                                                 air)),
                                              [pos_prec, []],
                                              [add_effect, rem_effect])
                
                loads.append(cur_load)
            
           
            
            return loads

        def unload_actions():
            """Create all concrete Unload actions and return a list

            :return: list of Action objects
            """
            unloads = []
            # TODO create all Unload ground actions from the domain Unload action
            
            
            # Form triplets of cargo, planes, airports
            cta_list = [(cur_cargo, cur_plane, cur_airport)
                        for cur_airport in self.airports
                        for cur_plane in self.planes
                        for cur_cargo in self.cargos]
            
            # Build all possible actions
            for cargo, plane, air in cta_list:
                pos_prec = [expr("In({}, {})".format(cargo, plane)),
                            expr("At({}, {})".format(plane, air))]
                
                add_effect = [expr("At({}, {})".format(cargo, air))]
                rem_effect = [expr("In({}, {})".format(cargo, plane))]
                
                # Empty list for negative preconditions
                # Build complete Action
                cur_unload = Action(expr("Unload({}, {}, {})".format(cargo, 
                                                                     plane, 
                                                                     air)),
                                [pos_prec, []],
                                [add_effect, rem_effect])
                
                unloads.append(cur_unload)
            
            return unloads

        def fly_actions():
            """Create all concrete Fly actions and return a list

            :return: list of Action objects
            """
            flys = []
            for fr in self.airports:
                for to in self.airports:
                    if fr != to:
                        for p in self.planes:
                            precond_pos = [expr("At({}, {})".format(p, fr)),
                                           ]
                            precond_neg = []
                            effect_add = [expr("At({}, {})".format(p, to))]
                            effect_rem = [expr("At({}, {})".format(p, fr))]
                            fly = Action(expr("Fly({}, {}, {})".format(p, fr, to)),
                                         [precond_pos, precond_neg],
                                         [effect_add, effect_rem])
                            flys.append(fly)
            return flys

        return load_actions() + unload_actions() + fly_actions()

    def actions(self, state: str) -> list:
        """ Return the actions that can be executed in the given state.

        :param state: str
            state represented as T/F string of mapped fluents (state variables)
            e.g. 'FTTTFF'
        :return: list of Action objects
        """
        # TODO implement
        possible_actions = []
        
        # Shamelessly copied from "example_have_cake.py"
        # due to identical functionality
        
        kb = PropKB()
        kb.tell(decode_state(state, self.state_map).pos_sentence())
        for action in self.actions_list:
            is_possible = True
            for clause in action.precond_pos:
                if clause not in kb.clauses: is_possible = False
            for clause in action.precond_neg:
                if clause in kb.clauses: is_possible = False
            if is_possible:
                possible_actions.append(action)
        
        return possible_actions

    def result(self, state: str, action: Action):
        """ Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state).

        :param state: state entering node
        :param action: Action applied
        :return: resulting state after action
        """
        
        
        # TODO implement
        # Shamelessly copied from "example_have_cake.py"
        # due to identical functionality
        new_state = FluentState([], [])
        
        old_state = decode_state(state, self.state_map)
        for fluent in old_state.pos:
            if fluent not in action.effect_rem:
                new_state.pos.append(fluent)
        for fluent in action.effect_add:
            if fluent not in new_state.pos:
                new_state.pos.append(fluent)
        for fluent in old_state.neg:
            if fluent not in action.effect_add:
                new_state.neg.append(fluent)
        for fluent in action.effect_rem:
            if fluent not in new_state.neg:
                new_state.neg.append(fluent)
        
        return encode_state(new_state, self.state_map)

    def goal_test(self, state: str) -> bool:
        """ Test the state to see if goal is reached

        :param state: str representing state
        :return: bool
        """
        kb = PropKB()
        kb.tell(decode_state(state, self.state_map).pos_sentence())
        for clause in self.goal:
            if clause not in kb.clauses:
                return False
        return True

    def h_1(self, node: Node):
        # note that this is not a true heuristic
        h_const = 1
        return h_const

    @lru_cache(maxsize=8192)
    def h_pg_levelsum(self, node: Node):
        """This heuristic uses a planning graph representation of the problem
        state space to estimate the sum of all actions that must be carried
        out from the current state in order to satisfy each individual goal
        condition.
        """
        # requires implemented PlanningGraph class
        pg = PlanningGraph(self, node.state)
        pg_levelsum = pg.h_levelsum()
        return pg_levelsum

    @lru_cache(maxsize=8192)
    def h_ignore_preconditions(self, node: Node):
        """This heuristic estimates the minimum number of actions that must be
        carried out from the current state in order to satisfy all of the goal
        conditions by ignoring the preconditions required for an action to be
        executed.
        """
        # TODO implement (see Russell-Norvig Ed-3 10.2.3  or Russell-Norvig Ed-2 11.2)
       
        # Create list of unmet goals
        # The length of the list is the value of the heuristic
        unmet_goal_list = [cur_fluent
                           for cur_fluent in self.goal
                           if node.state[self.goal_lookup[cur_fluent]] == 'F']
        
        return len(unmet_goal_list)
        
   
    @lru_cache(maxsize=8192)
    def h_pg_levelsum_iem(self, node: Node):
        """Variant of the pg heuristic for analysis purposes.
        Ignores interference_mutex and competing_needs_mutex check.
        """
        # requires implemented PlanningGraph class
        pg = PlanningGraph(self , node.state, interference_mutex=False,
                                             competing_needs_mutex=False)
        pg_levelsum = pg.h_levelsum()
        return pg_levelsum
    
    @lru_cache(maxsize=8192)
    def h_pg_levelsum_int(self, node: Node):
        """Variant of the pg heuristic for analysis purposes.
        Ignores inconsistent_effects_mutex and competing_needs_mutex check.
        """
        # requires implemented PlanningGraph class
        pg = PlanningGraph(self , node.state, inconsistent_effects_mutex=False,
                                              competing_needs_mutex=False)
        pg_levelsum = pg.h_levelsum()
        return pg_levelsum
    
    @lru_cache(maxsize=8192)
    def h_pg_levelsum_cn(self, node: Node):
        """Variant of the pg heuristic for analysis purposes.
        Ignores inconsistent_effects_mutex and interference_mutex check.
        """
        # requires implemented PlanningGraph class
        pg = PlanningGraph(self , node.state, inconsistent_effects_mutex=False,
                                              interference_mutex=False)
        pg_levelsum = pg.h_levelsum()
        return pg_levelsum
    
    
        




def cargo_problem_list_builder(cargos, planes, airports, pos_At, goal):
    
    # Helper function for building expressions
    def build_expr(exp_type, arg1, arg2):
        return expr(exp_type + '('+ arg1 + ', ' + arg2+')') 
    
    '''
    Build air cargo problem
    
    Input: cargos: list of cargos
           planes: list of planes
           airports: list of airports
           pos_At: dictionary specifying locations of cargo and planes
                   key of dict is a cargo or plane, value is 
                   the airport location
           goal  : dictionary specifying the goal location of cargo
                   
    Returns: AirCargoProblem object 
    '''
    
    
    # Positive list is initial state
    pos = [ build_expr('At', cur_key, pos_At[cur_key])
            for cur_key in pos_At.keys() ]
    
    # Initialize neg_list (populated next)
    neg = []
    
    
    # Negative 'At(C, A)' lists: set for any cargo not
    # at a given airport
    neg_at_cargo_list = [build_expr('At', cur_cargo, cur_airport)
                            for cur_cargo in cargos
                            for cur_airport in airports
                            if pos_At[cur_cargo] != cur_airport 
                        ]
    
    # 'At(P, A)' lists: set for any plane not at a given airport
    neg_at_plane_list = [build_expr('At', cur_plane, cur_airport)
                            for cur_plane in planes
                            for cur_airport in airports
                            if pos_At[cur_plane] != cur_airport
                        ]

    # Negative lists contains all 'In' literals
    # Planes are initially unloaded
    neg_in_list = [build_expr('In', cur_cargo, cur_plane)
                    for cur_cargo in cargos
                    for cur_plane in planes
                  ]
    
    neg = neg_at_cargo_list + neg_at_plane_list + neg_in_list
    
    # Build goal
    goal_list = [build_expr('At', cur_cargo, goal[cur_cargo])
                    for cur_cargo in goal.keys() ]
                    
    init = FluentState(pos, neg)
    
    return AirCargoProblem(cargos, planes, airports, init, goal_list)
   
    

def air_cargo_p1() -> AirCargoProblem:
    '''
    Init(At(C1, SFO) ∧ At(C2, JFK) 
	∧ At(P1, SFO) ∧ At(P2, JFK) 
	∧ Cargo(C1) ∧ Cargo(C2) 
	∧ Plane(P1) ∧ Plane(P2)
	∧ Airport(JFK) ∧ Airport(SFO))
    
    Goal(At(C1, JFK) ∧ At(C2, SFO))
    '''
    
    cargos = ['C1', 'C2']
    planes = ['P1', 'P2']
    airports = ['JFK', 'SFO']
    
    
    pos_At = { 'C1' : 'SFO',
               'C2' : 'JFK',
               'P1' : 'SFO',
               'P2' : 'JFK' }
    
    goal_dict = { 'C1' : 'JFK',
                  'C2' : 'SFO' }
    
    
    return cargo_problem_list_builder(cargos, planes, 
                                      airports, pos_At, goal_dict)


def air_cargo_p2() -> AirCargoProblem:
    '''
    Init(At(C1, SFO) ∧ At(C2, JFK) ∧ At(C3, ATL) 
	∧ At(P1, SFO) ∧ At(P2, JFK) ∧ At(P3, ATL) 
	∧ Cargo(C1) ∧ Cargo(C2) ∧ Cargo(C3)
	∧ Plane(P1) ∧ Plane(P2) ∧ Plane(P3)
	∧ Airport(JFK) ∧ Airport(SFO) ∧ Airport(ATL))
    
    Goal(At(C1, JFK) ∧ At(C2, SFO) ∧ At(C3, SFO))
    '''
    
    cargos = ['C1', 'C2', 'C3']
    planes = ['P1', 'P2', 'P3']
    airports = ['SFO', 'JFK', 'ATL']
    
   
    # 'Positive' initial conditions
    # Specify the starting locations of cargo, planes
    # Build a list of expressions
    
    pos_At = { 'C1' : 'SFO',
               'C2' : 'JFK',
               'C3' : 'ATL',
               'P1' : 'SFO',
               'P2' : 'JFK',
               'P3' : 'ATL' }
    
   
    goal_dict = { 'C1' : 'JFK',
                  'C2' : 'SFO',
                  'C3' : 'SFO' }
    
    return cargo_problem_list_builder(cargos, planes, 
                                      airports, pos_At, goal_dict)


def air_cargo_p3() -> AirCargoProblem:
    '''
    Init(At(C1, SFO) ∧ At(C2, JFK) ∧ At(C3, ATL) ∧ At(C4, ORD)
	∧ At(P1, SFO) ∧ At(P2, JFK)
	∧ Cargo(C1) ∧ Cargo(C2) ∧ Cargo(C3) ∧ Cargo(C4)
	∧ Plane(P1) ∧ Plane(P2)
	∧ Airport(JFK) ∧ Airport(SFO) ∧ Airport(ATL) ∧ Airport(ORD))
    Goal(At(C1, JFK) ∧ At(C3, JFK) ∧ At(C2, SFO) ∧ At(C4, SFO))
    '''

    cargos = ['C1', 'C2', 'C3', 'C4']
    planes = ['P1', 'P2']
    airports = ['SFO', 'JFK', 'ATL', 'ORD']
    
   
    # 'Positive' initial conditions
    # Specify the starting locations of cargo, planes
    # Build a list of expressions
    
    pos_At = { 'C1' : 'SFO',
               'C2' : 'JFK',
               'C3' : 'ATL',
               'C4' : 'ORD',
               'P1' : 'SFO',
               'P2' : 'JFK' }
    
    goal_dict = { 'C1' : 'JFK',
                  'C3' : 'JFK',
                  'C2' : 'SFO',
                  'C4' : 'SFO' }
    
    
    return cargo_problem_list_builder(cargos, planes, 
                                      airports, pos_At, goal_dict)