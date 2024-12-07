from json import load, decoder
from pathlib import Path
from sys import exit
from re import search, findall, sub, IGNORECASE
from difflib import ndiff
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from time import time, strftime, localtime
from collections import deque

class ProcessData:
    metadata = {'title': '', 'original_title': '', 'season': '01'}
    reference = {
        'target_folder': '', 'template': '', 'escape': [],
        'index': 0, 'length': 2, 'offset': 0, 
        'subfolder': False,  'series': False, 'separator': '.'
        }

class JsonProcess:
    ESCAPE_CHAR = r'\\|/|:|\*|\?|"|<|>|\|'

    def __init__(self, jsonfile: str) -> None:
        self.jsonfile = jsonfile
        if not Path(self.jsonfile).exists():
            exit(f'"{self.jsonfile}" cannot be found!')

    def loadJson(self) -> None:
        try:
            with open(self.jsonfile, 'r', encoding='UTF-8') as f:
                data = load(f)
                if not ('metadata' and 'reference') in data:
                    exit(f'{self.jsonfile} must contain metadata and reference!')
                ProcessData.metadata.update(data['metadata'])
                ProcessData.reference.update(data['reference'])
        except decoder.JSONDecodeError:
            exit(f'{self.jsonfile} is not properly json formated!')
        except UnicodeDecodeError:
            exit(f'{self.jsonfile} must use UTF-8 encode!')

    def checkMetadata(self) -> None:
        if not bool(ProcessData.metadata['title']):
            exit('title cannot be empty!')
        for k in ProcessData.metadata.values():
            if bool(search(self.ESCAPE_CHAR, k)):
                exit(f'invaid character \\/:*?"<>| in {ProcessData.metadata}')
        if ProcessData.reference['series']:
            if ProcessData.metadata['season'].isdigit():
                ProcessData.metadata['season'] = 'S' + ProcessData.metadata['season']
        else:
            ProcessData.metadata['season'] = ''

    def checkReference(self) -> None:
        if not bool(ProcessData.reference['target_folder']):
            exit('target_folder cannot be empty!')
        if len(ProcessData.reference['separator']) > 1:
            exit('separator can only hold less than 2 character!')
        for j in ['series', 'subfolder']:
            if not isinstance(ProcessData.reference[j], bool): 
                exit(f'{j} need to be True or False!')
        if ProcessData.reference['series']:
            if not bool(ProcessData.reference['template']):
                exit('template cannot be empty when series is true!')
        for l in ['index', 'length', 'offset']:
            if not isinstance(ProcessData.reference[l], int):
                exit(f'{l} need to be a number like 5 neither 5.0 nor 05 nor "5"')
        # you can use : and \ and / in target_folder
        if bool(search(self.ESCAPE_CHAR[7:], ProcessData.reference['target_folder'])):
            exit('invaid character *?"<>| in target_folder!')
        for k in ProcessData.reference.keys():
            if k == 'target_folder':
                continue
            if isinstance(ProcessData.reference[k], str):
                if bool(search(self.ESCAPE_CHAR, ProcessData.reference[k])):
                    exit(f'invaid character \\/:*?"<>| in reference {k}!')
        # test write access in target_folder
        try:
            current_time = strftime("%Y_%m_%d_%H-%M-%S", localtime())
            testfolder = Path(ProcessData.reference['target_folder']).joinpath(f'lotus_{current_time}')
            testfolder.mkdir(parents=True)
            testfolder.rmdir()
        except:
            exit(f'have no write access in {ProcessData.reference["target_folder"]}!')

    def processMetadata(self) -> dict:
        name_prefix = ''
        for i in ['title', 'original_title', 'season']:
            if bool(ProcessData.metadata[i]):
                name_prefix += f'{ProcessData.reference["separator"]}{ProcessData.metadata[i]}'
            ProcessData.metadata.pop(i)
        name_prefix = name_prefix[1:]
        
        name_postfix = ''
        try:
            for j in ProcessData.metadata.values():
                if bool(j):
                    name_postfix += f'{ProcessData.reference["separator"]}{j}'
        except:
            pass
        
        ProcessData.metadata.clear()
        ProcessData.metadata.update({'name_prefix': name_prefix})
        ProcessData.metadata.update({'name_postfix': name_postfix})
        return ProcessData.metadata

    def action(self) -> None:
        self.loadJson()
        self.checkReference()
        self.checkMetadata()
        self.processMetadata()

    def __call__(self) -> None:
        self.action()

class FileProcess:
    def __init__(self, file_name: str, test: str = 'test') -> None:
        self.file_name = file_name
        if bool(search(r'\\|/', self.file_name, IGNORECASE)):
            exit('file_name can not be a path')
        if test.casefold() == 'test':
            self.test = True
        else:
            self.test = False

    def getEpisode(self) -> str:
        EXTRA_INFO = r'pv|teaser|trailer|scene|clip|interview|extra|deleted'
        self.dotepisode = ''
        if bool(search(EXTRA_INFO, self.file_name, IGNORECASE)):
            self.episode = ''
            return self.episode
        else:
            episode = findall(r'\d+', self.file_name)
            if episode == [] or len(episode) < ProcessData.reference['index']:
                self.episode = ''
                return self.episode
            elif episode == findall(r'\d+', ProcessData.reference['template']):
                self.episode = ''
                return self.episode
            else:
                self.episode = episode[ProcessData.reference['index']]
                string_count = 0
                for y in ndiff(ProcessData.reference['template'], self.file_name):
                    if y[0] != ' ':
                        break
                    string_count += 1
                dotepisode = findall(r'^\.\d+', self.file_name[(string_count + len(self.episode)):])
                if bool(dotepisode):
                    self.dotepisode = dotepisode[0]
                return self.episode

    def getExtension(self) -> str:
        if not bool(findall(r'\.', self.file_name)):
            self.extension = ''
            return self.extension
        else:
            self.extension = self.file_name.split('.')[-1]
            return self.extension

    def getExtra(self) -> str:
        extra = [x for x in ndiff(ProcessData.reference['template'], self.file_name) if x[0] == '+']
        self.extra = ''.join([x[2] for x in extra])
        if ProcessData.reference['series']:
            self.extra = sub(self.episode, r'', self.extra, 1)
            self.extra = sub(self.dotepisode, r'', self.extra, 1)
        if bool(self.extension):
            self.extra = sub(f'.{self.extension}', r'', self.extra, 1)
        rest = set(findall(r'.', self.extra))
        if rest == {'.', ' '} or rest == {'.'} or rest == {' '}:
            self.extra = ''
        return self.extra

    def getTargetName(self) -> str:
        if self.file_name in ProcessData.reference['escape']:
            self.target_name = self.file_name
            return self.target_name
        else:
            name_deque = deque()
            if ProcessData.reference['series']:
                if bool(self.getEpisode()):
                    self.true_episode = str(int(self.episode) - ProcessData.reference['offset'])
                    self.true_episode = self.true_episode.zfill(ProcessData.reference['length'])
                    self.true_episode += self.dotepisode
                    name_deque.append(f'{ProcessData.reference["separator"]}E{self.true_episode}')
            name_deque.appendleft(ProcessData.metadata['name_prefix'])
            name_deque.append(ProcessData.metadata['name_postfix'])
            self.getExtension()
            if bool(ProcessData.reference['template']):
                if bool(self.getExtra()):
                    name_deque.append(ProcessData.reference['separator'] + self.extra)
            if bool(self.extension):
                name_deque.append('.' + self.extension)
            
            self.target_name = ''.join([x for x in name_deque])
            return self.target_name

    def getTargetPath(self) -> str:
        target_folder = Path(ProcessData.reference['target_folder'])
        try:
            if ProcessData.reference['subfolder'] and bool(self.episode):
                target_folder = target_folder.joinpath(self.true_episode)
        except:
            pass
        if not self.test and not target_folder.is_dir():
            target_folder.mkdir(parents=True)
        
        self.target_path = str(target_folder.joinpath(self.target_name))
        return self.target_path

    def __str__(self) -> str:
        self.getTargetName()
        self.getTargetPath()
        return self.target_path

    def __call__(self) -> str:
        self.getTargetName()
        self.getTargetPath()
        return self.target_path

class Lotus:
    def __init__(self) -> None:
        pass

    def setPath(self, path: str) -> None:
        self.path = Path(path)
        if not self.path.exists():
            exit(f'"{self.path}" cannot be found!')
        if not self.path.is_absolute():
            self.path = self.path.resolve()

    def setLinkOption(self, link_option: str) -> None:
        self.link_option = link_option.casefold()
        if link_option not in ['hardlink', 'softlink', 'test']:
            exit('link_option only has 3 choices: test, hardlink, softlink')

    def setRecursive(self, recursive: bool = False) -> None:
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

    def recursiveFilepool(self):
        for i in self.path.rglob('*'):
            if i.is_file():
                yield i

    def unRecursiveFilepool(self):
        for i in self.path.iterdir():
            if i.is_file():
                yield i

    def action(self, origin_path: Path, target_path: Path) -> None:
        pass

    def hardlinkaction(self, origin_path: Path, target_path: Path) -> None:
        target_path.hardlink_to(origin_path)

    def softlinkaction(self, origin_path: Path, target_path: Path) -> None:
        target_path.symlink_to(origin_path, target_is_directory=False)

    def linkAction(self, origin_path: Path) -> str:
        target_path = Path(FileProcess(origin_path.name, self.link_option)())
        # side effect link files
        if not target_path.is_file():
            self.action(origin_path, target_path)
            return f'{origin_path} <={self.link_option}=> {target_path}'
        else:
            return f'"{target_path}" already exist'

    def autoLink(self) -> None:
        if self.link_option == 'hardlink':
            self.action = self.hardlinkaction
        if self.link_option == 'softlink':
            self.action = self.softlinkaction
        if self.path.is_dir():
            file_pool = self.unRecursiveFilepool
            if self.recursive:
                file_pool = self.recursiveFilepool
            with ThreadPoolExecutor() as executor:
                for single_task in executor.map(self.linkAction, file_pool()):
                    print(single_task)
        elif self.path.is_file():
            print(self.linkAction(self.path))
        else:
            pass

    def cmd(self, option: str, path: str, jsonfile: str, recursive: bool = False) -> None:
        begin = time()
        self.setPath(path)
        self.setLinkOption(option)
        self.setRecursive(recursive)
        JsonProcess(jsonfile).action()
        self.autoLink()
        end = time()
        print(f"Total runtime of the program is {end - begin} s")

    def cli(self) -> None:
        parser = ArgumentParser(
            prog= 'lotus',
            description= 'hardlink or softlink file/s to another name in another path in same disk'
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
                    help= 'recursively search folder or not, default is not')
        
        args = parser.parse_args()
        self.cmd(args.option, args.path, args.jsonfile, args.recursive)

if __name__ == '__main__':
    Lotus().cli()
