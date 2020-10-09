import os
import os.path
import itertools
import numpy as np

from EFGGameParser import *


def Q4(filename):
    # to format the payoff value for every strategy set
    def payoff_formator(elm):
        return ' '.join(map(str, elm))

    # to format the game representation
    def nfg_formator(name, players, strategies, payoff_matrix):
        return [
            f'NFG 1 R "{name}"',
            '{{ "{}" }} {{ {} }}'.format('" "'.join(map(str, players)), ' '.join(map(str, strategies))),
            ' '.join(map(str, payoff_matrix))
        ]

    game = EfgGameParser.parse_efg_file(filename)
    strategy_profile_set, players_info_set, players_name = list(), list(), list()
    for player in game.players:
        t_action_names, t_players_info_set = list(), list()
        for info_sets in player.info_sets:
            for info_set in info_sets:
                t_action_names.append(info_set.action_names)
                t_players_info_set.append(info_set.info_num)
        players_name.append(player.name)
        strategy_profile_set.append(tuple(itertools.product(*t_action_names)))
        players_info_set.append(t_players_info_set)
    n_dims = tuple(len(strategies) for strategies in strategy_profile_set)

    def find_payoff(payoff_index):
        strategy_profile = tuple(strategy_profile_set[p_idx][s_idx] for p_idx,s_idx in enumerate(payoff_index))
        players_infonum_to_action = tuple(
                dict(
                    tuple(zip(info_nums, strategy_profile[p_idx]))
                ) for p_idx,info_nums in enumerate(players_info_set)
            )

        payoffs = None
        owner_player, info_num, node = game.prefix_traversal[0].owner_player, game.prefix_traversal[0].info_num, game.prefix_traversal[0]
        while node:
            zero_idx = owner_player - 1     # on the assumption that players are indexed from 1
            action = players_infonum_to_action[zero_idx][info_num]
            for child in node.children:
                if action != child[0]:
                    continue
                if (isinstance(child[1], Personal_node)):
                    owner_player, info_num, node = child[1].owner_player, child[1].info_num, child[1]
                if (isinstance(child[1], Terminal_node)):
                    payoffs, node = child[1].payoffs, None      # None is used to end loop
                break
            else:
                print('ERR: no valid child has found')
        assert payoffs, "payoffs should not be empty/None"
        return payoffs

    N = np.empty(n_dims, dtype=object)
    with np.nditer(N, flags=['multi_index', 'refs_ok'], op_flags=['writeonly']) as it:
        for elm in it:
            elm[...] = payoff_formator(find_payoff(it.multi_index))
    return nfg_formator(game.game_name, players_name, n_dims, N.reshape(-1, order='F').tolist())


dirname = 'EfgTestCases'
for filename in os.listdir(dirname):
    try:
        payoffs = Q4(os.path.join(dirname, filename))
        print(f'{filename}:\n{payoffs}\n')
    except Exception as exp:
        print(exp)

