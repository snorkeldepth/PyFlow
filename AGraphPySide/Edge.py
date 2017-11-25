from PySide import QtCore
from PySide import QtGui
from Settings import Colors
from Nodes import Reroute
from AbstractGraph import *
import weakref


class Edge(QtGui.QGraphicsPathItem, Colors):

    def __init__(self, source, destination, graph):
        QtGui.QGraphicsPathItem.__init__(self)
        self.graph = weakref.ref(graph)
        self.source = weakref.ref(source)
        self.destination = weakref.ref(destination)
        self.setAcceptedMouseButtons(QtCore.Qt.LeftButton)
        self.setAcceptHoverEvents(True)

        self.path = QtGui.QPainterPath()

        self.cp1 = QtCore.QPointF(0.0, 0.0)
        self.cp2 = QtCore.QPointF(0.0, 0.0)

        self.setZValue(-1)
        self.connection = {'From': self.source().port_name(),
                           'To': self.destination().port_name()}

        if isinstance(source.parentItem(), Reroute):
            if source.parentItem().inp0.hasConnections():
                self.color = source.parentItem().color
            else:
                self.color = destination.color
        else:
            self.color = self.source().color

        self.thikness = 1
        if source.data_type == AGPortDataTypes.tExec and destination.data_type == AGPortDataTypes.tExec:
            self.thikness = 2

        self.pen = QtGui.QPen(self.color, self.thikness, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)

        points = self.getEndPoints()
        self.updateCurve(points[0], points[1])

        self.setPen(self.pen)

        self.source().update()
        self.destination().update()

    def __str__(self):
        return '{0}.{1} >>> {2}.{3}'.format(self.source().parent().name,
                                            self.source().name,
                                            self.destination().parent().name,
                                            self.destination().name)

    def hoverEnterEvent(self, event):
        super(Edge, self).hoverEnterEvent(event)
        self.pen.setWidthF(self.thikness + (self.thikness / 1.5))
        self.update()
        if self.graph().is_debug():
            print(self.__str__())

    def getEndPoints(self):
        offset = self.source().boundingRect().width() / 3.25
        p1 = self.source().sceneTransform().map(QtCore.QPointF(offset * 2, offset))
        p2 = self.destination().sceneTransform().map(QtCore.QPointF(0, offset))
        return p1, p2

    def mousePressEvent(self, event):
        super(Edge, self).mousePressEvent(event)
        event.accept()

    def mouseReleaseEvent(self, event):
        super(Edge, self).mouseReleaseEvent(event)
        event.accept()

    def mouseMoveEvent(self, event):
        super(Edge, self).mouseMoveEvent(event)
        event.accept()

    def hoverLeaveEvent(self, event):
        super(Edge, self).hoverLeaveEvent(event)
        self.pen.setWidthF(self.thikness)
        self.update()

    def source_port_name(self):
        return self.source().port_name()

    def updateCurve(self, p1, p2):
        xDistance = p2.x() - p1.x()
        multiply = 3
        self.path = QtGui.QPainterPath()

        direction = QtGui.QVector2D(p1) - QtGui.QVector2D(p2)
        direction.normalize()

        self.path.moveTo(p1)
        if xDistance < 0:
            self.path.cubicTo(QtCore.QPoint(p1.x() + xDistance / -multiply, p1.y()), QtCore.QPoint(p2.x() - xDistance / -multiply, p2.y()), p2)
        else:
            self.path.cubicTo(QtCore.QPoint(p1.x() + xDistance / multiply, p1.y()), QtCore.QPoint(p2.x() - xDistance / 2, p2.y()), p2)

        self.setPath(self.path)

    def destination_port_name(self):
        return self.destination().port_name()

    def paint(self, painter, option, widget):
        self.setPen(self.pen)
        p1, p2 = self.getEndPoints()

        xDistance = p2.x() - p1.x()

        multiply = 3
        self.path = QtGui.QPainterPath()

        self.path.moveTo(p1)

        if xDistance < 0:
            self.cp1 = QtCore.QPoint(p1.x() + xDistance / -1.5, p1.y())
            self.cp2 = QtCore.QPoint(p2.x() - xDistance / -multiply, p2.y())
        else:
            self.cp1 = QtCore.QPoint(p1.x() + xDistance / multiply, p1.y())
            self.cp2 = QtCore.QPoint(p2.x() - xDistance / 2, p2.y())

        self.path.cubicTo(self.cp1, self.cp2, p2)

        self.setPath(self.path)

        super(Edge, self).paint(painter, option, widget)
