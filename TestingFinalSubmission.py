from Final_submission import *

for count in range(1,6):
    file_name = "Final_Submission_Test_Cases/test_case_" + str(count)

    try:
       if (count == 3):
           result =  computePSNE(file_name)
           print("que 3 :" , result)
       elif (count == 4):
           result = efg_NFG( file_name )
           print("que 4 :", result)
       elif (count == 5):
           result = computeSPNE(file_name)
           print("que 5 : ", result)

    except InvalidFileException as e:
        print(e)
    #except Exception as e:
    #   print(e)