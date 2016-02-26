#-------------------------------------------------------------------------------
# Name:        Modelando_ED
# Purpose:     Proyecto de Matematica Numerica II
#
# Author:      Yanesita and Machy
#
# Created:     17/05/2013
# Copyright:   (c) Yanesita and Machy 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

#from ODESolvers.ODESolvers import ODE
from __future__ import division
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *
from math import *
from PyQt5 import uic
from sys import path
from array import *
import matplotlib.pyplot as pl

import numpy as np

import sys

q=2/3
u=(1/9)*(1/365)
e=1/2
d=1/5
a=1/180
y=(1/3)*(1/270)
b=1/365
p=0.8


global parametros, dominios,condiciones,myDominios
parametros=[]
dominios=[]
condiciones=[]
myDominios={}

class MyDominio:
    def __init__(self,name='', condIn=None, condOut=None):
        if(condIn==None):
            self.condIn=[]
        else:
            self.condIn=condIn
        if(condOut==None):
            self.condOut=[]
        else:
            self.condOut=condOut
        self.name=name

    def condition(self):
        dimension= 'lambda *params:'+ self.name
        if(len(self.condIn)):
            for x in self.condIn:
                dimension+= '+' +'('+ x+')'
        if(len(self.condOut)):
             for x in self.condOut:
                dimension+= '-'  +'('+ x+')'
        return dimension

class MyItem(QGraphicsPolygonItem):
    def __init__(self, parent=None):
        QGraphicsPolygonItem.__init__(self, parent, scene=None)
        #QGraphicsItem.__init__(self,parent)
        self.circle = QPainterPath()
        self.circle.addEllipse(0,0,30,30)
        self.brush = QBrush(QColor(0,0,255,128))
        self.pen = QPen(Qt.black)
        self.pen.setWidth(1.0)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        #self.setFlag(QGraphicsItem.ItemIsSelectable)
        #self.setFlag(QGraphicsItem.ItemIsMovable)
        self.arrows = []
        path = QPainterPath()

    def removeArrow(self, arrow):
        if arrow in self.arrows:
            arrows.remove(arrow)

    def shape(self):
        return self.circle

    def boundingRect(self):
        return self.circle.boundingRect().adjusted(-1,-1,1,1)

    def paint(self,painter,styleoption,widget):
        if self.isSelected():
            self.brush.setColor(Qt.red)
        else:
            self.brush.setColor(Qt.blue)

        painter.setBrush(self.brush)
        painter.setPen(self.pen)
        painter.drawPath(self.circle)

    def mouseDoubleClickEvent(self,event):
        c,t = QColorDialog.getRgba(self.brush.color().rgba())
        if not t:
            return
        self.brush.setColor(QColor.fromRgba(c))
        self.update()

    def addArrow(self, arrow):
        self.arrows.append(arrow)

    def contextMenuEvent(self, event):
        self.scene().clearSelection()
        self.setSelected(True)
        self.myContextMenu.exec_(event.screenPos())

        def itemChange(self, change, value):
            if change == QGraphicsItem.ItemPositionChange:
                for arrow in self.arrows:
                    arrow.updatePosition()
        return QVariant(value)

class Arrow(QGraphicsLineItem):
    def __init__(self, startItem, endItem, parent=None, scene=None):
        QGraphicsLineItem.__init__(self, parent, scene)

        self.myStartItem = startItem
        self.myEndItem = endItem
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.myColor = Qt.black
        self.setPen(QPen(self.myColor, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        self.arrowHead = QPolygonF()
        self.brush = QBrush(QColor(0,0,255,128))
        #self.pen = QPen(Qt.black)
        #self.pen.setWidth(1.0)

    def setColor(self, color):
        self.myColor = color

    def boundingRect(self):
        extra = (self.pen().width() + 20) / 2.0
        p1 = self.line().p1()
        p2 = self.line().p2()
        return QRectF(p1, QSizeF(p2.x() - p1.x(), p2.y() - p1.y())).normalized().adjusted(-extra, -extra, extra, extra)

    def shape(self):
        path = QGraphicsLineItem.shape(self)
        path.addPolygon(self.arrowHead)
        return path

    def updatePosition(self):
        line = QLineF(self.mapFromItem(self.myStartItem, 0, 0), self.mapFromItem(self.myEndItem, 0, 0))
        self.setLine(line)

    def paint(self, painter, option, widget=None):
        if (self.myStartItem.collidesWithItem(self.myEndItem)):
            return

        myStartItem = self.myStartItem
        myEndItem = self.myEndItem
        myColor = self.myColor
        myPen = self.pen()
        myPen.setColor(self.myColor)
        arrowSize = 20.0
        painter.setPen(myPen)
        painter.setBrush(self.myColor)

        centerLine = QLineF(myStartItem.pos(), myEndItem.pos())
        endPolygon = myEndItem.polygon()
        p1 = endPolygon.first() + myEndItem.pos()

        intersectPoint = QPointF()
        for i in endPolygon:
            p2 = i + myEndItem.pos()
            polyLine = QLineF(p1, p2)
            intersectType = polyLine.intersect(centerLine, intersectPoint)
            if intersectType == QLineF.BoundedIntersection:
                break
            p1 = p2

        self.setLine(QLineF(intersectPoint, myStartItem.pos()))
        line = self.line()

        angle =acos(self.line().dx() / self.line().length())
        if line.dy() >= 0:
            angle = (pi * 2.0) - angle

        arrowP1 = line.p1() + QPointF(sin(angle + pi / 3.0) * arrowSize,
                                        cos(angle + pi / 3) * arrowSize)
        arrowP2 = line.p1() + QPointF(sin(angle + pi - pi / 3.0) * arrowSize,
                                        cos(angle + pi - pi / 3.0) * arrowSize)

        self.arrowHead.clear()
        for point in [line.p1(), arrowP1, arrowP2]:
            self.arrowHead.append(point)

        painter.drawLine(line)
        painter.drawPolygon(self.arrowHead)
        if self.isSelected():
            painter.setPen(QPen(myColor, 1, Qt.DashLine))
            myLine = QLineF(line)
            myLine.translate(0, 4.0)
            painter.drawLine(myLine)
            myLine.translate(0,-8.0)
            painter.drawLine(myLine)

    def mouseDoubleClickEvent(self,event):
        cond=DialogCondiciones()
        cond.show()

class DiagramScene(QGraphicsScene):
    InsertLine,MoveItem = range(2)

    def __init__(self,  parent=None):
        QGraphicsScene.__init__(self, parent)

        #self.myItemMenu = itemMenu
        self.myMode = self.MoveItem
        self.myItemType = DiagramItem.Step
        self.line = None
        self.textItem = None
        self.myItemColor = Qt.white
        self.myTextColor = Qt.black
        self.myLineColor = Qt.black
        self.myFont = QFont()

    def setLineColor(self, color):
        self.myLineColor = color
        if self.isItemChange(Arrow):
            item = self.selectedItems()[0]
            item.setColor(self.myLineColor)
            self.update()

    def setTextColor(self, color):
        self.myTextColor = color
        if self.isItemChange(DiagramTextItem):
            item = self.selectedItems()[0]
            item.setDefaultTextColor(myTextColor)

    def setItemColor(self, color):
        self.myItemColor = color
        if self.isItemChange(DiagramItem):
            item = self.selectedItems()[0]
            item.setBrush(self.myItemColor)

    def setFont(self, font):
        self.myFont = font
        if self.isItemChange(DiagramTextItem):
            item = self.selectedItems()[0]
            item.setFont(self.myFont)

    def setMode(self, mode):
        self.myMode = mode

    def setItemType(self, type):
        self.myItemType = type

    def editorLostFocus(self, item):
        cursor = item.textCursor()
        cursor.clearSelection()
        item.setTextCursor(cursor)
        if item.toPlainText().isEmpty():
            self.removeItem(item)
            item.deleteLater()

    def mousePressEvent(self, mouseEvent):
        if (mouseEvent.button() != Qt.LeftButton):
            return

        if self.myMode == self.InsertLine:
            self.line = QGraphicsLineItem(QLineF(mouseEvent.scenePos(),
                                        mouseEvent.scenePos()))
            self.line.setPen(QPen(self.myLineColor, 2))
            self.addItem(self.line)

        QGraphicsScene.mousePressEvent(self, mouseEvent)

    def mouseMoveEvent(self, mouseEvent):
        if self.myMode == self.InsertLine and self.line:
            newLine = QLineF(self.line.line().p1(), mouseEvent.scenePos())
            self.line.setLine(newLine)
        elif self.myMode == self.MoveItem:
            QGraphicsScene.mouseMoveEvent(self, mouseEvent)

    def mouseReleaseEvent(self, mouseEvent):
        if (self.line and self.myMode == self.InsertLine):
            startItems = self.items(self.line.line().p1())
            if len(startItems) and startItems[0] == self.line:
                startItems.pop(0)
            endItems = self.items(self.line.line().p2())
            if len(endItems) and endItems[0] == self.line:
                endItems.pop(0)

            self.removeItem(self.line)
            self.line = None

            if len(startItems) and len(endItems) and \
                    isinstance(startItems[0], MyItem) and \
                    isinstance(endItems[0], MyItem) and \
                    startItems[0] != endItems[0]:
                startItem = startItems[0]
                endItem = endItems[0]
                arrow = Arrow(startItem, endItem)
                arrow.setColor(self.myLineColor)
                startItem.addArrow(arrow)
                endItem.addArrow(arrow)
                arrow.setZValue(-1000.0)
                self.addItem(arrow)
                arrow.updatePosition()

        self.line = None
        QGraphicsScene.mouseReleaseEvent(self, mouseEvent)

    def isItemChange(self, type):
        for item in self.selectedItems():
            if isinstance(item, type):
                return True
        return False
    InsertTextButton = 10

class DiagramItem(QGraphicsPolygonItem):
    Step = range(1)

    def __init__(self, diagramType, contextMenu, parent=None, scene=None):
        QGraphicsPolygonItem.__init__(self, parent, scene)

        self.diagramType = diagramType
        self.contextMenu = contextMenu

        path = QPainterPath()

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.arrows = []

    def image(self):
        rect= QRect( QPoint(-100, -100), QPoint(100, 100))
        pixmap = QPixmap(250, 250)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setBrush(QBrush(QColor(0,0,255,128)))
        painter.setPen(QPen(Qt.black, 8))
        painter.translate(125, 125)
        painter.drawEllipse(rect)
        return pixmap

    def removeArrow(self, arrow):
        if arrow in self.arrows:
            arrows.remove(arrow)

    def removeArrows(self):
        for arrow in arrows:
            arrow.startItem().removeArrow(arrow)
            arrow.endItem().removeArrow(arrow)
            self.scene().removeItem(arrow)

    def addArrow(self, arrow):
        self.arrows.append(arrow)

    def contextMenuEvent(self, event):
        self.scene().clearSelection()
        self.setSelected(True)
        self.myContextMenu.exec_(event.screenPos())

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            for arrow in self.arrows:
                arrow.updatePosition()
        return QVariant(value)

class DialogCondiciones(QDialog):
    def __init__(self,parent=None):
        QDialog.__init__(self,parent)
        self.ui=uic.loadUi("Condiciones.ui",self)
        self.ui.comboBoxOut.addItems(dominios)
        self.ui.comboBoxIn.addItems(dominios)
        self.connect(self.ui.insertarCondicion,SIGNAL("clicked()"),self.agregarCondicion)

    def agregarCondicion(self):
        entrante= self.ui.comboBoxIn.currentIndex()
        saliente= self.ui.comboBoxOut.currentIndex()
        myDominios[str(dominios[entrante])].condIn.append(self.ui.lineCondicion.text())
        myDominios[str(dominios[saliente])].condOut.append(self.ui.lineCondicion.text())
       #condiciones.append(self.ui.lineCondicion.text())
        self.close()

class DialogDominios(QDialog):
    def __init__(self,parent=None):
        QDialog.__init__(self,parent)
        self.ui=uic.loadUi("Dominios.ui",self)
        self.connect(self.ui.aceptarDominio,SIGNAL("clicked()"),self.recibirDominio)

    def recibirDominio(self):
        dominios.append(self.ui.lineEditDominio.text())
        dom=MyDominio(self.ui.lineEditDominio.text())
        myDominios[str(self.ui.lineEditDominio.text())]=dom
        self.close()

class DialogParametros(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.ui = uic.loadUi("Parametros.ui",self)
        self.connect(self.ui.aceptarParametros,SIGNAL("clicked()"),self.recibirParametros)

    def recibirParametros(self):
        cond=self.ui.lineParametros.text()
        cond=cond.split(',')
        for x in cond:
            parametros.append(x)
        self.close()

class MainWindowControles(QMainWindow):


    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.ui = uic.loadUi("Controles.ui",self)
        self.line= False

        self.connect(self.ui.aceptar,SIGNAL("clicked()"),self.ok)
        self.connect(self.ui.actionParametros,SIGNAL("triggered()"),self.parametro)
        self.connect(self.ui.dominio, SIGNAL("clicked()"), self.itemInserted)
        self.connect(self.ui.insertLine,SIGNAL("clicked()"),self.addLine)

        #dibujar el rectangulo en el boton
        item = DiagramItem(0, self.ui.controles)
        icon = QIcon(item.image())
        self.ui.dominio.setIcon(icon)
        self.ui.dominio.setIconSize(QSize(50, 50))
        self.ui.dominio.setCheckable(True)

        #self.scene = QGraphicsScene()
        self.scene= DiagramScene()
        self.ui.graphicsView.setScene(self.scene)
        self.ui.graphicsView.setRenderHint(QPainter.Antialiasing)
        self.ui.graphicsView.setDragMode(QGraphicsView.RubberBandDrag)

        if(len(dominios)):
            for x in dominios:
                mD= MyDominio(x)

    def addLine(self):
        if self.line :
            self.line=False
            self.scene.myMode=DiagramScene.MoveItem
        elif (self.line==False):
            self.scene.myMode=DiagramScene.InsertLine
            self.line=True

    def ok(self):
        grafico= MainWindowGrafico()
        grafico.show()

        self.close()

    def parametro(self):
        dialogParam=DialogParametros()
        dialogParam.show()

    def itemInserted(self):
        i = MyItem()
        dialogDom=DialogDominios()
        dialogDom.show()
        i.setPos(0*30,0*30)
        self.scene.addItem(i)
        self.update()

class MainWindowGrafico(QMainWindow):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.ui = uic.loadUi("Grafico.ui",self)
        self.ui.listaParametros.addItems(parametros)
        self.connect(self.ui.euler,SIGNAL("clicked()"),self.ecuacion)
        #self.connect(self.ui.rungekutta,SIGNAL("clicked()"),self.p)
        self.ecuac={}
        for x in myDominios.keys():
            self.ecuac[x]=myDominios[x].condition()


        #self.ivp=eval('lambda x,*t: array([t[0],t[1],t[2],t[2]])')

    def euler2(self,y0, f, t0=0., h=.001, iters=1000):
        #q=2/3
        #u=(1/9)*(1/365)
        #e=1/2
        #d=1/5
        #a=1/180
        #y=(1/3)*(1/270)
        #b=1/365
        #p=0.8
        carlos = []
        evelio = []
        yanet = []
        fernando = []
        ttt=[]
        ttt.append(t0)
        carlos.append(y0[0])
        evelio.append(y0[1])
        yanet.append(y0[2])
        fernando.append(y0[3])
        count=1
        while(count<iters):
        #for x in range(iters):
            carlos.append(carlos[count-1]+h* (f(ttt[count-1],[carlos[count-1],evelio[count-1],yanet[count-1],fernando[count-1]])[0]))
            evelio.append(evelio[count-1]+h* f(ttt[count-1],[carlos[count-1],evelio[count-1],yanet[count-1],fernando[count-1]])[1])
            yanet.append(yanet[count-1]+h* f(ttt[count-1],[carlos[count-1],evelio[count-1],yanet[count-1],fernando[count-1]])[2])
            fernando.append(fernando[count-1]+h* f(ttt[count-1],[carlos[count-1],evelio[count-1],yanet[count-1],fernando[count-1]])[3])
            ttt.append(ttt[count-1] + h)
            count+=1
        ret=[]
        ret.append(carlos)
        ret.append(evelio)
        ret.append(yanet)
        ret.append(fernando)
        pl.plot(ttt,ret[1])
        pl.draw()
        return ttt,ret

    def euler1(self,y0, f, t0=0., h=.01, iters=12000):
        self.dicc={}
        for x in range(len(y0)):
            self.dicc[str(x)]=np.zeros (iters)
            self.dicc[str(x)][0]=y0[x]
        #carlos = np.zeros (iters)
        #evelio = np.zeros (iters)
        #yanet = np.zeros (iters)
        #fernando = np.zeros (iters)
        self.ttt=np.zeros(iters)
        self.ttt[0]=t0
        #carlos[0]=y0[0]
        #evelio[0]=y0[1]
        #yanet[0]=y0[2]
        #fernando[0]=y0[3]
        count=1
        while(count<iters):
            for x in range(len(y0)):
            #carlos[count]=carlos[count-1]+h* (f(ttt[count-1],[carlos[count-1],evelio[count-1],yanet[count-1],fernando[count-1]])[0])
            #evelio[count]=evelio[count-1]+h* f(ttt[count-1],[carlos[count-1],evelio[count-1],yanet[count-1],fernando[count-1]])[1]
            #yanet[count]=yanet[count-1]+h* f(ttt[count-1],[carlos[count-1],evelio[count-1],yanet[count-1],fernando[count-1]])[2]
            #fernando[count]=fernando[count-1]+h* f(ttt[count-1],[carlos[count-1],evelio[count-1],yanet[count-1],fernando[count-1]])[3]
                aux=[]
                for j in range(len(y0)):
                    aux.append(self.dicc[str(j)][count-1])

                self.dicc[str(x)][count]=self.dicc[str(x)][count-1]+h* (f(self.ttt[count-1],aux)[x])
                self.ttt[count] = self.ttt[count-1] + h
            count+=1

        pl.plot(self.ttt,self.dicc.values()[0])
        pl.plot(self.ttt,self.dicc.values()[1])
        pl.plot(self.ttt,self.dicc.values()[2])
        pl.plot(self.ttt,self.dicc.values()[3])
        pl.show()

    def p(self,   widget=None):
        self.myColor = Qt.black
        #self.setPen(QtGui.QPen(self.myColor, 2, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        self.pen=Qt.red
        pixmap = QPixmap(250, 250)
        #pixmap.fill(QtCore.Qt.transparent)
        painter = QPainter(pixmap)

        myStartItem = QPointF(self.ttt[0],self.dicc['1'][0])
        myEndItem = QPointF(self.ttt[len(self.ttt)-1],self.dicc['1'][len(self.ttt)-1])
        self.myColor = Qt.blue
        myPen = self.pen
        #myPen.setColor(self.myColor)
        #arrowSize = 20.0
        painter.setPen(myPen)
        painter.setBrush(self.myColor)

        centerLine = QLineF(myStartItem, myEndItem)
        #endPolygon = myEndItem.polygon()
        #p1 = endPolygon.first() + myEndItem.pos()

        intersectPoint = QPointF()
        ##        for i in endPolygon:
        ##            p2 = i + myEndItem.pos()
        ##            polyLine = QtCore.QLineF(p1, p2)
        ##            intersectType = polyLine.intersect(centerLine, intersectPoint)
        ##            if intersectType == QtCore.QLineF.BoundedIntersection:
        ##                break
        ##            p1 = p2

        #self.setLine(QLineF(intersectPoint, myStartItem))
        for x in range(len(self.ttt)/100):
            line =  QLineF(self.ttt[x-1],self.dicc['1'][x-1],self.ttt[x],self.dicc['1'][x])
            painter.drawLine(line)



    def ecuacion(self):
        #self.ivp.rhs=eval(self.ecuac[myDominios.keys()[0]])
        #self.ode = ODE()
        self.t=[0.59,0.30,0.08,0.03]
        self.ivp=eval('lambda x, t: [q*u + e*t[1]*(t[0]+t[2]) - d*t[1]*t[0] - (a+u)*t[0],(1-q)*u + d*t[1]*t[0] + b*p*t[3] - e*t[1]*(t[0]+t[2]) - u*t[1],a*t[0] + b*(1-p)*t[2] - (y+u)*t[1],y*t[1] - b*t[2] - u*t[2]]')
#self.ivp=eval('lambda x, t: [q*u + e*t[1]*(t[0]+t[2]) - d*t[1]*t[0] - (a+u)*t[0],(1-q)*u + d*t[1]*t[0] + b*p*t[3] - e*t[1]*(t[0]+t[2]) - u*t[1],a*t[0] + b*(1-p)*t[2] - (y+u)*t[1],y*t[1] - b*t[2] - u*t[2]]')
#self.t=[0.59,0.30,0.08,0.03]
        self.ode=self.euler1(self.t,self.ivp)
        #print(self.ode)







app = QApplication(sys.argv)
#m = MainWindowControles()
m = MainWindowGrafico()
m.show()
app.exec_()

#if __name__ == '__main__':
 #   main()
