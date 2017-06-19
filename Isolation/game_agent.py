"""Finish all TODO items in this file to complete the isolation project, then
test your agent's strength against a set of known agents using tournament.py
and include the results in your report.
"""
import random
import math


class SearchTimeout(Exception):
    """Subclass base exception for code clarity. """
    pass



def min_dist_func(game, cur_player):
    """ Helper function for custom evaluation
    functions which use the distance to the 
    nearest wall as a feature.
    """
    # Determine distance of player to walls
    y, x = game.get_player_location(cur_player)
    
    top_wall_dist   = y
    bot_wall_dist   = game.height - y
    right_wall_dist = game.width - x
    left_wall_dist  = x

    min_dist = min((top_wall_dist, bot_wall_dist, 
                right_wall_dist, left_wall_dist))
    
    return 1.0/(1.0 + float(min_dist))


def custom_score(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    This is the LCPOM heuristic, as described in the accompanying
    heuristic_analysis.pdf document.
    
    The return value is an optimized linear combination of the 
    avaialble player moves and (the negative of) the opponent moves.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """

    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")
    
    
    
    player_wall_metric   = min_dist_func(game, player)
    opponent_wall_metric = min_dist_func(game, game.get_opponent(player)) 
    
    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
    return float(0.5*own_moves - opp_moves) + (opponent_wall_metric-player_wall_metric)

    

def custom_score_2(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.
    
    This is the DPOW heuristic, as described s described in the accompanying
    heuristic_analysis.pdf document.
    
    The return value is a function of the distance to the closest wall.


    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """
    # If the board is a "game over" scenario, report that
    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")
    
   
    
    player_wall_metric   = min_dist_func(game, player)
    opponent_wall_metric = min_dist_func(game, game.get_opponent(player)) 
    
    return opponent_wall_metric - player_wall_metric 
    


def custom_score_3(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    This is the LCTOT heuristic, as described s described in the accompanying
    heuristic_analysis.pdf document.
    
    The return value is a function of the distance to the closest wall,
    combined with the LCPOM heuristic.
    
    
    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """
    # TODO: finish this function!
    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
    return float(0.5*own_moves - opp_moves)


class IsolationPlayer:
    """Base class for minimax and alphabeta agents -- this class is never
    constructed or tested directly.

    ********************  DO NOT MODIFY THIS CLASS  ********************

    Parameters
    ----------
    search_depth : int (optional)
        A strictly positive integer (i.e., 1, 2, 3,...) for the number of
        layers in the game tree to explore for fixed-depth search. (i.e., a
        depth of one (1) would only explore the immediate sucessors of the
        current state.)

    score_fn : callable (optional)
        A function to use for heuristic evaluation of game states.

    timeout : float (optional)
        Time remaining (in milliseconds) when search is aborted. Should be a
        positive value large enough to allow the function to return before the
        timer expires.
    """
    def __init__(self, search_depth=3, score_fn=custom_score, timeout=10.):
        self.search_depth = search_depth
        self.score = score_fn
        self.time_left = None
        self.TIMER_THRESHOLD = timeout


class MinimaxPlayer(IsolationPlayer):
    """Game-playing agent that chooses a move using depth-limited minimax
    search. You must finish and test this player to make sure it properly uses
    minimax to return a good move before the search time limit expires.
    """

    def get_move(self, game, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        NOTE: This function has been modified from the original version
        in the following ways:
            1. Implements iterative deepening, using the same approach 
               as AlphaBeta. Not clear whether this was actually required
               or not, but it seemed like the fair choice for running
               the tournament (otherwise unfair advantage to AlphaBeta).
               
            2. When the MiniMax search returns a (-1, -1) while legal moves
               remain (i.e. prediction of a loss when playing against 
               an optimal player), get_move() returns a greedy move.
               This avoids "defeatism" and prevents unnecessary forfeits
               (agent may still lose, but possibly not.)
               
            3. If the move is the very first of the game, choose the middle
               of the board. Not positive this the the best opening move,
               but it is a reasonable one. Using a simple first move
               was necessary to pass timing requirements of the project
               assistant for an empty board (allowing the greedy search
               to evaluate first was occasionally failing the timing)

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """
        
        
        
        
        legal_moves = game.get_legal_moves()
        if not legal_moves:
            return (-1, -1)
        
        # Is it the initial move?
        # If so, return center position
        if game.move_count == 0:
            return(int(game.height/2), 
                   int(game.width/2))
        
        best_move = (-1, -1)
        self.time_left = time_left

        # Initialize the best move so that this function returns something
        # in case the search fails due to timeout
        # In order to avoid defeatist behavior, choose a "greedy" move
        # as the fallback.
        # If no better move is succesfully computed (there may in fact
        # be no move to play that doesn't end in a loss against an
        # optimal player), the first legal move is chosen. 
        # This prevents the game from being forfeited even if there is
        # all moves are predicted to lead to loss; the other player 
        # may still play a bad move.
        
        try:
            
            _, greedy_move = max([(self.score(game.forecast_move(m), self), m) 
                                                        for m in legal_moves])                                         
            
            # Start search with a depth of 1
            cur_depth = 1

       
            # The try/except block will automatically catch the exception
            # raised when the timer is about to expire.
            
           
            
            # There are still moves left to play
            # Find them through iterative deepening
            # Loop is terminated only by the timeout exception
            # There is no break from the loop in case of a
            # win or loss, since the retutn from minimax
            # does not carry score information. This means
            # some redundant moves may be investigated
            # until timeout.
            while True:
                #print('Working on depth == ', cur_depth)
                best_move = self.minimax(game, cur_depth)
                cur_depth += 1
            
        except SearchTimeout:
            # Out of time, return best move found so far
            if best_move != (-1, -1):
                return best_move
            else:
                return greedy_move
        
        

    
    def minimax(self, game, depth):
        """Implement the minimax search algorithm as described in the lectures.
        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state
        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting
        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)
        Returns
        ----------
        float
            The score for the current search branch
        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves
        """
        
        
        # minimax_helper is the recurive function within minimax
        # It returns a tuple of (best_score, best_move)
        # But the API requires a return of best_move only, so
        # the top level minimax wraps the minimax_helper
        def minimax_helper(self, game_h, depth_h, maximizing_player):
            if self.time_left() < self.TIMER_THRESHOLD:
                raise SearchTimeout()
    
            # Initialize scores, moves for this board
            results = []
            
            # Curent Point-Of-View
            if maximizing_player:
                POV = self
            else:
                POV = game_h.get_opponent(self)
    
            # Obtain legal moves for this POV
            legal_moves = game_h.get_legal_moves(POV)
    
            # Out of moves? If so, return immediately
            if not legal_moves:
                return (game_h.utility(self), (-1, -1))
    
            # There are still moves left to play ...
            for cur_move in legal_moves:
                # Forecast for the move:
                cur_move_board = game_h.forecast_move(cur_move)
                
                if depth_h == 1:
                    # Reached search bottom
                    # We're about to evaluate leaf nodes, no recursion
                    # Simply evaluate the possible moves from this board
                    score = self.score(cur_move_board, self)
                    
                else:
                    # Not at the bottom yet, keep recursively calling 
                    # the minimax_helper function
                    # Reduce depth by 1
                    # Toggle active player
                    score, _ = minimax_helper(self, 
                                                cur_move_board, 
                                                depth_h - 1, 
                                                not maximizing_player)
                # Save results    
                # Form a tuple of score, move which leads to the score
                results.append((score, cur_move))
    
            # After obtaining all scores, moves for game nodes
            # below this one, choose the best depending on 
            # whether this is the maximizing, minimizing player
            # Choose max, min based on first tuple entry (score)
            if maximizing_player:
                return max(results, key = lambda x : x[0])
            else: 
                return min(results, key = lambda x : x[0])
        
        
        # Start by calling minimax_helper, which will recurse on itself
        # Return only the best move
        _, best_move = minimax_helper(self, game, depth, True)
        return best_move
    
    




class AlphaBetaPlayer(IsolationPlayer):
    """Game-playing agent that chooses a move using iterative deepening minimax
    search with alpha-beta pruning. You must finish and test this player to
    make sure it returns a good move before the search time limit expires.
    """

    def get_move(self, game, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        Modify the get_move() method from the MinimaxPlayer class to implement
        iterative deepening search instead of fixed-depth search.

        **********************************************************************
        NOTE: If time_left() < 0 when this function returns, the agent will
              forfeit the game due to timeout. You must return _before_ the
              timer reaches 0.
        **********************************************************************
        
        NOTE: This function has been modified from the original version
        in the following ways:
               
            1. When the MiniMax search returns a (-1, -1) while legal moves
               remain (i.e. prediction of a loss when playing against 
               an optimal player), get_move() returns a greedy move.
               This avoids "defeatism" and prevents unnecessary forfeits
               (agent may still lose, but possibly not.)
               
            2. If the move is the very first of the game, choose the middle
               of the board. Not positive this the the best opening move,
               but it is a reasonable one. 

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """
        
        legal_moves = game.get_legal_moves()
        if not legal_moves:
            return (-1, -1)
        
        # Is it the initial move?
        # If so, return center position
        if game.move_count == 0:
            return(int(game.height/2), 
                   int(game.width/2))
      
        best_move = (-1, -1)
        self.time_left = time_left

        # Initialize the best move so that this function returns something
        # in case the search fails due to timeout
        # In order to avoid defeatist behavior, choose a "greedy" move
        # as the fallback.
        # If no better move is succesfully computed (there may in fact
        # be no move to play that doesn't end in a loss against an
        # optimal player), the first legal move is chosen. 
        # This prevents the game from being forfeited even if there is
        # all moves are predicted to lead to loss; the other player 
        # may still play a bad move.
        
        _, greedy_move = max([(self.score(game.forecast_move(m), self), m) 
                                                    for m in legal_moves])                                             
        
        # Start search with a depth of 1
        cur_depth = 1

        try:
            # The try/except block will automatically catch the exception
            # raised when the timer is about to expire.
            
           
            
            # There are still moves left to play
            # Find them through iterative deepening
            # Loop is terminated only by the timeout exception
            # There is no break from the loop in case of a
            # win or loss, since the retutn from alphabeta
            # does not carry score information. This means
            # some redundant moves may be investigated
            # until timeout.
            while True:
                #print('Working on depth == ', cur_depth)
                best_move = self.alphabeta(game, cur_depth)
                cur_depth += 1
            
        except SearchTimeout:
            # Out of time, return best move found so far
            if best_move != (-1, -1):
                return best_move
            else:
                return greedy_move
        
       

        

    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf")):
        """Implement depth-limited minimax search with alpha-beta pruning as
        described in the lectures.

        This should be a modified version of ALPHA-BETA-SEARCH in the AIMA text
        https://github.com/aimacode/aima-pseudocode/blob/master/md/Alpha-Beta-Search.md

        **********************************************************************
            You MAY add additional methods to this class, or define helper
                 functions to implement the required functionality.
        **********************************************************************

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        alpha : float
            Alpha limits the lower bound of search on minimizing layers

        beta : float
            Beta limits the upper bound of search on maximizing layers

        Returns
        -------
        (int, int)
            The board coordinates of the best move found in the current search;
            (-1, -1) if there are no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project tests; you cannot call any other evaluation
                function directly.

            (2) If you use any helper functions (e.g., as shown in the AIMA
                pseudocode) then you must copy the timer check into the top of
                each helper function or else your agent will timeout during
                testing.
        """
        
        # alphabeta_helper is the recurive function within minimax
        # It returns a tuple of (best_score, best_move)
        # But the API requires a return of best_move only, so
        # the top level minimax wraps the minimax_helper
        def alphabeta_helper(self, game_h, depth_h, alpha_h, beta_h, maximizing_player):
       
            if self.time_left() < self.TIMER_THRESHOLD:
                raise SearchTimeout()
    
            # Curent Point-Of-View
            if maximizing_player:
                POV = self
            else:
                POV = game_h.get_opponent(self)
    
            # Obtain legal moves for this POV
            legal_moves = game_h.get_legal_moves(POV)
    
            # Out of moves? If so, return immediately
            if not legal_moves:
                return (game_h.utility(self), (-1, -1))
            
            # Initialize Alpha-Beta algorithm
            lo_score, hi_score = (float("inf"), float("-inf"))
            best_move = (-1, -1)
            
         
           
            if depth_h == 1:
                # Reached search bottom
                # We're about to evaluate leaf nodes, no recursion
                # Simply evaluate the possible moves from this board
                if maximizing_player:
                    for cur_move in legal_moves:
                        # Examine all the leaves
                        cur_move_board = game_h.forecast_move(cur_move)
                        score = self.score(cur_move_board, self)
                        
                        # Is the new score better than beta?
                        # If so, we're done searching
                        if score >= beta_h: return (score, cur_move)
                        
                        # Not higher than beta; keep track of new high score,
                        # if available
                        if score > hi_score:
                            hi_score, best_move = (score, cur_move)
                            
                    return (hi_score, best_move)
                
                
                else:
                    # Opposing player
                    for cur_move in legal_moves:
                        # Examine all the leaves
                        cur_move_board = game_h.forecast_move(cur_move)
                        score = self.score(cur_move_board, self)
                        
                        # Is the new score less than alpha?
                        # If so, we're done searching
                        if score <= alpha_h: return (score, cur_move)
                       
                        # Not done, update low score if appropriate
                        if score < lo_score:
                            lo_score, best_move = (score, cur_move)
                            
                    return (lo_score, best_move)
    
    
            # Not search bottom, additional recursion to be done
            if maximizing_player:
                for cur_move in legal_moves:
                    cur_move_board = game_h.forecast_move(cur_move)
                    # Not at the bottom yet, keep recursively calling 
                    # the minimax_helper function
                    # Reduce depth by 1
                    # Toggle active player
                    score, _ = alphabeta_helper(self, 
                                                cur_move_board, 
                                                depth_h - 1, 
                                                alpha_h, beta_h, 
                                                not maximizing_player)
            
                    # Is the new score better than beta?
                    # If so, we're done searching
                    if score >= beta_h: return (score, cur_move)
                    
                     # Not higher than beta; keep track of new high score,
                     # if available
                    if score > hi_score:
                        hi_score, best_move = (score, cur_move)
                    
                    # maximizing player chooses max
                    alpha_h = max(alpha_h, hi_score)
                 
                # maximizing player chooses highest score
                return (hi_score, best_move)
            
            else:
                # Opponent options ...
                for cur_move in legal_moves:
                    cur_move_board = game_h.forecast_move(cur_move)
                    # Not at the bottom yet, keep recursively calling 
                    # the minimax_helper function
                    # Reduce depth by 1
                    # Toggle active player
                    score, _ = alphabeta_helper(self, 
                                                cur_move_board, 
                                                depth_h - 1, 
                                                alpha_h, beta_h, 
                                                not maximizing_player)
                   
                    # Is the new score less than alpha?
                    # If so, we're done searching
                    if score <= alpha_h: return (score, cur_move)
                    
                    # Not done, update lo_score if appropriate
                    if score < lo_score:
                        lo_score, best_move = (score, cur_move)
                        
                    # minimizing player chooses min    
                    beta_h = min(beta_h, lo_score)
                
                # minimizing player chooses lowest score
                return (lo_score, best_move)
            
        # Start by calling alphabeta_helper, which will recurse on itself
        # Return only the best move    
        ret_score, ret_move = alphabeta_helper(self, game, depth, alpha, beta, True)
        return ret_move
