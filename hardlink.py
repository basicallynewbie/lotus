#!/usr/bin/python3
import json
import pathlib
import sys
import re
import difflib

class HardLink():
    def __init__(self, path, jsonfile):
        self.path = path
        self.jsonfile = jsonfile
        self.linkfolder = ''
        self.linkpath = ''

    def initMetadata(self):
        self.metadata = {
            'title': '', 'originaltitle': '', 'season': '01', 'episode': '',
            'language': '', 'subtitle': '', 'reselution': '', 'encode': '',
            'country': '', 'year': '', 'genre': '', 'group': '',
            'studio': '', 'director': '', 'writer': '', 'actor': '',
            'extra': '', 'extension': '', 'index': 0, 'series': False,
            'linkfolder': '', 'template': '', 'subfolder': False
            }
        
        self.linkname = ''
        self.subfoldername = ''

    def updateMetadata(self):
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

    def checkMeatadata(self):
        if not bool(self.metadata['title']):
            sys.exit('title cannot be empty!')
        if not bool(self.metadata['linkfolder']):
            sys.exit('linkfolder cannot be empty!')
        if type(self.metadata['series']) != bool:
                sys.exit('series need to be true or false')
        if type(self.metadata['subfolder']) != bool:
                sys.exit('subfolder need to be true or false')
        if type(self.metadata['index']) != int:
                sys.exit('index need to be a number like 5 neither 5.0 nor 05 nor "5"')

    def processMetadata(self, filename):
        self.linkfolder = pathlib.Path(self.metadata['linkfolder'])
        if not pathlib.Path(self.metadata['linkfolder']).is_absolute():
            sys.exit('linkfolder need to be an absolute path!')

        if self.metadata['series']:
            self.metadata['season'] = 'S' + str(self.metadata['season'])
            
            try:
                episode = re.findall(r'\d+', filename)
                episode = episode[int(self.metadata['index'])]
                extrainfo = r'pv|teaser|trailer|scene|clip|interview|extra|deleted'
                if bool(re.search(extrainfo, filename, re.IGNORECASE)):
                    self.metadata.pop('episode')
                elif episode == re.findall(r'\d+', self.metadata['reselution'])[0]:
                    self.metadata.pop('episode')
                else:
                    if self.metadata['subfolder']:
                        self.subfoldername = episode
                    self.metadata['episode'] = 'E' + episode
            except:
                pass
        else:
            self.metadata.pop('season')
            self.metadata.pop('episode')

        if not bool(re.findall(r'\.', filename)):
            self.metadata.pop('extension')
        else:
            self.metadata['extension'] = filename.split('.')[-1]

        if bool(self.metadata['template']):
            extra = self.metadata['template']
            extra = [x for x in difflib.ndiff(extra, filename) if x[0] != ' ']
            extra = ''.join([x[2] for x in extra])

            trim = re.match(r'\d', extra)
            if trim != None:
                extra = re.sub(episode, '', extra)

            if 'extension' in self.metadata:
                extra = re.sub('.' + self.metadata['extension'], '', extra)

            self.metadata['extra'] = extra

        self.metadata.pop('linkfolder')
        self.metadata.pop('series')
        self.metadata.pop('index')
        self.metadata.pop('template')
        self.metadata.pop('subfolder')

        for i in self.metadata.values():
            if bool(i):
                self.linkname = self.linkname + f'.{i}'
        self.linkname = self.linkname[1:]

        if filename == pathlib.Path(self.jsonfile).name:
            self.linkname = filename

    def checkInput(self, abspath):
        if not pathlib.Path(abspath).exists():
            sys.exit(f'"{abspath}" cannot be found!')
        elif not pathlib.Path(abspath).is_absolute():
            sys.exit(f'"{abspath}" need to be an absolute path!')
        else:
            pass

    def checkAction(self):
        self.checkInput(self.path)
        self.path = pathlib.Path(self.path)
        self.checkInput(self.jsonfile)
        self.jsonfile = pathlib.Path(self.jsonfile)

    def fileLinker(self, originpath):
        truelinkfolder = pathlib.Path(self.linkfolder).joinpath(self.subfoldername)
        if not pathlib.Path(truelinkfolder).is_dir():
            try:
                pathlib.Path.mkdir(truelinkfolder, parents=True)
            except:
                sys.exit(f'no permission to create "{truelinkfolder}"')

        self.linkpath = truelinkfolder.joinpath(self.linkname)
        if not self.linkpath.is_file():
            self.linkpath.hardlink_to(originpath)
            print(f'{originpath} <==> {self.linkpath}')

    def linkProcessing(self, originname, originpath):
        self.initMetadata()
        self.updateMetadata()
        self.checkMeatadata()
        self.processMetadata(originname)
        self.fileLinker(originpath)

    def noneRecursiveWay(self):
        for i in self.path.iterdir():
                if i.is_file():
                    self.linkProcessing(i.name, i)

    def recursiveWay(self):
        for i in self.path.rglob('*'):
                if i.is_file():
                    self.linkProcessing(i.name, i)

    def autoLink(self, whichway):
        if self.path.is_dir():
            whichway
        elif self.path.is_file():
            self.linkProcessing(self.path.name, self.path)
        else:
            pass

    def linkAction(self):
        self.checkAction()
        self.autoLink(self.noneRecursiveWay)

    def recursiveLinkAction(self):
        self.checkAction()
        self.autoLink(self.recursiveWay)

if __name__ == '__main__':
    rl = HardLink(sys.argv[1], sys.argv[2])
    rl.linkAction()

    # nrl = HardLink(sys.argv[1], sys.argv[2])
    # nrl.recursiveLinkAction()
