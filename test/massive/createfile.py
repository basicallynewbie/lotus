from pathlib import Path

sf = Path('source')
if not sf.exists():
    sf.mkdir()


for i in range(2000):
    target = sf.joinpath(str(i))
    if not target.exists():
        target.mkdir()
    file = target.joinpath(f"[somegroup] exampletv {i} [1920x1080p][AAC][AVC][JA][CHS].txt")
    f = open(str(file), "w" , encoding='UTF-8')
    f.write(f"{i}")
    f.close()
