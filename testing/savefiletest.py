from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *

points = [[350, 1], [550, 2]]
led_outputs = [5.5, 6.2]

error = None
fh = None
print "before try"
try:
    print "before qfile"
    fh = QFile('filename')
    print "hello"
    openfile = open('pathtofile', 'w')
    if not fh.open(QIODevice.WriteOnly):
        raise IOError, unicode(fh.errorString())
    #if not fh2.open(QIODevice.WriteOnly):
        #raise IOError, unicode(fh.errorString())
    stream = QDataStream(fh)
    stream.writeInt32(23435435)
    stream.writeInt32(100)
    stream.setVersion(QDataStream.Qt_4_2)
    openfile.write('Debug file')
    openfile.write(repr((points, led_outputs)))
##    for wavelength, amplitude in points:
##        stream.writeInt16(wavelength)
##        stream.writeDouble(amplitude)
##        openfile.write(str(wavelength))
##        openfile.write(str(amplitude))
##        print [wavelength, amplitude]
    stream.writeInt32(int(600))
    print int(600)
    for amplitude in led_outputs:
        stream.writeDouble(amplitude)
        print amplitude
except (IOError, OSError), e:
    error = "Failed to save: %s" % e
    print error
finally:
    openfile.close()
    if fh is not None:
        fh.close()
    if error is not None:
        pass
    #self.dirty = False
