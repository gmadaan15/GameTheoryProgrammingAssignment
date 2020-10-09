from NFGGameParser import InvalidFileException
from EFGGameParser import EfgGameParser

for count in range(1,6):
    file_name = "EfgTestCases/test_case_" + str(count)

    try:
        game = EfgGameParser.parse_efg_file(file_name)
        print(game.compute_spnes())
    except InvalidFileException as e:
        print(e)
    #except Exception as e:
        #print("other exception :\n" + str(e))