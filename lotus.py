from json import load, decoder
from pathlib import Path
from sys import exit
import re
from difflib import ndiff
from argparse import ArgumentParser

class Lotus():
    def __init__(self) -> None:
        self.fileProcess = self.FileProcess()

    class FileProcess():
        def __init__(self) -> None:
            pass

        def getInfo(self, filename: str, metadata: dict) -> None:
            self.filename = Path(filename).name
            self.index = metadata['index']
            self.length = metadata['length']
            self.offset = metadata['offset']
            self.template = metadata['template']
            self.series = metadata['series']
            self.target_folder = Path(metadata['target_folder'])
            self.subfolder = metadata['subfolder']
            self.name_list = [metadata['title_prefix'], metadata['title_rest']]

        def getEpisode(self) -> str:
            self.episode = ''
            try:
                episode = re.findall(r'\d+', self.filename)
                extra_info = r'pv|teaser|trailer|scene|clip|interview|extra|deleted'
                if bool(re.search(extra_info, self.filename, re.IGNORECASE)):
                    self.episode = ''
                elif episode == re.findall(r'\d+', self.template):
                    self.episode = ''
                else:
                    self.episode = episode[int(self.index)]
            except:
                self.episode = ''
            return self.episode
        
        def getExtension(self) -> str:
            if not bool(re.findall(r'\.', self.filename)):
                self.extension = ''
            else:
                self.extension = self.filename.split('.')[-1]
            return self.extension
        
        def getExtra(self) -> str:
            extra = ''
            if bool(self.template):
                extra = self.template
                extra = [x for x in ndiff(extra, self.filename) if x[0] != ' ']
                extra = ''.join([x[2] for x in extra])

                # get rid of self.episode
                try:
                    trim = re.match(r'\d', extra)
                    if trim != None:
                        extra = re.sub(self.episode, r'', extra, 1)
                except:
                    pass
                try:
                    if bool(self.extension):
                        extra = re.sub(r'.' + self.extension, r'', extra, 1)
                except:
                    pass
            self.extra = extra
            return self.extra
        
        def getTargetName(self) -> str:
            if self.series:
                self.getEpisode()
                if bool(self.episode):
                    if self.offset:
                        self.episode = str(int(self.episode) - self.offset)
                    self.name_list.insert(1, '.E' + self.episode.zfill(self.length))
            self.getExtension()
            if bool(self.getExtra()):
                self.name_list.append('.' + self.extra)
            if bool(self.extension):
                self.name_list.append('.' + self.extension)

            self.target_name = ''
            for i in self.name_list:
                self.target_name += i
            return self.target_name
        
        def getTargetFolder(self):
            self.ture_target_folder = self.target_folder
            try:
                if self.subfolder and bool(self.episode):
                    self.ture_target_folder = self.ture_target_folder.joinpath(
                            self.episode.zfill(self.length)
                        )
            except:
                pass
            return self.ture_target_folder
        
        def getTargetPath(self):
            self.target_path = self.ture_target_folder.joinpath(self.target_name)
            return self.target_path

    def getUserInput(self, path: str, jsonfile: str, recursive: bool = False) -> None:
        self.path = Path(path)
        self.jsonfile = Path(jsonfile)
        self.recursive = recursive
        if isinstance(recursive, str):
            if recursive.casefold() in ['f', 'false', '0']:
                self.recursive = False
            elif recursive.casefold() in ['t', 'true', '1']:
                self.recursive = True
            else:
                exit('recursive need to be True or False')
        if isinstance(recursive, int):
            if recursive == 0:
                self.recursive = False
            elif recursive == 1:
                self.recursive = True
            else:
                exit('recursive need to be True or False')

    def checkUserInput(self) -> None:
        for i in [self.path, self.jsonfile]:
            if not i.exists():
                exit(f'"{i}" cannot be found!')
        if not self.path.is_absolute():
            self.path = self.path.resolve()

    def importMetadata(self) -> dict:
        self.metadata = {
            'title': '', 'original_title': '', 'season': '01', 'episode': '', 
            'index': 0, 'series': False, 'target_folder': '', 'subfolder': False, 
            'length': 2, 'offset': 0, 'template': ''
            }
        try:
            with open(self.jsonfile, 'r', encoding='UTF-8') as f:
                data = load(f)
                self.metadata.update(data)
        except decoder.JSONDecodeError:
            exit(f'{self.jsonfile} is not properly json formated!')
        except UnicodeDecodeError:
            exit(f'{self.jsonfile} must use UTF-8 encode!')
        return self.metadata

    def checkMetadata(self) -> None:
        for i in ['title', 'target_folder']:
                if not bool(self.metadata[i]):
                    exit(f'{i} cannot be empty!')
        for j in ['series', 'subfolder']:
            if not isinstance(self.metadata[j], bool): 
                exit('series need to be true or false')
        if self.metadata['series']:
            if not bool(self.metadata['template']):
                exit('template cannot be empty when series is true')
        for l in ['index', 'length', 'offset']:
            if not isinstance(self.metadata[l], int):
                exit(f'{l} need to be a number like 5 neither 5.0 nor 05 nor "5"')
        escape_char = r'\\|/|:|\*|\?|"|<|>|\|'
        # you can use : and \ and / in target_folder
        if bool(re.search(escape_char[7:], self.metadata['target_folder'])):
            exit('invaid character *?"<>| in target_folder')
        for k in self.metadata.keys():
            if k == 'target_folder':
                continue
            if isinstance(self.metadata[k], str):
                if bool(re.search(escape_char, self.metadata[k])):
                    exit(f'invaid character \\/:*?"<>| in {k}')

    def processMetadata(self) -> dict:
        tempdict = {}
        for i in ['index', 'length', 'offset', 'template', 
                'series', 'target_folder', 'subfolder']:
            tempdict.update({i: self.metadata[i]})
        
        if tempdict['series']:
            if self.metadata['season'].isdigit():
                self.metadata['season'] = 'S' + str(self.metadata['season'])
        else:
            self.metadata['season'] = ''

        for l in ['target_folder', 'subfolder', 'template',
                    'series', 'index', 'length', 'offset']:
            self.metadata.pop(l)

        self.title_prefix = ''
        for i in ['title', 'original_title', 'season']:
            if bool(self.metadata[i]):
                self.title_prefix += f'.{self.metadata[i]}'
                self.metadata.pop(i)
        self.title_prefix = self.title_prefix[1:]
        tempdict.update({'title_prefix': self.title_prefix})

        self.title_rest = ''
        for j in self.metadata.values():
            if bool(j):
                self.title_rest += f'.{j}'
        tempdict.update({'title_rest': self.title_rest})

        self.metadata.clear()
        self.metadata.update(tempdict)
        return self.metadata
    
    def autolink(self) -> None:
        def testLinkAction(origin_path: str) -> None:
            if not self.fileProcess.target_path.is_file():
                print(f'{origin_path} <==> {self.fileProcess.target_path} \n')
            else:
                print(f'"{self.fileProcess.target_path}" already exist')
        
        def createLinkFolder() -> None:
            if not self.fileProcess.ture_target_folder.is_dir():
                try:
                    self.fileProcess.ture_target_folder.mkdir(parents=True)
                except:
                    exit(f'no permission to create "{self.fileProcess.ture_target_folder}"')
        # can't softlink in windows due to PermissionError
        def trueLinkAction(origin_path: str) -> None:
            def action(input_path):
                if self.link_option == 'hardlink':
                    self.fileProcess.target_path.hardlink_to(input_path)
                elif self.link_option == 'softlink':
                    self.fileProcess.target_path.symlink_to(input_path, target_is_directory=False)
                else:
                    pass

            try:
                createLinkFolder()
                if not self.fileProcess.target_path.is_file():
                    action(origin_path)
                    print(f'{origin_path} <==> {self.fileProcess.target_path}')
            except:
                exit(f'no permission to create "{self.fileProcess.target_path}"')

        def fileAction(origin_path_file):
            self.fileProcess.getInfo(origin_path_file, self.metadata)
            self.fileProcess.getTargetName()
            self.fileProcess.getTargetFolder()
            self.fileProcess.getTargetPath()

            if self.link_option == 'test':
                testLinkAction(origin_path_file)
            elif self.link_option == 'hardlink' or 'softlink':
                trueLinkAction(origin_path_file)
            else:
                exit('link_option only has 3 choices: test, hardlink, softlink')

        zone = None
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
        self.importMetadata()
        self.checkMetadata()
        self.processMetadata()
        self.autolink()
    
    def cli(self) -> None:
        parser = ArgumentParser(
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
    Lotus().cli()
