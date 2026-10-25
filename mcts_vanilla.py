
from mcts_node import MCTSNode
from p2_t3 import Board
from random import choice
from math import sqrt, log

num_nodes = 1000
explore_faction = 2.

def traverse_nodes(node: MCTSNode, board: Board, state, bot_identity: int):
    while not board.is_ended(state) and len(node.untried_actions) == 0:
        is_opponent = board.current_player(state) != bot_identity

        action = max ( node.child_nodes.keys(), key=lambda a: ucb(node.child_nodes[a], is_opponent) )
        node = node.child_nodes[action]
        state = board.next_state(state, action)
    return node, state

def expand_leaf(node: MCTSNode, board: Board, state):
   if board.is_ended(state):
       return node, state
   if len(node.untried_actions) > 0:
       action = choice(node.untried_actions)
       node.untried_actions.remove(action)
       new_state = board.next_state(state, action)

       child_node = MCTSNode(
           parent=node,
           parent_action=action,
           action_list= list(board.legal_actions(new_state))
       )
       node.child_nodes[action] = child_node
       return child_node, new_state
   
   return node, state
  
def rollout(board: Board, state):
    while not board.is_ended(state):
        actions = list(board.legal_actions(state))
        action = choice(actions)
        state = board.next_state(state, action)
    return state


def backpropagate(node: MCTSNode|None, won: bool):
    while node is not None:
        node.visits += 1
        if won:
            node.wins += 1
        node = node.parent

def ucb(node: MCTSNode, is_opponent: bool):
    if node.visits == 0:
        return float('inf')
    win_rate = node.wins / node.visits
    if is_opponent:
        win_rate = 1 - win_rate
    return win_rate + explore_faction * sqrt(log(node.parent.visits + 1) / node.visits)

def get_best_action(root_node: MCTSNode):
    return max( root_node.child_nodes.keys(),
                key=lambda a: root_node.child_nodes[a].visits )
               
    
def is_win(board: Board, state, identity_of_bot: int):
    # checks if state is a win state for identity_of_bot
    outcome = board.points_values(state)
    assert outcome is not None, "is_win was called on a non-terminal state"
    return outcome[identity_of_bot] == 1

def think(board: Board, current_state, previous_tree=None):
    bot_identity = board.current_player(current_state)
    if previous_tree is None:
        root_node = MCTSNode(
            parent=None,
            parent_action=None,
            action_list=list(board.legal_actions(current_state))
        )
    else:
        root_node = previous_tree
    for _ in range(num_nodes):
        state = current_state
        node = root_node

        node, state = traverse_nodes(node, board, state, bot_identity)
        node, state = expand_leaf(node, board, state)
        terminal_state = rollout(board, state)
        won = is_win(board, terminal_state, bot_identity)
        backpropagate(node, won)

    best_action = get_best_action(root_node)
    
    #print(f"Action chosen: {best_action}")
    return best_action
