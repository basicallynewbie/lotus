from json import load, decoder
from pathlib import Path
from sys import exit as exits
from re import search, findall, sub, compile
from difflib import ndiff, SequenceMatcher
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from time import time, strftime, localtime
from collections import deque
from codecs import open as opens

class Data:
    metadata = {'title': '', 'original_title': '', 'season': '01'}
    reference = {
        'series': False, 'subfolder': False, 'no_extra': False, 
        'match_ratio': False, 'keep': False, 'target_folder': '', 
        'template': '', 'episode_symbol': 'E', 'separator': '.', 
        'index': 0, 'length': 2, 'offset': 0, 'ratio': 0.5,
        'escape': [], 'ignore': [], 'replace': {}, 'manual': {}
        }

class JsonProcess:
    ESCAPE_CHAR = r'\\|/|:|\*|\?|"|<|>|\|'

    def __init__(self, jsonfile: str, encode: str = 'utf-8-sig') -> None:
        self.jsonfile = jsonfile
        if not Path(self.jsonfile).exists():
            exits(f'"{self.jsonfile}" cannot be found!')
        self.encode = encode

    def loadJson(self) -> None:
        try:
            with opens(self.jsonfile, 'r', encoding=self.encode) as f:
                data = load(f)
        except decoder.JSONDecodeError:
            exits(f'{self.jsonfile} is not properly json formated!')
        finally:
            try:
                Data.metadata.update(data['metadata'])
            except KeyError:
                exits(f'{self.jsonfile} must contain metadata!')
            except UnboundLocalError:
                exits(f'cannot decode {self.jsonfile}!')
            try:
                Data.reference.update(data['reference'])
            except Exception as e:
                exits(f'unknown error: {str(e)}')

    def checkReferenceBool(self) -> None:
        for j in ['series', 'subfolder', 'no_extra', 'match_ratio', 'keep']:
            if not isinstance(Data.reference[j], bool): 
                exits(f'reference {j} need to be True or False!')

    def checkReferenceStr(self) -> None:
        if not bool(Data.reference['target_folder']):
            Data.reference['target_folder'] = str(Path().absolute())
        if len(Data.reference['separator']) > 1:
            exits('reference separator can only hold less than 2 character!')
        if Data.reference['series'] or Data.reference['match_ratio']:
            if not bool(Data.reference['template']):
                exits('reference template cannot be empty when series or match_ratio is true!')
        for t in ['target_folder', 'template', 'separator', 'episode_symbol']:
            if not isinstance(Data.reference[t], str):
                Data.reference[t] = str(Data.reference[t])
        # you can use : and \ and / in target_folder
        for k in Data.reference.keys():
            if k == 'target_folder':
                if bool(search(self.ESCAPE_CHAR[7:], Data.reference[k])):
                    exits('invaid character *?"<>| in reference target_folder!')
            elif isinstance(Data.reference[k], str):
                if bool(search(self.ESCAPE_CHAR, Data.reference[k])):
                    exits(f'invaid character \\/:*?"<>| in reference {k}!')

    def checkReferenceInt(self) -> None:
        for l in ['index', 'length', 'offset']:
            if not isinstance(Data.reference[l], int):
                exits(f'reference {l} need to be a number like 5 neither 5.0 nor 05 nor "5"')
        for n in ['index', 'length']:
            if  Data.reference[n] < 0:
                exits(f'reference {n} need to be a number greater than or equal to 0')

    def checkReferenceFloat(self) -> None:
        if not isinstance(Data.reference['ratio'], float):
            exits('reference ratio need to be a number like 0.5 neither 5 nor 5.0 nor 05 nor "5"')
        if not 0 < Data.reference['ratio'] < 1:
            exits('reference ratio need to be a number greater than 0 and less than 1')

    def checkReferenceList(self) -> None:
        # you can use : and \ and / in escape and ignore
        for p in ['escape', 'ignore']:
            if not isinstance(Data.reference[p], list): 
                exits(f'reference {p} need to be a list!')
            for f in Data.reference[p]:
                if not isinstance(f, str): 
                    exits(f'reference {p} can only store string!')
                if bool(search(self.ESCAPE_CHAR[7:], f)):
                    exits(f'invaid character *?"<>| in reference {p}!')

    def checkReferenceDict(self) -> None:
        for d in ['replace', 'manual']:
            if not isinstance(Data.reference[d], dict): 
                exits(f'reference {d} need to be a dictionary!')
            for i in (set(Data.reference[d].keys()) | set(Data.reference[d].values())):
                if not isinstance(i, str): 
                    exits(f'reference {d} can only store string!')
        # you can use every character in replace
        # you can use : and \ and / in manual
        for u in Data.reference['manual'].keys():
            if not bool(search(r'\\|/', u)):
                exits("reference manual's key must be a path")
            if bool(search(self.ESCAPE_CHAR[7:], (u or Data.reference['manual'][u]))):
                exits('invaid character *?"<>| in reference manual!')

    def checkWriteAccess(self) -> None:
        # test write access in target_folder
        try:
            current_time = strftime("%Y_%m_%d_%H-%M-%S", localtime())
            testfolder = Path(Data.reference['target_folder']).joinpath(f'lotus_{current_time}')
            testfolder.mkdir(parents=True)
            testfolder.rmdir()
        except PermissionError:
            exits(f'have no write access in {Data.reference["target_folder"]}!')
        except Exception as e:
            exits(f'unknown error: {str(e)}')

    def checkMetadata(self) -> None:
        if not bool(Data.metadata['title']):
            exits('title cannot be empty!')
        for k in Data.metadata.keys():
            if not isinstance(Data.metadata[k], str):
                Data.metadata[k] = str(Data.metadata[k])
            if bool(search(self.ESCAPE_CHAR, Data.metadata[k])):
                exits(f'invaid character \\/:*?"<>| in metadata {k}')
        if Data.reference['series']:
            if Data.metadata['season'].isdigit():
                Data.metadata['season'] = f"S{Data.metadata['season']}"
        else:
            Data.metadata['season'] = ''

    def processMetadata(self) -> dict:
        name_prefix = ''
        for i in ['title', 'original_title', 'season']:
            if bool(Data.metadata[i]):
                name_prefix += f'{Data.reference["separator"]}{Data.metadata[i]}'
            Data.metadata.pop(i)
        name_prefix = name_prefix[1:]
        
        name_postfix = ''
        try:
            for j in Data.metadata.values():
                if bool(j):
                    name_postfix += f'{Data.reference["separator"]}{j}'
        except:
            pass
        
        Data.metadata.clear()
        Data.metadata.update({'name_prefix': name_prefix})
        Data.metadata.update({'name_postfix': name_postfix})
        return Data.metadata

    def action(self) -> None:
        self.loadJson()
        self.checkReferenceBool()
        self.checkReferenceFloat()
        self.checkReferenceStr()
        self.checkReferenceInt()
        self.checkReferenceList()
        self.checkReferenceDict()
        self.checkWriteAccess()
        self.checkMetadata()
        self.processMetadata()

    def __call__(self) -> None:
        self.action()

class FileProcess:
    def __init__(self, dir: Path) -> None:
        self.dir = dir
    
    def getEpisode(self) -> str:
        number = compile(r'\d+(?:\.\d+)?')
        episode = number.findall(self.name)
        if (episode == []
            ) or (len(episode) < Data.reference['index']
            ) or (episode == number.findall(Data.reference['template'])):
            self.episode = ''
        else:
            self.episode = episode[Data.reference['index']]
        return self.episode
    
    def trueEpisode(self) -> str:
        self.getEpisode()
        if bool(self.episode):
            if bool(search(r'\.', self.episode)):
                f, b = self.episode.split('.')
                self.true_episode = f'{str(
                    int(f) - Data.reference['offset']
                    ).zfill(Data.reference['length'])}.{b}'
            else:
                self.true_episode = str(
                    int(self.episode) - Data.reference['offset']
                    ).zfill(Data.reference['length'])
            return self.true_episode
        return None
    
    def getExtra(self) -> str:
        if SequenceMatcher(
                a=Data.reference['template'], 
                b=self.name
                ).ratio() >= Data.reference['ratio']:
            extra = [
                x 
                for x in ndiff(Data.reference['template'], self.name) 
                if x[0] == '+'
                ]
            self.extra = ''.join([i[2] for i in extra])
        else:
            self.extra = self.name
        
        if Data.reference['series']:
            self.extra = sub(self.episode, r'', self.extra, count=1)
        for i in Data.reference['replace'].keys():
            self.extra = sub(i, Data.reference['replace'][i], self.extra)
        if set(findall(r'.', self.extra)) in [{'.', ' '}, {'.'}, {' '}]:
            self.extra = ''
        return self.extra

    def getTargetName(self) -> str:
        name_deque = deque()
        if Data.reference['series']:
            if bool(self.trueEpisode()):
                name_deque.append(
                    f'{Data.reference["separator"]
                    }{Data.reference["episode_symbol"]
                    }{self.true_episode}'
                    )
        name_deque.appendleft(Data.metadata['name_prefix'])
        name_deque.append(Data.metadata['name_postfix'])
        if not Data.reference['no_extra']:
            if bool(Data.reference['template']):
                if bool(self.getExtra()):
                    name_deque.append(Data.reference['separator'] + self.extra)
        name_deque.append(self.extension)

        self.target_name = ''.join([x for x in name_deque])
        return self.target_name

    def getTargetFolder(self) -> Path:
        self.target_folder = Path(Data.reference['target_folder'])
        if Data.reference['keep']:
            self.target_folder = self.target_folder.joinpath(self.diff)
        try:
            if Data.reference['subfolder'] and bool(self.episode):
                self.target_folder = self.target_folder.joinpath(self.true_episode)
        except:
            pass
        return self.target_folder

    def getTargetPath(self, path: Path) -> Path:
        self.path = path
        self.name = self.path.stem
        self.extension = self.path.suffix
        if self.path != self.dir:
            self.diff = Path('/'.join(
                [i for i in self.path.parts[len(self.dir.parts):(len(self.path.parts) - 1)]]
                ))
        else:
            self.diff = Path('')
        if self.path in Data.reference['manual'].keys():
            self.target_path = Path(Data.reference['manual'][self.path])
        else:
            self.getTargetName()
            self.getTargetFolder()
            self.target_path = self.target_folder.joinpath(self.target_name)
        return self.target_path
    
    def __str__(self, path: Path):
        return str(self.getTargetPath(path))

    def __call__(self, path: Path) -> Path:
        return self.getTargetPath(path)

class Lotus:
    def __init__(self) -> None:
        pass

    def setPath(self, path: str) -> None:
        self.path = Path(path)
        if not self.path.exists():
            exits(f'"{self.path}" cannot be found!')
        if not self.path.is_absolute():
            self.path = self.path.resolve()
        if self.path.is_file():
            self.dir = self.path.parent
        else:
            self.dir = self.path

    def setLinkOption(self, link_option: str) -> None:
        self.link_option = link_option.casefold()
        if self.link_option not in ['hardlink', 'softlink', 'test', 'rename']:
            exits('link_option only has 4 choices: test, hardlink, softlink, rename')

    def setRecursive(self, recursive: bool = False) -> None:
        self.recursive = recursive
        if isinstance(recursive, str):
            if recursive.casefold() in ['f', 'false', '0']:
                self.recursive = False
            elif recursive.casefold() in ['t', 'true', '1']:
                self.recursive = True
            else:
                exits('recursive need to be True or False')
        if isinstance(recursive, int):
            if recursive == 0:
                self.recursive = False
            elif recursive == 1:
                self.recursive = True
            else:
                exits('recursive need to be True or False')
        if not isinstance(self.recursive, bool):
            exits('recursive was given a wrong type')

    def processList(self, key) -> list:
        for i in range(len(Data.reference[key])):
            if search(r'^\.[\\/]', Data.reference[key][i]):
                Data.reference[key][i] = self.dir.joinpath(Data.reference[key][i])
            else:
                Data.reference[key][i] = Path(Data.reference[key][i])
        return Data.reference[key]

    def processManual(self) -> dict:
        items = {}
        for i in Data.reference['manual'].keys():
            if search(r'^\.[\\/]', i):
                items.update({self.dir.joinpath(i): Data.reference['manual'][i]})
            else:
                items.update({Path(i): Data.reference['manual'][i]})
        Data.reference['manual'] = items
        return Data.reference['manual']

    def recursiveFilepool(self):
        for i in self.path.rglob('*'):
            if i.is_file():
                yield i

    def unRecursiveFilepool(self):
        for i in self.path.iterdir():
            if i.is_file():
                yield i

    def check(self, path: Path, key: str) -> bool:
        if path in Data.reference[key] or Path(path.name) in Data.reference[key]:
            return True
        return False

    def linkAction(self, path: Path) -> str:
        if self.check(path, 'ignore'):
            return f'{path} is in ignore list'
        elif Data.reference['match_ratio']:
            if not SequenceMatcher(
                a=Data.reference['template'], 
                b=path.name
                ).ratio() >= Data.reference['ratio']:
                return f'{path} does not match ratio'
        else:
            if self.check(path, 'escape'):
                target_path = Path(Data.reference['target_folder']).joinpath(path.name)
            else:
                target_path = FileProcess(self.dir)(path)
            if not target_path.parent.exists():
                if self.link_option != 'test':
                    target_path.parent.mkdir(parents=True)
            if not target_path.is_file():
                if self.link_option == 'hardlink':
                    target_path.hardlink_to(path)
                elif self.link_option == 'softlink':
                    target_path.symlink_to(path, target_is_directory=False)
                elif self.link_option == 'rename':
                    path.rename(target_path)
                return f'{path} <={self.link_option}=> {target_path}'
            else:
                return f'{target_path} already exist'

    def autoLink(self) -> None:
        if self.path.is_dir():
            if self.recursive:
                file_pool = self.recursiveFilepool
            else:
                file_pool = self.unRecursiveFilepool
            with ThreadPoolExecutor() as executor:
                for single_task in executor.map(self.linkAction, file_pool()):
                    print(single_task)
        elif self.path.is_file():
            print(self.linkAction(self.path))
        else:
            pass

    def cmd(
            self, option: str, 
            path: str, 
            jsonfile: str, 
            recursive: bool = False, 
            encode: str = 'utf-8-sig'
            ) -> None:
        begin = time()
        self.setPath(path)
        self.setLinkOption(option)
        self.setRecursive(recursive)
        JsonProcess(jsonfile, encode)()
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
        subparsers.add_parser('rename', 
                                help='rename file/s')
        
        parser.add_argument('path', type=str, help='The source path of your file or folder')
        parser.add_argument('jsonfile', type=str, help='The source path of your jsonfile')
        parser.add_argument('-r', '--recursive', action='store_true',
                    help='recursively search folder or not, default is not')
        parser.add_argument('--encode', type=str, help='The encode of your jsonfile', required=False)
        
        args = parser.parse_args()
        self.cmd(args.option, args.path, args.jsonfile, args.recursive, args.encode)

if __name__ == '__main__':
    Lotus().cli()
