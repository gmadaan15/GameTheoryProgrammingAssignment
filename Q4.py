import itertools
import numpy as np

from EFGGameParser import *


def Q4(filename):
    game = EfgGameParser.parse_efg_file(filename)
    players_strategies = tuple(tuple(itertools.product(*(tuple(info_set.action_names for info_sets in player.info_sets for info_set in info_sets)))) for player in game.players)
    players_info_set = tuple(tuple(info_set.info_num for info_sets in player.info_sets for info_set in info_sets) for player in game.players)
    n_dims = tuple(len(strategies) for strategies in players_strategies)

    def get_child_node(owner_player, info_num, action):
        for node in game.prefix_traversal:
            if (isinstance(node, Personal_node)) \
                    and node.owner_player == owner_player and node.info_num == info_num:
                for child in node.children:
                    if action == child[0]:
                        if (isinstance(child[1], Personal_node)):
                            return 'p', child[1].owner_player, child[1].info_num
                        if (isinstance(child[1], Terminal_node)):
                            return 't', None, child[1].payoffs
        return None, None, None

    def compute_payoff(payoff_index):
        player_wise_strategies = tuple(players_strategies[p_idx][s_idx] for p_idx,s_idx in enumerate(payoff_index))
        player_wise_info_num_to_action = tuple(dict(tuple(zip(info_nums, player_wise_strategies[p_idx]))) for p_idx,info_nums in enumerate(players_info_set))

        node_type, owner_player, info_num = 'p', game.prefix_traversal[0].owner_player, game.prefix_traversal[0].info_num
        while node_type == 'p':
            zero_idx = owner_player - 1     # on the assumption that players are indexed from 1
            action = player_wise_info_num_to_action[zero_idx][info_num]
            node_type, owner_player, info_num = get_child_node(owner_player, info_num, action)
        assert node_type == 't', "node_type should be terminal node"
        return info_num     # incase of node_type == 't', info_num has payoff

    N = np.empty(n_dims, dtype=object)
    with np.nditer(N, flags=['multi_index', 'refs_ok'], op_flags=['writeonly']) as it:
        for elm in it:
            elm[...] = ' '.join(map(str, compute_payoff(it.multi_index)))
    return N.reshape(-1, order='F')


print(Q4('EfgTestCases/test_case_1'))
print(Q4('EfgTestCases/test_case_2'))
print(Q4('EfgTestCases/test_case_3'))   # information_set is not linearly increasing, will produce wrong result
print(Q4('EfgTestCases/test_case_4'))

