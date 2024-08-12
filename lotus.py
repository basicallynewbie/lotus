import json
import pathlib
import sys
import re
import difflib
import argparse

class Lotus():
    def __init__(self) -> None:
        pass

    def initMetadata(self) -> None:
        self.metadata = {
            'title': '', 'original_title': '', 'season': '01', 'episode': '',
            'language': '', 'subtitle': '', 'quality': '', 'reselution': '', 
            'encode': '','country': '', 'year': '', 'genre': '', 'group': '',
            'studio': '', 'director': '', 'writer': '', 'actor': '','extra': '', 
            'extension': '', 'index': 0, 'series': False, 'target_folder': '', 
            'template': '', 'subfolder': False, 'length': 2, 'offset': 0
            }
        
        self.target_name = ''
        self.subfolder = ''

    def updateMetadata(self) -> dict:
        try:
            with open(self.jsonfile, 'r', encoding='UTF-8') as f:
                data = json.load(f)
                for i in self.metadata.keys():
                    try:
                        self.metadata[i] = data[i]
                    except KeyError:
                        continue
        except:
            sys.exit(f'{self.jsonfile} is not properly json formated!')
        return self.metadata

    def checkMeatadata(self) -> None:
        for i in ['title', 'target_folder']:
            if not bool(self.metadata[i]):
                sys.exit(f'{i} cannot be empty!')
        for j in ['series', 'subfolder']:
            if not isinstance(self.metadata[j], bool): 
                sys.exit('series need to be true or false')
        for l in ['index', 'length', 'offset']:
            if not isinstance(self.metadata[l], int):
                sys.exit(f'{l} need to be a number like 5 neither 5.0 nor 05 nor "5"')
        escape_char = r'\\|/|:|\*|\?|"|<|>|\|'
        for k in [
            'title', 'original_title', 'season', 'language', 
            'subtitle', 'quality', 'reselution', 'encode', 
            'country', 'year', 'genre', 'group', 'studio', 
            'director', 'writer', 'actor', 'template'
            ]:
            if bool(re.search(escape_char, self.metadata[k])):
                # you can use : and \ and / in target_folder
                sys.exit(f'invaid character: \\/:*?"<>|')
        self.target_folder = pathlib.Path(self.metadata['target_folder'])

    def processMetadata(self, file_name) -> None:
        if self.metadata['series']:
            self.metadata['season'] = 'S' + str(self.metadata['season'])
            try:
                episode = re.findall(r'\d+', file_name)
                episode = episode[int(self.metadata['index'])]
                extra_info = r'pv|teaser|trailer|scene|clip|interview|extra|deleted'
                if bool(re.search(extra_info, file_name, re.IGNORECASE)):
                    self.metadata.pop('episode')
                elif episode == re.findall(r'\d+', self.metadata['reselution'])[0]:
                    self.metadata.pop('episode')
                else:
                    if self.metadata['offset']:
                        episode = str(int(episode) - self.metadata['offset'])
                    episode = episode.zfill(self.metadata['length'])
                    self.metadata['episode'] = 'E' + episode
                    if self.metadata['subfolder']:
                        self.subfolder = episode
            except:
                self.metadata.pop('episode')
        else:
            self.metadata.pop('season')
            self.metadata.pop('episode')

        if not bool(re.findall(r'\.', file_name)):
            self.metadata.pop('extension')
        else:
            self.metadata['extension'] = file_name.split('.')[-1]

        if bool(self.metadata['template']):
            extra = self.metadata['template']
            extra = [x for x in difflib.ndiff(extra, file_name) if x[0] != ' ']
            extra = ''.join([x[2] for x in extra])

            trim = re.match(r'\d', extra)
            if trim != None:
                extra = re.sub(episode, r'', extra)

            if 'episode' in self.metadata:
                extra = re.sub(str(int(episode)), r'', extra)

            if 'extension' in self.metadata:
                extra = re.sub(r'.' + self.metadata['extension'], r'', extra)

            self.metadata['extra'] = extra

        pop_list = ['target_folder', 'series', 'index', 'template', 
                   'subfolder', 'length', 'offset']
        for l in pop_list:
            self.metadata.pop(l)

        for i in self.metadata.values():
            if bool(i):
                self.target_name = self.target_name + f'.{i}'
        self.target_name = self.target_name[1:]

        # avoid rename jsonfile
        if file_name == pathlib.Path(self.jsonfile).name:
            self.target_name = file_name

# get output name
    def getTargetName(self, origin_name: str) -> str:
        self.initMetadata()
        self.updateMetadata()
        self.checkMeatadata()
        self.processMetadata(origin_name)
        return self.target_name
    
# update target_folder if subfolder set to true
    def getTargetFolder(self) -> str:
        self.target_folder = pathlib.Path(self.target_folder).joinpath(self.subfolder)
        return self.target_folder

    def getTargetPath(self) -> str:
        self.target_path = self.target_folder.joinpath(self.target_name)
        return self.target_path
    
    def getUserInput(self, path: str, jsonfile: str, recursive: bool = False) -> None:
        self.path = pathlib.Path(path)
        self.jsonfile = pathlib.Path(jsonfile)
        self.recursive = recursive
        if isinstance(recursive, str):
            if recursive.casefold()in ['f', 'false', '0']:
                self.recursive = False
            elif recursive.casefold() in ['t', 'true', '1']:
                self.recursive = True
            else:
                sys.exit('recursive need to be True or False')
        if isinstance(recursive, int):
            if recursive == 0:
                self.recursive = False
            elif recursive == 1:
                self.recursive = True
            else:
                sys.exit('recursive need to be True or False')

    def checkUserInput(self) -> None:
        for i in [self.path, self.jsonfile]:
            if not i.exists():
                sys.exit(f'"{i}" cannot be found!')
        if not self.path.is_absolute():
            self.path = self.path.resolve()

# function for testing rename
    def getOutputPair(self) -> list:
        self.checkUserInput()
        output_pair = []
        def fileAction(origin_path_file):
            self.getTargetName(origin_path_file.name)
            self.getTargetFolder()
            self.getTargetPath()
            pair_list = []
            pair_list.append(origin_path_file.name)
            pair_list.append(self.target_name)
            output_pair.append(pair_list)
            
        if self.recursive:
            zone = self.path.rglob('*')
        else:
            zone = self.path.iterdir()

        if self.path.is_dir():
            for i in zone:
                if i.is_file():
                    fileAction(i)
        elif self.path.is_file():
            fileAction(self.path)
        else:
            pass

        return output_pair

# function for testing link
    def testLinkAction(self, origin_path: str) -> None:
        if not self.target_path.is_file():
            print(f'{origin_path} <==> {self.target_path} \n')
        else:
            print(f'"{self.target_path}" already exist')
    
    def createLinkFolder(self) -> None:
        if not self.target_folder.is_dir():
            try:
                self.target_folder.mkdir(parents=True)
            except:
                sys.exit(f'no permission to create "{self.target_folder}"')

# can't softlink in windows due to PermissionError
    def trueLinkAction(self, origin_path: str) -> None:
        def action(input_path):
            if self.link_option == 'hardlink':
                self.target_path.hardlink_to(input_path)
            elif self.link_option == 'softlink':
                self.target_path.symlink_to(input_path, target_is_directory=False)
            else:
                pass

        try:
            self.createLinkFolder()
            if not self.target_path.is_file():
                action(origin_path)
                print(f'{origin_path} <==> {self.target_path}')
        except:
            sys.exit(f'no permission to create "{self.target_path}"')

    def autoLink(self) -> None:
        def fileAction(origin_path_file):
            self.getTargetName(origin_path_file.name)
            self.getTargetFolder()
            self.getTargetPath()

            if self.link_option == 'test':
                self.testLinkAction(origin_path_file)
            elif self.link_option == 'hardlink' or 'softlink':
                self.trueLinkAction(origin_path_file)
            else:
                sys.exit('link_option only has 3 choices: test, hardlink, softlink')

        if self.recursive:
            zone = self.path.rglob('*')
        else:
            zone = self.path.iterdir()

        if self.path.is_dir():
            for i in zone:
                if i.is_file():
                    fileAction(i)
        elif self.path.is_file():
            fileAction(self.path)
        else:
            pass

    def execute(self, link_option: str) -> None:
        self.link_option = link_option
        self.checkUserInput()
        self.autoLink()

    def cli(self) -> None:
        parser = argparse.ArgumentParser(
            prog='lotus',
            description='hardlink or softlink file/s to another name in another path'
            )

        subparsers = parser.add_subparsers(dest= 'option', required= True)

        subparsers.add_parser('test', help= 'print outcome without action')
        subparsers.add_parser('hardlink', 
                              help= 'Make file/s in path a hard link pointing to target')
        subparsers.add_parser('softlink', 
                              help= 'Make file/s in path a symbolic link pointing to target')

        parser.add_argument('path', type= str, help= 'The source path of your file or folder')
        parser.add_argument('jsonfile', type= str, help= 'The source path of your jsonfile')
        parser.add_argument('-r', '--recursive', action= 'store_true',
                     help= 'recursively search folder or not, default not')

        args = parser.parse_args()

        self.getUserInput(args.path, args.jsonfile, args.recursive)
        self.execute(args.option)

if __name__ == '__main__':  
    # link = Lotus()
    # link.getUserInput(sys.argv[1], sys.argv[2], sys.argv[3])
    # print(link.getOutputPair())
    # link.execute(sys.argv[4])
    Lotus().cli()
