from aimacode.planning import Action
from aimacode.search import Problem
from aimacode.utils import expr
from lp_utils import decode_state

import time


# Timer dictionary
timer_dict = {}

def add_to_timer(name, time_val):
       
    # First time calling timer?
    if 'n' in timer_dict:
        cur_n = timer_dict['n']
        timer_dict['n'] = cur_n + 1
    else:
        timer_dict['n'] = 0
    
    if name in timer_dict:
       #print('In timer, accing ', name)
        cur_time = timer_dict[name]
        timer_dict[name] = cur_time + time_val
    else:
        #print('In timer, adding ', name)
        timer_dict[name] = time_val
        
    if int(timer_dict['n']) % 1000000 == 0:
        print('Timer info:', ' count==', timer_dict['n'])
        display_timer()
            
def display_timer():
    tot_time = 0.0
    for cur_key in timer_dict:
        if cur_key == 'n':
            continue
        tot_time += timer_dict[cur_key]
        
    for cur_key in timer_dict:
        if cur_key == 'n':
            continue
        print('Function: ', cur_key, ' time_frac=', 
              timer_dict[cur_key]/tot_time)
        
        

class PgNode():
    """Base class for planning graph nodes.

    includes instance sets common to both types of nodes used in a planning graph
    parents: the set of nodes in the previous level
    children: the set of nodes in the subsequent level
    mutex: the set of sibling nodes that are mutually exclusive with this node
    """

    def __init__(self):
        self.parents = set()
        self.children = set()
        self.mutex = set()
        
        
        
   
        
        

    def is_mutex(self, other) -> bool:
        """Boolean test for mutual exclusion

        :param other: PgNode
            the other node to compare with
        :return: bool
            True if this node and the other are marked mutually exclusive (mutex)
        """
        if other in self.mutex:
            return True
        return False

    def show(self):
        """helper print for debugging shows counts of parents, children, siblings

        :return:
            print only
        """
        print("{} parents".format(len(self.parents)))
        print("{} children".format(len(self.children)))
        print("{} mutex".format(len(self.mutex)))


class PgNode_s(PgNode):
    """A planning graph node representing a state (literal fluent) from a
    planning problem.

    Args:
    ----------
    symbol : str
        A string representing a literal expression from a planning problem
        domain.

    is_pos : bool
        Boolean flag indicating whether the literal expression is positive or
        negative.
    """

    def __init__(self, symbol: str, is_pos: bool):
        """S-level Planning Graph node constructor

        :param symbol: expr
        :param is_pos: bool
        Instance variables calculated:
            literal: expr
                    fluent in its literal form including negative operator if applicable
        Instance variables inherited from PgNode:
            parents: set of nodes connected to this node in previous A level; initially empty
            children: set of nodes connected to this node in next A level; initially empty
            mutex: set of sibling S-nodes that this node has mutual exclusion with; initially empty
        """
        PgNode.__init__(self)
        self.symbol = symbol
        self.is_pos = is_pos
        self.__hash = None

    def show(self):
        """helper print for debugging shows literal plus counts of parents,
        children, siblings

        :return:
            print only
        """
        if self.is_pos:
            print("\n*** {}".format(self.symbol))
        else:
            print("\n*** ~{}".format(self.symbol))
        PgNode.show(self)

    def __eq__(self, other):
        """equality test for nodes - compares only the literal for equality

        :param other: PgNode_s
        :return: bool
        """
        return (isinstance(other, self.__class__) and
                self.is_pos == other.is_pos and
                self.symbol == other.symbol)

    def __hash__(self):
        self.__hash = self.__hash or hash(self.symbol) ^ hash(self.is_pos)
        return self.__hash


class PgNode_a(PgNode):
    """A-type (action) Planning Graph node - inherited from PgNode """


    def __init__(self, action: Action):
        """A-level Planning Graph node constructor

        :param action: Action
            a ground action, i.e. this action cannot contain any variables
        Instance variables calculated:
            An A-level will always have an S-level as its parent and an S-level as its child.
            The preconditions and effects will become the parents and children of the A-level node
            However, when this node is created, it is not yet connected to the graph
            prenodes: set of *possible* parent S-nodes
            effnodes: set of *possible* child S-nodes
            is_persistent: bool   True if this is a persistence action, i.e. a no-op action
        Instance variables inherited from PgNode:
            parents: set of nodes connected to this node in previous S level; initially empty
            children: set of nodes connected to this node in next S level; initially empty
            mutex: set of sibling A-nodes that this node has mutual exclusion with; initially empty
        """
        PgNode.__init__(self)
        self.action = action
        self.prenodes = self.precond_s_nodes()
        self.effnodes = self.effect_s_nodes()
        self.is_persistent = self.prenodes == self.effnodes
        self.__hash = None

    def show(self):
        """helper print for debugging shows action plus counts of parents, children, siblings

        :return:
            print only
        """
        print("\n*** {!s}".format(self.action))
        PgNode.show(self)

    def precond_s_nodes(self):
        """precondition literals as S-nodes (represents possible parents for this node).
        It is computationally expensive to call this function; it is only called by the
        class constructor to populate the `prenodes` attribute.

        :return: set of PgNode_s
        """
        
       
        
        nodes = set()
        for p in self.action.precond_pos:
            nodes.add(PgNode_s(p, True))
        for p in self.action.precond_neg:
            nodes.add(PgNode_s(p, False))
            
            
        return nodes

    def effect_s_nodes(self):
        """effect literals as S-nodes (represents possible children for this node).
        It is computationally expensive to call this function; it is only called by the
        class constructor to populate the `effnodes` attribute.

        :return: set of PgNode_s
        """
      
        
        nodes = set()
        for e in self.action.effect_add:
            nodes.add(PgNode_s(e, True))
        for e in self.action.effect_rem:
            nodes.add(PgNode_s(e, False))
        
        return nodes

    def __eq__(self, other):
        """equality test for nodes - compares only the action name for equality

        :param other: PgNode_a
        :return: bool
        """
        return (isinstance(other, self.__class__) and
                self.is_persistent == other.is_persistent and
                self.action.name == other.action.name and
                self.action.args == other.action.args)

    def __hash__(self):
        self.__hash = self.__hash or hash(self.action.name) ^ hash(self.action.args)
        return self.__hash


def mutexify(node1: PgNode, node2: PgNode):
    """ adds sibling nodes to each other's mutual exclusion (mutex) set. These should be sibling nodes!

    :param node1: PgNode (or inherited PgNode_a, PgNode_s types)
    :param node2: PgNode (or inherited PgNode_a, PgNode_s types)
    :return:
        node mutex sets modified
    """
    if type(node1) != type(node2):
        raise TypeError('Attempted to mutex two nodes of different types')
    node1.mutex.add(node2)
    node2.mutex.add(node1)


class PlanningGraph():
    """
    A planning graph as described in chapter 10 of the AIMA text. The planning
    graph can be used to reason about 
    """

    def __init__(self, problem: Problem, state: str, 
                 serial_planning=True,
                 inconsistent_effects_mutex=True,
                 interference_mutex=True,
                 competing_needs_mutex=True,
                 compute_mutexes=True
                 ):
        """
        :param problem: PlanningProblem (or subclass such as AirCargoProblem or HaveCakeProblem)
        :param state: str (will be in form TFTTFF... representing fluent states)
        :param serial_planning: bool (whether or not to assume that only one action can occur at a time)
        Instance variable calculated:
            fs: FluentState
                the state represented as positive and negative fluent literal lists
            all_actions: list of the PlanningProblem valid ground actions combined with calculated no-op actions
            s_levels: list of sets of PgNode_s, where each set in the list represents an S-level in the planning graph
            a_levels: list of sets of PgNode_a, where each set in the list represents an A-level in the planning graph
        """
        
        
        
        
        self.problem = problem
        self.fs = decode_state(state, problem.state_map)
        self.serial = serial_planning
        self.all_actions = self.problem.actions_list + self.noop_actions(self.problem.state_map)
        self.s_levels = []
        self.a_levels = []
        
        # Flags for setting which mutexes to use
        # Or disable all mutex calculations with compute_mutexes
        self.inconsistent_effects_mutex_flag = inconsistent_effects_mutex
        self.interference_mutex_flag = interference_mutex
        self.competing_needs_mutex_flag = competing_needs_mutex
        self.compute_mutexes = compute_mutexes
        
        self.create_graph()
        
        
        
    
            
            

    def noop_actions(self, literal_list):
        """create persistent action for each possible fluent

        "No-Op" actions are virtual actions (i.e., actions that only exist in
        the planning graph, not in the planning problem domain) that operate
        on each fluent (literal expression) from the problem domain. No op
        actions "pass through" the literal expressions from one level of the
        planning graph to the next.

        The no-op action list requires both a positive and a negative action
        for each literal expression. Positive no-op actions require the literal
        as a positive precondition and add the literal expression as an effect
        in the output, and negative no-op actions require the literal as a
        negative precondition and remove the literal expression as an effect in
        the output.

        This function should only be called by the class constructor.

        :param literal_list:
        :return: list of Action
        """
        start = time.time()
        action_list = []
        for fluent in literal_list:
            act1 = Action(expr("Noop_pos({})".format(fluent)), ([fluent], []), ([fluent], []))
            action_list.append(act1)
            act2 = Action(expr("Noop_neg({})".format(fluent)), ([], [fluent]), ([], [fluent]))
            action_list.append(act2)
            
        end = time.time()
        add_to_timer('noop_actions', end-start)
        
        return action_list

    #@profile
    def create_graph(self):
        """ build a Planning Graph as described in Russell-Norvig 3rd Ed 10.3 or 2nd Ed 11.4

        The S0 initial level has been implemented for you.  It has no parents and includes all of
        the literal fluents that are part of the initial state passed to the constructor.  At the start
        of a problem planning search, this will be the same as the initial state of the problem.  However,
        the planning graph can be built from any state in the Planning Problem

        This function should only be called by the class constructor.

        :return:
            builds the graph by filling s_levels[] and a_levels[] lists with node sets for each level
        """
        start = time.time()
      
        # the graph should only be built during class construction
        if (len(self.s_levels) != 0) or (len(self.a_levels) != 0):
            raise Exception(
                'Planning Graph already created; construct a new planning graph for each new state in the planning sequence')

        # initialize S0 to literals in initial state provided.
        leveled = False
        level = 0
        self.s_levels.append(set())  # S0 set of s_nodes - empty to start
        # for each fluent in the initial state, add the correct literal PgNode_s
        for literal in self.fs.pos:
            self.s_levels[level].add(PgNode_s(literal, True))
        for literal in self.fs.neg:
            self.s_levels[level].add(PgNode_s(literal, False))
        # no mutexes at the first level

        # continue to build the graph alternating A, S levels until last two S levels contain the same literals,
        # i.e. until it is "leveled"
        while not leveled:
            self.add_action_level(level)
            if self.compute_mutexes:
                self.update_a_mutex(self.a_levels[level])

            level += 1
            self.add_literal_level(level)
            if self.compute_mutexes:
                self.update_s_mutex(self.s_levels[level])

            if self.s_levels[level] == self.s_levels[level - 1]:
                leveled = True
                    
        end = time.time()
        add_to_timer('create_graph', end-start)

    #@profile
    def add_action_level(self, level):
        """ add an A (action) level to the Planning Graph

        :param level: int
            the level number alternates S0, A0, S1, A1, S2, .... etc the level number is also used as the
            index for the node set lists self.a_levels[] and self.s_levels[]
        :return:
            adds A nodes to the current level in self.a_levels[level]
        """
        # TODO add action A level to the planning graph as described in the Russell-Norvig text
        # 1. determine what actions to add and create those PgNode_a objects
        # 2. connect the nodes to the previous S literal level
        # for example, the A0 level will iterate through all possible actions for the problem and add a PgNode_a to a_levels[0]
        #   set iff all prerequisite literals for the action hold in S0.  This can be accomplished by testing
        #   to see if a proposed PgNode_a has prenodes that are a subset of the previous S level.  Once an
        #   action node is added, it MUST be connected to the S node instances in the appropriate s_level set.

        # Start timing
        start = time.time()

        a_nodes = set()
        
        # All possible actions
        for cur_act in self.all_actions:
            # Temporary node associated with this action
            # May or may not end up being stored
            cur_a_node = PgNode_a(cur_act)
            
            # Are the preconditions of this actions completely
            # contained in the s-levels of the parent level?
            if cur_a_node.prenodes.issubset(self.s_levels[level]):
                # if so, add the temporary node to the list 
                # of action nodes
                a_nodes.add(cur_a_node)
          
                for cur_s_node in self.s_levels[level]:
                    # Connect a-nodes to previous s-level
                    # And vice-versa
                    if cur_s_node in cur_a_node.prenodes:
                        cur_a_node.parents.add(cur_s_node)
                        cur_s_node.children.add(cur_a_node)
                    
                    
        # Add discovered a_nodes to a_level
        self.a_levels.append(a_nodes)
        
        end = time.time()
        add_to_timer('add_action_level', end-start)


    def add_literal_level(self, level):
        """ add an S (literal) level to the Planning Graph

        :param level: int
            the level number alternates S0, A0, S1, A1, S2, .... etc the level number is also used as the
            index for the node set lists self.a_levels[] and self.s_levels[]
        :return:
            adds S nodes to the current level in self.s_levels[level]
        """
        # TODO add literal S level to the planning graph as described in the Russell-Norvig text
        # 1. determine what literals to add
        # 2. connect the nodes
        # for example, every A node in the previous level has a list of S nodes in effnodes that represent the effect
        #   produced by the action.  These literals will all be part of the new S level.  Since we are working with sets, they
        #   may be "added" to the set without fear of duplication.  However, it is important to then correctly create and connect
        #   all of the new S nodes as children of all the A nodes that could produce them, and likewise add the A nodes to the
        #   parent sets of the S nodes
        
        # Start timing
        start = time.time()
        
        s_nodes = set()
        # Find the actions from the preceding level
        for cur_a_node in self.a_levels[level - 1]:
            # Find s nodes that result from the actions
            for cur_s_node in cur_a_node.effnodes:
                # Add s-node to set of s-nodes for this level
                s_nodes.add(cur_s_node)
                
                # Assign self as the child node of the parent node
                cur_a_node.children.add(cur_s_node)
                
                # Assign the parent (action) node
                cur_s_node.parents.add(cur_a_node)
                
                
                
        # Add all the state nodes to the s_levels
        self.s_levels.append(s_nodes)
        
        end = time.time()
        add_to_timer('add_literal_level', end-start)

    #@profile
    def update_a_mutex(self, nodeset):
        """ Determine and update sibling mutual exclusion for A-level nodes

        Mutex action tests section from 3rd Ed. 10.3 or 2nd Ed. 11.4
        A mutex relation holds between two actions a given level
        if the planning graph is a serial planning graph and the pair are nonpersistence actions
        or if any of the three conditions hold between the pair:
           Inconsistent Effects
           Interference
           Competing needs

        :param nodeset: set of PgNode_a (siblings in the same level)
        :return:
            mutex set in each PgNode_a in the set is appropriately updated
        """
        # Start timing
        start = time.time()
        
        nodelist = list(nodeset)
        for i, n1 in enumerate(nodelist[:-1]):
            for n2 in nodelist[i + 1:]:
                # Broken into separate if statements to make sure
                # mutex checks are done as soon as one is found
                # Not clear whether python evaluates all 'or-ed'
                # statements before declaring True after finding
                # that one of them is true (although no real performance
                # effect foound)
                if (self.serialize_actions(n1, n2)):
                    mutexify(n1, n2)
                    continue
                if (self.inconsistent_effects_mutex(n1, n2)):
                    mutexify(n1, n2)
                    continue
                if (self.interference_mutex(n1, n2)):
                    mutexify(n1, n2)
                    continue
                if (self.competing_needs_mutex(n1, n2)):
                    mutexify(n1, n2)
                    continue
                    
        end = time.time()
        add_to_timer('update_a_mutex', end-start)

    def serialize_actions(self, node_a1: PgNode_a, node_a2: PgNode_a) -> bool:
        """
        Test a pair of actions for mutual exclusion, returning True if the
        planning graph is serial, and if either action is persistent; otherwise
        return False.  Two serial actions are mutually exclusive if they are
        both non-persistent.

        :param node_a1: PgNode_a
        :param node_a2: PgNode_a
        :return: bool
        """
        #
        if not self.serial:
            return False
        if node_a1.is_persistent or node_a2.is_persistent:
            return False
        return True

    def inconsistent_effects_mutex(self, node_a1: PgNode_a, node_a2: PgNode_a) -> bool:
        """
        Test a pair of actions for inconsistent effects, returning True if
        one action negates an effect of the other, and False otherwise.

        HINT: The Action instance associated with an action node is accessible
        through the PgNode_a.action attribute. See the Action class
        documentation for details on accessing the effects and preconditions of
        an action.

        :param node_a1: PgNode_a
        :param node_a2: PgNode_a
        :return: bool
        """
        
        # For debugging
        if not self.inconsistent_effects_mutex_flag: return False
        
        # TODO test for Inconsistent Effects between nodes
    
        # Does a2 remove the effect that a1 adds?
        for cur_eff in node_a1.action.effect_add:
            if cur_eff in node_a2.action.effect_rem: return True

        # Does a1 remove effect that a2 adds?
        for cur_eff in node_a2.action.effect_add:
            if cur_eff in node_a1.action.effect_rem: return True

        # No clashing effects found
        return False

    def interference_mutex(self, node_a1: PgNode_a, node_a2: PgNode_a) -> bool:
        """
        Test a pair of actions for mutual exclusion, returning True if the 
        effect of one action is the negation of a precondition of the other.

        HINT: The Action instance associated with an action node is accessible
        through the PgNode_a.action attribute. See the Action class
        documentation for details on accessing the effects and preconditions of
        an action.

        :param node_a1: PgNode_a
        :param node_a2: PgNode_a
        :return: bool
        """
        # TODO test for Interference between nodes
        
        
        # For debugging, test the effect of intereference mutex
        if not self.interference_mutex_flag: return False
        
        # Start timimg
        start = time.time()
        
       
        # Effects of a1 as negative preconditions of a2 
        for cur_eff in node_a1.action.effect_add:
            if cur_eff in node_a2.action.precond_neg: return True
                
        
        # Effects of a2 as negative preconditions of a1
        for cur_eff in node_a2.action.effect_add:
            if cur_eff in node_a1.action.precond_neg: return True
                

        # Effects removed by a1 as preconditions for a2
        for cur_eff in node_a1.action.effect_rem:
            if cur_eff in node_a2.action.precond_pos: return True
                
        # Effects removed by a2 as preconditions for a1
        for cur_eff in node_a2.action.effect_rem:
            if cur_eff in node_a1.action.precond_pos: return True
                
            
        end = time.time()
        add_to_timer('interference_mutex', end-start)

        return False

   # @profile
    def competing_needs_mutex(self, node_a1: PgNode_a, node_a2: PgNode_a) -> bool:
        """
        Test a pair of actions for mutual exclusion, returning True if one of
        the precondition of one action is mutex with a precondition of the
        other action.

        :param node_a1: PgNode_a
        :param node_a2: PgNode_a
        :return: bool
        """
       
        # For debugging: check impact of competing_needs_mutex
        if not self.competing_needs_mutex_flag: return False
        
        # Start timing
        start = time.time()
        
        # Form pairs of preconditions for node_a1, node_a2
        prec_pairs = [(cur_prec_a1, cur_prec_a2)
                      for cur_prec_a1 in node_a1.parents
                      for cur_prec_a2 in node_a2.parents]
        
        # If any of the pairs of preconditions are mutually exclusive,
        # tag the nodes as being mutex
        for cur_pair in prec_pairs:
            if cur_pair[0].is_mutex(cur_pair[1]):
                end = time.time()
                add_to_timer('competing_needs_mutex', end-start)
                return True

        end = time.time()
        add_to_timer('competing_needes_mutex', end-start)
        return False

    def update_s_mutex(self, nodeset: set):
        """ Determine and update sibling mutual exclusion for S-level nodes

        Mutex action tests section from 3rd Ed. 10.3 or 2nd Ed. 11.4
        A mutex relation holds between literals at a given level
        if either of the two conditions hold between the pair:
           Negation
           Inconsistent support

        :param nodeset: set of PgNode_a (siblings in the same level)
        :return:
            mutex set in each PgNode_a in the set is appropriately updated
        """
        
        start = time.time()
        
        nodelist = list(nodeset)
        for i, n1 in enumerate(nodelist[:-1]):
            for n2 in nodelist[i + 1:]:
                if (self.negation_mutex(n1, n2) or 
                   self.inconsistent_support_mutex(n1, n2)):
                    mutexify(n1, n2)
        
        end = time.time()
        add_to_timer('update_s_mutex', end-start)
        

    def negation_mutex(self, node_s1: PgNode_s, node_s2: PgNode_s) -> bool:
        """
        Test a pair of state literals for mutual exclusion, returning True if
        one node is the negation of the other, and False otherwise.

        HINT: Look at the PgNode_s.__eq__ defines the notion of equivalence for
        literal expression nodes, and the class tracks whether the literal is
        positive or negative.

        :param node_s1: PgNode_s
        :param node_s2: PgNode_s
        :return: bool
        """
        # TODO test for negation between nodes
        # If the literal is the same, the logic value should also
        # be the same
        
        if node_s1.symbol == node_s2.symbol:
            if node_s1.is_pos != node_s2.is_pos:
                return True
        else:
            return False
        
        #return node_s1.symbol == node_s2.symbol and node_s1.is_pos != node_s2.is_pos
       

    def inconsistent_support_mutex(self, node_s1: PgNode_s, node_s2: PgNode_s):
        """
        Test a pair of state literals for mutual exclusion, returning True if
        there are no actions that could achieve the two literals at the same
        time, and False otherwise.  In other words, the two literal nodes are
        mutex if all of the actions that could achieve the first literal node
        are pairwise mutually exclusive with all of the actions that could
        achieve the second literal node.

        HINT: The PgNode.is_mutex method can be used to test whether two nodes
        are mutually exclusive.

        :param node_s1: PgNode_s
        :param node_s2: PgNode_s
        :return: bool
        """
        # TODO test for Inconsistent Support between nodes
        # Make sure node_s1's preconditions aren't mutually exclusive with node_s2's preconditions
        
        # Start timing
        start = time.time()
        
        # Build list of pairs of preconditions
        prec_list = [(prec_s1, prec_s2)
                     for prec_s1 in node_s1.parents
                     for prec_s2 in node_s2.parents]
        
        for cur_pair in prec_list:
            if not cur_pair[0].is_mutex(cur_pair[1]):
                end = time.time()
                add_to_timer('inconsistent_support_mutex', end-start)
                return False

        end = time.time()
        add_to_timer('inconsistent_support_mutex', end-start)
        return True

    def h_levelsum(self) -> int:
        """The sum of the level costs of the individual goals (admissible if goals independent)

        :return: int
        """
        level_sum = 0
        # TODO implement
        
        # For each goal in the problem, determine their level cost, 
        # then add the costs together
        # This implementation assumes all goals are positive
        # ALSO: this heuristic does NOT track mutexes
        # There is no check to see that states which match goal
        # states are not mutexed
        # Because of this the pg_levelsum heuristic ultimately
        # does not take advantage of the full complexity
        # of the pg data structure.
        
        # Start timing
        start = time.time()
        
        # Goals found so far
        found_goals = set()
        
        # Loop though all s-levels, checking whether
        # any states match goal states
        # If so, add them to the 'found_goals', and increment
        # level cost
        for level, state_set in enumerate(self.s_levels):
            for cur_state in state_set:
                # Assumes all goals positive
                if (cur_state.is_pos and cur_state.symbol in self.problem.goal 
                                 and cur_state.symbol not in found_goals):
                    found_goals.add(cur_state.symbol)
                    level_sum += level
                    
        # Did we find everything?
        # Maybe some goals are unattainable ...
        if len(found_goals) != len(self.problem.goal):
           return float('inf')
           
        end = time.time()
        add_to_timer('h_levelsum', end-start)
        return level_sum
