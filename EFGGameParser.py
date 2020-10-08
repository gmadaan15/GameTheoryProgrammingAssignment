import re
from NFGGameParser import InvalidFileException
from itertools import product

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
    def __add_children__ (self, children ):
        self.children = children

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
        root = prefix_traversal[0]
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
        match_obj = re.match('EFG +2 +R +"(.*?)" +{(.*?)}(?: +"(.*?)")?', file_lines[0].rstrip("\n"))

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

