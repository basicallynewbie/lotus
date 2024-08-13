import json

print('please read aboutjson.txt first\n')

jsonDict = {}

def requireInput(required):
    while True:
        inputs = str(input(f'\n{required} is required: '))
        if inputs == '':
            continue
        else:
            break
    jsonDict.update({f'{required}': inputs})

def trueORfalse(condition):
    print('\n"true or t or 1" for True, "false or f or 0" for False, default = False')
    while True:
        inputs = input(f'{condition} (True or False): ')
        if inputs == '':
            inputs = False
            break
        elif inputs.casefold() in ['t', 'true', '1']:
            inputs = True
            break
        elif inputs.casefold() in ['f', 'false', '0']:
                inputs = False
                break
        else:
            continue
    jsonDict.update({f'{condition}': inputs})

def requireInt(integer, default):
    while True:
        try:
            inputs = input(f'\n{integer} (integer: default={default}): ')
            if inputs == '':
                inputs = int(default)
            else:
                inputs = int(inputs)
        except ValueError:
            print(f'{integer} need to be integer.')
            continue
        else:
            break
    jsonDict.update({f'{integer}': inputs})

print('target_folder need human verify because it may not exist!')
requireInput('target_folder')

requireInput('title')

trueORfalse('series')

try:
    if jsonDict['series']:
        season = input('\nseason (default = 01): ') 
        if season == '': season = '01'
        jsonDict.update({'season': season})
except:
    pass

try:
    if jsonDict['season']:

        requireInt('index', 0)

        trueORfalse('subfolder')

        requireInt('length', 2)
    
        requireInt('offset', 0)
except:
    pass

optionList = [
                'original_title', 'template', 'language', 'subtitle', 
                'quality', 'reselution', 'encode', 'country', 
                'year', 'genre', 'group', 'studio', 
                'director', 'writer', 'actor'                  
            ]
def optionChoise():
    for i in optionList:
        userInput = input(f'\n{i} (optional): ')
        jsonDict.update({i: userInput})
optionChoise()

while True:
    try:
        jsonfile = str(input(f'\nthe name of your jsonfile: '))
        if jsonfile == '':
            continue
        open(f'{jsonfile}', 'x', encoding='UTF-8')
    except FileExistsError:
        print(f'{jsonfile} already exist.')
        continue
    else:
        break

with open(f'{jsonfile}', 'w', encoding='UTF-8') as json_file:
    json.dump(jsonDict, json_file)

print(f'{jsonfile} created')
