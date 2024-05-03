from hardlink import HardLink
import sys

link = HardLink(sys.argv[1], sys.argv[2])
link.linkAction()
