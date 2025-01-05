from json import load, decoder
from pathlib import Path
from sys import exit
from re import search, findall, sub, IGNORECASE
from difflib import ndiff, SequenceMatcher
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from time import time, strftime, localtime
from collections import deque
import _locale
_locale._getdefaultlocale = (lambda *args: ['en_US', 'utf8'])

class ProcessData:
    metadata = {'title': '', 'original_title': '', 'season': '01'}
    reference = {
        'subfolder': False,  'series': False, 'no_extra': False,
        'target_folder': '', 'episode_symbol': 'E', 'template': '', 
        'separator': '.', 'index': 0, 'length': 2, 'offset': 0, 
        'escape': [], 'ignore': [], 'replace': {}, 'manual': {},
        'ratio': 0.5
        }

class JsonProcess:
    ESCAPE_CHAR = r'\\|/|:|\*|\?|"|<|>|\|'

    def __init__(self, jsonfile: str) -> None:
        self.jsonfile = jsonfile
        if not Path(self.jsonfile).exists():
            exit(f'"{self.jsonfile}" cannot be found!')

    def loadJson(self) -> None:
        try:
            with open(self.jsonfile, 'r') as f:
                data = load(f)
                if not 'metadata' in data:
                    exit(f'{self.jsonfile} must contain metadata!')
                ProcessData.metadata.update(data['metadata'])
                try:
                    ProcessData.reference.update(data['reference'])
                except:
                    pass
        except decoder.JSONDecodeError:
            exit(f'{self.jsonfile} is not properly json formated!')
        except UnicodeDecodeError:
            exit(f'cannot decode {self.jsonfile}!')

    def checkReferenceBool(self) -> None:
        for j in ['series', 'subfolder', 'no_extra']:
            if not isinstance(ProcessData.reference[j], bool): 
                exit(f'reference {j} need to be True or False!')

    def checkReferenceStr(self) -> None:
        if not bool(ProcessData.reference['target_folder']):
            ProcessData.reference['target_folder'] = str(Path().absolute())
        if len(ProcessData.reference['separator']) > 1:
            exit('reference separator can only hold less than 2 character!')
        if ProcessData.reference['series']:
            if not bool(ProcessData.reference['template']):
                exit('reference template cannot be empty when series is true!')
        for t in ['target_folder', 'template', 'separator', 'episode_symbol']:
            if not isinstance(ProcessData.reference[t], str):
                ProcessData.reference[t] = str(ProcessData.reference[t])
        # you can use : and \ and / in target_folder
        for k in ProcessData.reference.keys():
            if k == 'target_folder':
                if bool(search(self.ESCAPE_CHAR[7:], ProcessData.reference['target_folder'])):
                    exit('invaid character *?"<>| in reference target_folder!')
                continue
            if isinstance(ProcessData.reference[k], str):
                if bool(search(self.ESCAPE_CHAR, ProcessData.reference[k])):
                    exit(f'invaid character \\/:*?"<>| in reference {k}!')

    def checkReferenceInt(self) -> None:
        for l in ['index', 'length', 'offset']:
            if not isinstance(ProcessData.reference[l], int):
                exit(f'reference {l} need to be a number like 5 neither 5.0 nor 05 nor "5"')
        for n in ['index', 'length']:
            if  ProcessData.reference[n] < 0:
                exit(f'reference {n} need to be a number greater than or equal to 0')

    def checkReferenceFloat(self) -> None:
        if not isinstance(ProcessData.reference['ratio'], float):
            exit('reference ratio need to be a number like 0.5 neither 5 nor 5.0 nor 05 nor "5"')
        if not 0 < ProcessData.reference['ratio'] < 1:
            exit('reference ratio need to be a number greater than 0 and less than 1')

    def checkReferenceList(self) -> None:
        # you can use : and \ and / in escape and ignore
        for p in ['escape', 'ignore']:
            if not isinstance(ProcessData.reference[p], list): 
                exit(f'reference {p} need to be a list!')
            for f in ProcessData.reference[p]:
                if not isinstance(f, str): 
                    exit(f'reference {p} can only store string!')
                if bool(search(self.ESCAPE_CHAR[7:], f)):
                    exit(f'invaid character *?"<>| in reference {p}!')

    def checkReferenceDict(self) -> None:
        for d in ['replace', 'manual']:
            if not isinstance(ProcessData.reference[d], dict): 
                exit(f'reference {d} need to be a dictionary!')
            for i in (set(ProcessData.reference[d].keys()) | set(ProcessData.reference[d].values())):
                if not isinstance(i, str): 
                    exit(f'reference {d} can only store string!')
        # you can use every character in replace
        # you can use : and \ and / in manual
        for u in ProcessData.reference['manual'].keys():
            if not bool(search(r'\\|/', u)):
                exit("reference manual's key must be a path")
            if bool(search(self.ESCAPE_CHAR[7:], (u or ProcessData.reference['manual'][u]))):
                exit('invaid character *?"<>| in reference manual!')

    def checkWriteAccess(self) -> None:
        # test write access in target_folder
        try:
            current_time = strftime("%Y_%m_%d_%H-%M-%S", localtime())
            testfolder = Path(ProcessData.reference['target_folder']).joinpath(f'lotus_{current_time}')
            testfolder.mkdir(parents=True)
            testfolder.rmdir()
        except:
            exit(f'have no write access in {ProcessData.reference["target_folder"]}!')

    def checkMetadata(self) -> None:
        if not bool(ProcessData.metadata['title']):
            exit('title cannot be empty!')
        for k in ProcessData.metadata.keys():
            if not isinstance(ProcessData.metadata[k], str):
                ProcessData.metadata[k] = str(ProcessData.metadata[k])
            if bool(search(self.ESCAPE_CHAR, ProcessData.metadata[k])):
                exit(f'invaid character \\/:*?"<>| in metadata {k}')
        if ProcessData.reference['series']:
            if ProcessData.metadata['season'].isdigit():
                ProcessData.metadata['season'] = f"S{ProcessData.metadata['season']}"
        else:
            ProcessData.metadata['season'] = ''

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
        self.checkReferenceBool()
        self.checkReferenceStr()
        self.checkReferenceInt()
        self.checkReferenceFloat()
        self.checkReferenceList()
        self.checkReferenceDict()
        self.checkWriteAccess()
        self.checkMetadata()
        self.processMetadata()

    def __call__(self) -> None:
        self.action()

class FileProcess:
    def __init__(self, file_name: str) -> None:
        self.file_name = file_name
        if bool(search(r'\\|/', self.file_name)):
            exit('file_name can not be a path')

    def getEpisode(self) -> str:
        EXTRA_INFO = r'pv|teaser|trailer|scene|clip|interview|extra|deleted'
        self.dotepisode = ''
        if bool(search(EXTRA_INFO, self.file_name, flags=IGNORECASE)):
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
        if SequenceMatcher(
                a=ProcessData.reference['template'], 
                b=self.file_name
                ).ratio() > ProcessData.reference['ratio']:
            extra = [x for x in ndiff(ProcessData.reference['template'], self.file_name) if x[0] == '+']
            self.extra = ''.join([i[2] for i in extra])
        else:
            self.extra = self.file_name
        
        if ProcessData.reference['series']:
            self.extra = sub(self.episode, r'', self.extra, count=1)
            self.extra = sub(self.dotepisode, r'', self.extra, count=1)
        if bool(self.extension):
            self.extra = sub(f'.{self.extension}', r'', self.extra, count=1)
        if set(findall(r'.', self.extra)) in [{'.', ' '}, {'.'}, {' '}]:
            self.extra = ''
        return self.extra

    def getTargetName(self) -> str:
        name_deque = deque()
        if ProcessData.reference['series']:
            if bool(self.getEpisode()):
                self.true_episode = str(int(self.episode) - ProcessData.reference['offset'])
                self.true_episode = self.true_episode.zfill(ProcessData.reference['length'])
                self.true_episode += self.dotepisode
                name_deque.append(
                    f'{ProcessData.reference["separator"]}'\
                    f'{ProcessData.reference["episode_symbol"]}'\
                    f'{self.true_episode}'
                    )
        name_deque.appendleft(ProcessData.metadata['name_prefix'])
        name_deque.append(ProcessData.metadata['name_postfix'])
        self.getExtension()
        if not ProcessData.reference['no_extra']:
            if bool(ProcessData.reference['template']):
                if bool(self.getExtra()):
                    name_deque.append(ProcessData.reference['separator'] + self.extra)
        if bool(self.extension):
            name_deque.append('.' + self.extension)
        
        self.target_name = ''.join([x for x in name_deque])
        
        for i in ProcessData.reference['replace'].keys():
            self.target_name = sub(i, ProcessData.reference['replace'][i], self.target_name)
        
        return self.target_name

    def getTargetPath(self) -> str:
        target_folder = Path(ProcessData.reference['target_folder'])
        try:
            if ProcessData.reference['subfolder'] and bool(self.episode):
                target_folder = target_folder.joinpath(self.true_episode)
        except:
            pass
        
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
        if self.path.is_file():
            self.dir = self.path.parent
        else:
            self.dir = self.path

    def setLinkOption(self, link_option: str) -> None:
        self.link_option = link_option.casefold()
        if self.link_option not in ['hardlink', 'softlink', 'test']:
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
        if not isinstance(self.recursive, bool):
            exit('recursive was given a wrong type')

    def processList(self, key) -> list:
        for i in range(len(ProcessData.reference[key])):
            if search(r'^\.[\\/]', ProcessData.reference[key][i]):
                ProcessData.reference[key][i] = self.dir.joinpath(ProcessData.reference[key][i])
            else:
                ProcessData.reference[key][i] = Path(ProcessData.reference[key][i])
        return ProcessData.reference[key]

    def processManual(self) -> dict:
        items = {}
        for i in ProcessData.reference['manual'].keys():
            if search(r'^\.[\\/]', i):
                items.update({self.dir.joinpath(i): ProcessData.reference['manual'][i]})
            else:
                items.update({Path(i): ProcessData.reference['manual'][i]})
        ProcessData.reference['manual'] = items
        return ProcessData.reference['manual']

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
        if origin_path in ProcessData.reference['ignore'] \
            or Path(origin_path.name) in ProcessData.reference['ignore']:
            return ''
        
        if origin_path in ProcessData.reference['escape'] \
            or Path(origin_path.name) in ProcessData.reference['escape']:
            target_path = Path(ProcessData.reference['target_folder']).joinpath(origin_path.name)
        elif origin_path in ProcessData.reference['manual'].keys():
            target_path = Path(ProcessData.reference['manual'][origin_path])
        else:
            target_path = Path(FileProcess(origin_path.name)())
        
        if not self.link_option == 'test' and not target_path.parent.exists():
            target_path.parent.mkdir(parents=True)
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
        JsonProcess(jsonfile)()
        self.processList('escape')
        self.processList('ignore')
        self.processManual()
        self.autoLink()
        end = time()
        print(f"Total runtime of the program is {end - begin} s")

    def cli(self) -> None:
        parser = ArgumentParser(
            prog= 'lotus',
            description= 'hardlink or softlink file/s with another name in another path in batch'
            )
        
        subparsers = parser.add_subparsers(dest='option', required=True)
        
        subparsers.add_parser('test', help='print outcome without action')
        subparsers.add_parser('hardlink', 
                                help='Make file/s in path a hard link pointing to target')
        subparsers.add_parser('softlink', 
                                help='Make file/s in path a symbolic link pointing to target')
        
        parser.add_argument('path', type=str, help='The source path of your file or folder')
        parser.add_argument('jsonfile', type=str, help='The source path of your jsonfile')
        parser.add_argument('-r', '--recursive', action='store_true',
                    help='recursively search folder or not, default is not')
        
        args = parser.parse_args()
        self.cmd(args.option, args.path, args.jsonfile, args.recursive)

if __name__ == '__main__':
    Lotus().cli()
