from NFGGameParser import NfgGameParser,InvalidFileException
import numpy as np



def find_psne(file_name):

    # parse the file and get me all the required details
    game = NfgGameParser.parse_nfg_file(file_name)

    no_of_strategies = game["no_of_strategies"]
    no_of_players = len(game["players"])
    pay_off_values = game["pay_off_values"]

    # since the no of players is unknown, we need to enumerate all the strategy profile possibilities
    # RECURSIVELY
    def enumerate_strategies (playerIdx, no_of_strategies, all_strategies):

        if len(no_of_strategies)==1:
            for strategy in range(no_of_strategies[0]):
                all_strategies.append(np.array([strategy]))
            #print(other_player_strategies)
            return

        enumerate_strategies(playerIdx, no_of_strategies[1:], all_strategies)
        new_add = []
        for strategy in range(no_of_strategies[0]):
            for idx in range(len(all_strategies)):
                next_player_strategy = all_strategies[idx]
                if strategy == 0:
                    all_strategies[idx] = np.concatenate ((next_player_strategy, np.array([0])))
                    continue
                copy_next_player_strategy = np.copy(next_player_strategy)
                copy_next_player_strategy[len(copy_next_player_strategy)-1] = strategy
                new_add.append(copy_next_player_strategy)
        for elm in new_add:
            all_strategies.append(elm)
        return

    all_psne_candidates = {}
    all_strategies = []
    # for each player ,we will find its best response for every other players's strategy,
    # if they all select the same one, than that is a psne
    for playerIdx in range(no_of_players):

        #print(no_of_strategies)
        if len(all_strategies) == 0:
            enumerate_strategies(playerIdx, list(no_of_strategies), all_strategies)

        #print(all_strategies)
        # for every other player strategy
        for other_player_strategy in all_strategies:
            index = other_player_strategy.tolist()
            index.append(playerIdx)

            # no need to enumerate player's own strategy
            if (index[no_of_players - playerIdx-1] != 0 ):
                continue
            max_payoff_indexes = []
            max_payoff = float('-inf')

            # player will try each strategy and select the best ones
            for strategy in range(no_of_strategies[playerIdx]):
                index[no_of_players - playerIdx -1] = strategy
                index_tuple = tuple(index)

                pay_off = pay_off_values.item(index_tuple)
                #print(index_tuple, pay_off)

                if pay_off > max_payoff:
                    max_payoff = pay_off
                    max_payoff_indexes = [index_tuple]

                elif pay_off == max_payoff:
                    max_payoff_indexes.append(index_tuple)
            #print(max_payoff_indexes, )
            for cand in max_payoff_indexes:
                cand = cand[:len(cand)-1]
                #cand = reversed(cand)
                if cand in all_psne_candidates:
                    all_psne_candidates[cand]+=1
                    continue
                all_psne_candidates[cand] = 1
    #print(all_psne_candidates)

    # output result format, no need to worry if you understand all_psne_candidates
    result = []
    for i, (k, v) in enumerate(all_psne_candidates.items()):
        if v != no_of_players:
            continue
        psne = []
        k = list(k)
        k.reverse()
        for idx in range(len(k)):
            for strategy in range(no_of_strategies[idx]):
                if strategy != k[idx]:
                    psne.append( 0 )
                    continue
                psne.append(1)
        result.append(psne)

    return result





for count in range(5,6):
    file_name = "NfgTestCases/test_case_" + str(count)

    try:
        #game = NfgGameParser.parse_nfg_file(file_name)
        #print(game)
        result = find_psne( file_name )
        print(result)
    except InvalidFileException as e:
        print(e)





