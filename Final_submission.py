import re
import numpy as np
from itertools import product
import os
import os.path
import itertools


'''
Questions are after these classes and helper functions

# test files that we used, kindly make sure that you test it with these formats,
# we made hard assumptions about the file formats
If you face any InvalidFileException, kindly let us know. We are very sure that we would be able to solve it.

********* NFG file *************
NFG 1 R "Test Case 3 : three player game"
{ "Player 1" "Player 2", "Player 3" } { 3 3 2 }
 2 0 4 3 2 3 1 0 2 1 1 1 0 1 0 0 0 3 1 2 3 2 1 0 3 1 1 2 0 3 1 3 2 0 0 0 4 1 2 2 2 2 3 0 3 1 1 2 0 4 3 2 1 0

*********** EFG file *************
EFG 2 R "Untitled Extensive Game" { "Player 1" "Player 2" }
""
p "" 1 1 "" { "Greedy" "Fair" } 0
p "" 2 1 "" { "Reject" "Accept" } 0
t "" 1 "" { 5, 5 }
t "" 2 "" { 0, 0 }
p "" 2 2 "" { "Reject" "Accept" } 0
t "" 3 "" { 9, 1 }
t "" 4 "" { 0, 0 }
'''



# exception to be thrown in case the file format is invalid
class InvalidFileException(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        #print('calling str')
        if self.message:
            return 'InvalidFileException: {0} '.format(self.message)
        else:
            return 'InvalidFileException has been raised'

# parser for parsing nfg game
class NfgGameParser(object):
    # various error messages used by the InvalidFileException
    EXTREME_VERSIONS_MESSAGE = "\nInvalid Format, We have included examples of our test formats of input .nfg file inside NfgTestCases folder, kindly take a look at it and " \
                               "do the corrections that are required "

    WRONG_NUMBER_OF_STRATEGIES = "\nnumber of strategies passed seems to be wrong with respect to number of players, kindly correct it."

    NON_POSITIVE_INTEGER_STRATEGY_VALUES = "\n number of Strategies passed is not an integer value, kindly check"

    WRONG_NUMBER_OF_PAYOFF_VALUES = "\nno of pay off values passed seems to be wrong with respect to number of players, kindly correct it."

    WRONG_PAYOFF_VALUES_FORMAT = "\npayoff values format doesn't seem to be right, kindly check"


    # return game dictionary keys and the value types
    # string
    GAME_NAME = "game_name"

    # tuple of strings
    PLAYERS = "players"

    # tuple of integers
    NO_OF_STRATEGIES = "no_of_strategies"

    # string
    GAME_COMMENT = "game_comment"

    # N-d Array, payoff[0][2][1][3] means
    # player-1 using 3rd strategy
    # player-2 using 1st strategy
    # player-3 using 2nd strategy
    # player-4 using 1st strategy
    PAY_OFF_VALUES = "pay_off_values"

    @classmethod
    # function to parse the NFG file
    def parse_nfg_file( cls, filename ):

        # print the file name for verifying, used it while testing
        print(filename + " : ")

        # read the lines of the file
        with open(filename, 'r') as infile:
            lines = ' '.join(infile.readlines())         # regex will takecare of the newline character

        # regex matching
        # old regex , 'NFG *1 *R *"(.*?)" *{(.*?)} *{(.*?)}(?: *"(.*?)")? *(.+)'
        # NOTE: '\s' will match wide range of whitespace characters, instead of just 'space' character
        match_obj = re.match('NFG\s+1\s+R\s+"(.*?)"\s+{(.*?)}\s+{(.*?)}(?:\s+"(.*?)")?\s+(.+)', lines)

        # try to extract the values
        try:
            game_name, players_str, no_of_strategies_str, game_comment, payoff_values_str = match_obj.groups()
        except AttributeError:
            raise InvalidFileException(cls.EXTREME_VERSIONS_MESSAGE)
        except Exception:
            raise InvalidFileException(cls.EXTREME_VERSIONS_MESSAGE)

        # we have players
        players = [player for player in re.findall('"(.+?)"', players_str.strip())]
        # this needs further processing
        no_of_strategies_str = no_of_strategies_str.strip().split()
        payoff_values_str = payoff_values_str.strip().split()
        #print(no_of_strategies_str)
        #print(payoff_values_str)

        # check the count of strategies against the no of players
        no_of_players = len(players)
        if (len(no_of_strategies_str) != no_of_players):
            raise InvalidFileException(cls.WRONG_NUMBER_OF_STRATEGIES)

        # extract the values in a list
        no_of_strategies = []
        total_combinations = 1
        for count_str in no_of_strategies_str:
            try:
                count = int(count_str)
            except ValueError:
                InvalidFileException(cls.NON_POSITIVE_INTEGER_STRATEGY_VALUES)

            no_of_strategies.append(count)
            total_combinations *= count

        # check the count of strategies against no of players and no of strategies
        if (len(payoff_values_str) / no_of_players != total_combinations):
            raise InvalidFileException(cls.WRONG_NUMBER_OF_PAYOFF_VALUES)

        # extract the payoff values as tuples
        payoff_values = []
        for i in range(0,len(payoff_values_str),no_of_players):
            payoff_single = []
            for j in range (i,i+no_of_players,1):
                try:
                    #print(payoff_values_str[j])
                    # NOTE: consider using float/int instead of eval
                    evaluated = float(payoff_values_str[j])
                    #print(evaluated)
                except Exception:
                    raise InvalidFileException (cls.WRONG_PAYOFF_VALUES_FORMAT)
                payoff_single.append(evaluated)

            #print(payoff_single)
            payoff_single = tuple(payoff_single)
            payoff_values.append(payoff_single)

        # we will use a list of lists to intialise the N-d Array
        # for getting this list of lists, we need to extract data with respect to different dimensions
        last_list = payoff_values
        for dimension in no_of_strategies[0:len(no_of_strategies)-1]:
            new_list = []
            for i in range(0,len(last_list), dimension):
                l = last_list[i:i+dimension]
                new_list.append(l)
            #print(new_list)
            last_list = new_list

        # n-d array declaration
        payoff_values = np.array(last_list)
        #print(payoff_values[3][0][2])
        # create tuples so that it can't be modified later
        no_of_strategies = tuple(no_of_strategies)
        players = tuple(players)


        #print(payoff_values[0][0], payoff_values[0][1], payoff_values[1][0],payoff_values[2][1] )
        # create a dict for output
        game = { cls.GAME_NAME : game_name, cls.PLAYERS : players, cls.GAME_COMMENT : game_comment, cls.NO_OF_STRATEGIES:no_of_strategies ,
                 cls.PAY_OFF_VALUES : payoff_values }
        return game

def cartesian_product(pools):
  result = [[]]
  for pool in pools:
    result = [x+[y] for x in result for y in pool]
  return result

# personal node class and attributes
class Personal_node(object):
    node_name = ""
    owner_player = -64
    info_num = -64
    info_name =""
    action_names=tuple()
    outcome= -64
    outcome_name= ""
    payoffs = tuple()
    children = ()
    # choosen action that gives the best payoff for the subtree
    best_actions = []

    # constructor
    def __init__(self,node_name, owner_player, info_num, info_name, action_names, outcome, outcome_name, payoffs):
        self.node_name=node_name
        self.owner_player = owner_player
        self.info_num =  info_num
        self.info_name = info_name
        self.action_names = action_names
        self.outcome = outcome
        self.outcome_name = outcome_name
        self.payoffs = payoffs

    # provate function, should not be called from outside
    # this should be called while parsing and not while using
    # will be known when full game is intialised
    def __add_children__ (self, children ):
        self.children = children

    # private function, will be set when the full game is intialised
    def __set_best_actions__ (self, actions):
        self.best_actions = actions

        #print( self.owner_player , self.info_num, actions )

    # to print the full info with children
    def __str__(self):
        children_print = "( "
        for child in self.children:
            if (isinstance(child[1], Personal_node)):
                children_print += "( " +child[0] + " - " + str(child[1].owner_player) + " - " + str(child[1].info_num) + " ), "
            else:
                children_print += "( " + child[0] + " - " + str(child[1].node_name) + " - " + str(
                    child[1].payoffs) + " ), "
        children_print += " )"
        out = "PERSONAL_NODE( node_name : {}, owner_player : {}, info_num : {}, info_name : {}, action_names : {}, outcome : {}, outcome_name : {}," \
              " payoffs : {}, children : {} )".format(
            self.node_name, self.owner_player, self.info_num, self.info_name, self.action_names, self.outcome, self.outcome_name, self.payoffs, children_print
        )
        return out

# Terminal node class and attributes
class Terminal_node(object):
    node_name=""
    outcome=-64
    outcome_name = ""
    payoffs = tuple()

    def __init__(self,node_name, outcome, outcome_name, payoffs):
        self.node_name = node_name
        self.outcome = outcome
        self.outcome_name = outcome_name
        self.payoffs = payoffs

    def __str__(self):
        out = "TERMINAL_NODE( node_name : {}, outcome: {}, outcome_name : {} , payoffs : {} )".format(self.node_name, self.outcome,
                                                                                                      self.outcome_name, self.payoffs)
        return out

# even though not used, still class is declared
class Chance_node(object):
    node_name=""
    info_num=-64
    info_name=""
    actions=tuple()
    outcome=-64
    payoffs = tuple()

    def __init__(self, node_name, info_num, info_name, actions, outcome, payoffs):
        self.node_name = node_name
        self.info_num = info_num
        self.info_name = info_name
        self.actions = actions
        self.outcome = outcome
        self.payoffs = payoffs

# Player class and attributes
class Player(object):
    # information sets is a list of sets and personal_nodes is the unique node out of every info_set
    info_sets = tuple()
    name = ""
    strategy_sequences = tuple()
    personal_nodes = ()
    spne_strategies = []


    def __init__(self, name, info_sets):
        self.info_sets = info_sets
        self.name = name

        # lets get every unique info_set, so that the analysis is little bit simplified
        personal_nodes = []
        for set in info_sets:
            personal_nodes.append(set[0])

        self.personal_nodes = tuple(personal_nodes)


    # private function
    # not to be called while using, should only be used while parsing
    # creates a strategy sequence for every player
    def __build_strategy_sequence__(self):
        if len(self.personal_nodes) > 0:
            cartesian_product_actions = list(self.personal_nodes[0].children)
            for idx in range(1, len(self.personal_nodes)):
                cartesian_product_actions = list(product(cartesian_product_actions, self.personal_nodes[idx].children))

            self.strategy_sequences = tuple(cartesian_product_actions)
        #print("Strategy_sequence : " , self.strategy_sequences)

    def __set_psne_strategy__(self):
        if len(self.personal_nodes) > 0:
            best_actions_list = []
            for idx in range(0, len(self.personal_nodes)):
                best_actions_list.append( self.personal_nodes[idx].best_actions )


            self.spne_strategies = cartesian_product(best_actions_list)

    def __str__(self):
        personal_nodes_print = "\n( \n"
        for node in self.personal_nodes:
            personal_nodes_print = personal_nodes_print + str(node) + " ,\n"
        personal_nodes_print = personal_nodes_print + " )\n"
        out = "PLAYER( name : {}, \n personal_nodes : {} )".format( self.name, personal_nodes_print )
        return out

# Efg game class and attributes
class EfgGame(object):
    game_name = ""
    game_comment = ""
    prefix_traversal = ()
    players = ()
    root = None

    def __init__(self,game_name, game_comment, players, prefix_traversal) :
        self.game_name = game_name
        self.players = players
        self.game_comment = game_comment
        self.prefix_traversal = prefix_traversal

        # lets connect all the nodes, once these things are ready
        self.build_tree( 0 )
        self.root = prefix_traversal[0]

        for player in self.players:
            player.__build_strategy_sequence__()



    # can only be called from inside, a private function
    # given the prefix list, build the tree that is assign the children to their respective nodes
    def build_tree(self, index):
        node = self.prefix_traversal[index]
        if isinstance( node, Terminal_node ) :
            return index + 1


        children = []
        last_index = index + 1
        for idx in range(0,len(node.action_names) ):
            children.append((node.action_names[idx], self.prefix_traversal[last_index]))
            new_index = self.build_tree(last_index)
            last_index = new_index

        node.__add_children__( tuple(children) )
        #print("For node {}{}, children are {}".format(node.node_name,node.info_num, children))
        return last_index

    # for every node set their best nodes, later each player can find its psne
    def __set_best_action_for_nodes__(self, index):
        node = self.prefix_traversal[index]
        if isinstance(node, Terminal_node):
            return node.payoffs, index+1

        best_payoffs = [float('-inf')]*len(self.players)
        best_actions = []
        last_index = index + 1

        #print("Start : " , node.owner_player, node.info_num)
        for idx in range(0, len(node.action_names)):
            payoffs , new_index = self.__set_best_action_for_nodes__( last_index )

            # payoff is selected accroding to the player
            owner_player = node.owner_player
            payoff = payoffs[owner_player-1]
            best_payoff = best_payoffs[owner_player-1]

            # for finding the next child
            last_index = new_index

            # update best child if its the best
            if payoff > best_payoff:
                best_payoffs = payoffs
                best_actions = [node.action_names[idx]]
            elif payoff == best_payoff:
                best_actions.append(node.action_names[idx])

        #print( owner_player, node.info_num, best_payoffs, best_actions )

        node.__set_best_actions__(best_actions)

        return best_payoffs, last_index

    # psne
    def compute_spnes(self):
        # set best actions for all nodes and find psne for each player
        self.__set_best_action_for_nodes__(0)
        for player in self.players:
            player.__set_psne_strategy__()

        spnes_list = []
        for player in self.players:
            spnes_list.append(player.spne_strategies)
        #print(spnes_list)
        spnes = cartesian_product(spnes_list)
        return spnes
    def __str__(self):
        players_print = "\n( \n"
        for player in self.players:
            players_print = players_print +  str(player) + " ,\n"
        players_print += " )\n"

        prefix_traversal_print = "\n( \n"
        for node in self.prefix_traversal:
            prefix_traversal_print += str(node) + " ,\n"
        prefix_traversal_print += " )\n"

        out = "EXTENSIVE FORM GAME( game_name : {}, game_comment : {}, \n players : {}, \n prefix_traversal : {} )".format( self.game_name, self.game_comment,
                                                                                                                players_print, prefix_traversal_print )
        return out

# Efg game parser class, takes in a file name and create an EfgGame object
class EfgGameParser(object):
    # various error messages used by the InvalidFileException
    EXTREME_VERSIONS_MESSAGE = "\nInvalid Format, We have included examples of our test formats of input .efg file inside EfgTestCases folder, kindly take a look at it and " \
                               "do the corrections that are required "
    INVALID_NODE_MESSAGE = "some invalid node got detected, we are considering only personal and terminal nodes, kindly check if any other node format is there"

    @classmethod
    # function to parse the NFG file
    def parse_efg_file(cls, filename):
        game_name = ""
        game_comment = ""
        players = []
        prefix_traversal = []

        file_variable = open(filename)
        file_lines= file_variable.readlines()
        #print(file_lines)

        # lets match for the first line
        match_obj = re.match('EFG\s+2\s+R\s+"(.*?)"\s+{(.*?)}(?:\s+"(.*?)")?', ' '.join(file_lines))

        if match_obj is None:
            raise InvalidFileException( cls.EXTREME_VERSIONS_MESSAGE )

        game_name, players_str, game_comment = match_obj.groups()
        players_str = [player for player in re.findall('"(.+?)"', players_str.strip())]

        # need to find all info sets for all players
        players_info_sets = []
        for player_name in players_str:
            #players.append( Player( tuple(), player_name) )
            players_info_sets.append([])

        # will pass through all the nodes and categorise them.
        for index in range( 1, len(file_lines) ):
            line = file_lines[index].rstrip("\n")

            # not considering chance nodes in the file, if given, an error will be raised
            '''
            match_obj = re.match ( 'c +"(.*?)" +(.+?) +"(.*?)"(?: +{(.*?)})? +(.+?)(?: +{(.*?)})?', line )
            if match_obj is not None:
                node_name, info_num, info_name, actions, outcome, payoffs = match_obj.groups()
                info_num, outcome = int(info_num), int(outcome)
                actions = [(action, float(prob)) for action, prob in re.findall('"(.*?)" +(.*?) ', actions + ' ')]
                payoffs = tuple(map(float, payoffs.replace(',', ' ').split()))
                prefix_traversal.append( Chance_node( node_name, info_num, info_name, actions, outcome, payoffs ) )
                continue
            '''

            try:

                # lets match the regex
                match_obj = re.match('p\s+"(.*?)"\s+(\d+?)\s+(\d+?)(?: +"(.*?)")?(?: +{(.*?)})? +(\d+?)(?: +"(.*?)")?(?: +{(.*?)})?', line)
                if match_obj is not None:
                    # get all the attributes documented
                    node_name, owner_player, info_num, info_name, action_names, outcome, outcome_name, payoffs = match_obj.groups()
                    owner_player, info_num, outcome = int(owner_player), int(info_num), int(outcome)
                    action_names = [action_name for action_name in re.findall('"(.+?)"', action_names.strip())]
                    action_names = tuple(action_names)

                    # if payoffs is not given, would not be considered in the analysis
                    if payoffs is not None:
                        payoffs = tuple(map(float, payoffs.replace(',', ' ').split()))
                    else:
                        payoffs = tuple()

                    # checking for same info set coming again
                    same_info_num = False
                    same_info_idx = -16

                    # create an object personal node
                    personal_node = Personal_node(node_name, owner_player, info_num, info_name, action_names, outcome,
                                                  outcome_name, payoffs)

                    # check if its a repeated info set, and note the idx of the already existing info set
                    for idx in range(len(players_info_sets[owner_player-1])):
                        node = players_info_sets[owner_player-1][idx][0]
                        if node.info_num == info_num:
                            same_info_num = True
                            same_info_idx = idx
                            break

                    # this may be the same info, but in a tree its a different node all together,
                    # hence a new node has to be created and appended in the prefix_traversal
                    prefix_traversal.append( personal_node )

                    # if its a new info set personal node, add a new set to the list
                    if same_info_num == False:
                        players_info_sets[owner_player-1].append([personal_node])
                    # else keep it together with the already existing info set
                    else:
                        players_info_sets[owner_player - 1][same_info_idx].append(personal_node)
                    continue

                # matching for terminal node, collect all info and append into prefix traversal
                match_obj = re.match(
                    't +"(.*?)" +(\d+?)(?: +"(.*?)")? +{(.*?)}', line)
                if match_obj is not None:
                    node_name, outcome, outcome_name, payoffs = match_obj.groups()
                    outcome = int(outcome)
                    payoffs = tuple(map(float, payoffs.replace(',', ' ').split()))
                    terminal_node = Terminal_node( node_name, outcome, outcome_name, payoffs )
                    #print(type(terminal_node))
                    prefix_traversal.append(terminal_node)
                    continue
            # find any exception, the format of the node may be wrong
            except Exception as e :
                print(e)
                raise InvalidFileException(cls.INVALID_NODE_MESSAGE)



            # reached till point, than definitly some invalid point detected
            raise InvalidFileException(cls.INVALID_NODE_MESSAGE)

        # collect all players data to make a list of players
        for idx in range(len(players_str)):
            players.append( Player( players_str[idx] , tuple( players_info_sets[idx] ) ))

        #print( game_name, game_comment, players, prefix_traversal )
        # create an object of Efg game
        efg_game = EfgGame(game_name, game_comment, tuple(players), tuple(prefix_traversal))

        return efg_game


#QUESTION 3
def computePSNE(file_name):

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

#QUESTION 4
def efg_NFG( filename ):
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


# QUESTION 5
def computeSPNE(file_name):
    game = EfgGameParser.parse_efg_file(file_name)
    # since every attribute is envolved in for computing spnes, all its other info is already calculated when the game was built
    return game.compute_spnes()



