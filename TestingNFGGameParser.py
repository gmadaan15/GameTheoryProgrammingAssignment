from NFGGameParser import NfgGameParser,InvalidFileException


for count in range(1,12):
    file_name = "NfgTestCases/test_case_" + str(count)

    try:
        game = NfgGameParser.parse_nfg_file(file_name)
        print(game)
    except InvalidFileException as e:
        print(e)
    except Exception as e:
        print("other exception :\n" + str(e))