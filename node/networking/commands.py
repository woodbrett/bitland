'''
Created on Mar 26, 2021

@author: brett_wood
'''

def commands(command_text = '', command_number = 0):
    
    command_dict = {
        "getHeaders": 1,
        "data": 2
        }
    
    try:
        command = [command_text, command_dict[command_text]]
    except:
        command = []
    
    if command == []:
        for key, value in command_dict.items():
             if command_number == value:
                 command = [key, command_dict[key]]
                 break
     
    return command


def dataTypes(data_type_text = '', data_type_number = 0):
    
    data_type_dict = {
        "header": 1,
        "transaction": 2,
        "block": 3
        }
    
    try:
        data_type = [data_type_text, data_type_dict[data_type_text]]
    except:
        data_type = []
    
    if data_type == []:
        for key, value in data_type_dict.items():
             if data_type_number == value:
                 data_type = [key, data_type_dict[key]]
                 break
     
    return data_type


if __name__ == '__main__':
    
    print(commands(command_text ="getHeaders"))
    print(commands(command_number =1))
    
    print(dataTypes(data_type_text ="transaction"))
    print(dataTypes(data_type_number =1))    