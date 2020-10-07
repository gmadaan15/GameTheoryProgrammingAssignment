import re
import numpy as np


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
    # player-1 using 0th strategy
    # player-2 using 2nd strategy
    # player-3 using 1st strategy
    # player-4 using 3rd strategy
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

            no_of_strategies.append(int(count))
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
        for dimension in reversed(no_of_strategies[1:]):
            new_list = []
            for i in range(0,len(last_list), dimension):
                l = last_list[i:i+dimension]
                new_list.append(l)
            #print(new_list)
            last_list = new_list

        # n-d array declaration
        payoff_values = np.array(last_list)

        # create tuples so that it can't be modified later
        no_of_strategies = tuple(no_of_strategies)
        players = tuple(players)


        #print(payoff_values[0][0], payoff_values[0][1], payoff_values[1][0],payoff_values[2][1] )
        # create a dict for output
        game = { cls.GAME_NAME : game_name, cls.PLAYERS : players, cls.GAME_COMMENT : game_comment, cls.NO_OF_STRATEGIES:no_of_strategies ,
                 cls.PAY_OFF_VALUES : payoff_values }
        return game




