'''
trap_potential_animation.py

Yu Tomita
yu.t@gatech.edu
2008

Creates continuous images of 3D saddle point surface and
a ball on the surface. The flipping surface represents
the potential of the quadruple ion trap, and a ball 
represents a trapped ion.
'''


import sys
import math
import time
import getpass

from random import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

savingImages = 0	 # 1 -> save images # XXX

ESCAPE = '\033'

fieldSize=50		# mesh size of surface
field=[[]]*fieldSize*(2)
deriv=[[]]*fieldSize*(2)
fmx=5.
fmz=0.08
maxz=0.
coarse=4
angle=-20
i=0
finalangle = 12*math.pi # ending angle (quits program when angle>finalangle)
px,py,pz=(10.,0.,0.) 	# starting point of a ball
vx,vy,vz=(0.,0.,0.)  	# starting velocity of the ball
r=1.0				 	# radius of the ball
ang=math.pi-0.2	

# This is called only once at start
def initStates():
	global field, fieldSize, maxz,deriv
	for i in xrange(-fieldSize,fieldSize,1):
		field[i]=[0.0]*fieldSize*(2)
		deriv[i]=[(0.0,0.0)]*fieldSize*(2)
		for j in xrange(-fieldSize,fieldSize,1):
			field[i][j]=(1.*(i)**2-1.*(j)**2)*fmz/fmx
			if i>-fieldSize and i is not 0:
				di=-field[i][j]+field[i-1][j]
			else:
				di=0.
			if j>-fieldSize and j is not 0:
				dj=-field[i][j]+field[i][j-1]
			else:
				dj=0.
			deriv[i][j]=(2*di,2*dj)
			if maxz<field[i][j]:
				maxz=field[i][j]
	print deriv[-20][0]
	pass	

# This is called at every step 
def computeStep():
	global angle,deriv,r
	global finalangle
	global px,py,pz,vx,vy,vz,ang
	ang=(ang+0.2)
	r=math.sin(ang%(2*math.pi))
	da=0.
	angle=angle+da
	if ang>finalangle:
		sys.exit()
	ci=0.1
	cj=1.
	da=1.*da*math.pi/180
	px=math.cos(da)*(px+vx)-math.sin(da)*(pz+vz)
	pz=math.sin(da)*(px+vx)+math.cos(da)*(pz+vz)
	px=px*1.0
	pz=pz*1.0
	vz=math.sin(angle)*(vx)+math.cos(angle)*(vz)
	py=r*field[int(px)][int(pz)]
	di=r*deriv[int(px)][int(pz)][0]
	dj=r*deriv[int(px)][int(pz)][1]
	vx,vy,vz=(vx+ci*di,0.,vz+cj*dj)	
	return
	

#--------- below is all graphics related --------#

capturedImage = ()				
capturedImageFormat = GL_RGB		
capturedSize = (320, 240 ,3)

def gradient(a):
	a=a*2
	if a<=1:
		return [0, 0, abs(a-1)]
	return [abs(a-1), 0, 0]

def InitGL(Width, Height):
	glClearColor(1.0, 1.0, 1.0, 0.0)
	glClearDepth(1.0)
	glDepthFunc(GL_LESS)
	glEnable(GL_DEPTH_TEST)
	glShadeModel(GL_SMOOTH)

	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluPerspective(45.0, float(Width)/float(Height), 0.1, 2000.0)
	glMatrixMode(GL_MODELVIEW)

def ReSizeGLScene(Width, Height):
	if Height == 0:                                          
		Height = 1
	glViewport(0, 0, Width, Height)         
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluPerspective(45.0, float(Width)/float(Height), 0.1, 2000.0)
	glMatrixMode(GL_MODELVIEW)

# numx = number of lines from x=0 to edge (length is twice)
def drawGrid():
	global field, fieldSize,r
	for i in range(-fieldSize,fieldSize,coarse):
		for j in range(-fieldSize,fieldSize,coarse):
			glBegin(GL_POLYGON)
			glColor3fv(gradient((r*field[i][j]+maxz)/(maxz*2)))
			glVertex3f(i, r*field[i][j], j)
			glVertex3f((i+coarse), r*field[i+coarse][j], j)
			glVertex3f((i+coarse), r*field[i+coarse][j+coarse], (j+coarse))
			glVertex3f((i), r*field[i][j+coarse], (j+coarse))
			glEnd()

def drawBall():
	glColor3f(0.,.9,.8)	
	glutSolidSphere(3,10,10)

def DrawGLScene():
	global px, py, pz
	global fmx, fmz	
	global angle
	global i
	zoom=0
	fieldSize=10
	computeStep() 	# update positions etc

	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glLoadIdentity()# Reset The View

	# Draw a ball
	glTranslatef(0.,-1.,-800+zoom*5)
	glRotate(50,1,0,0)      # 26.56=atan(5/10)
	glScalef(fmx,fmx,fmx)
	glRotate(angle,0,1,0)
	glPushMatrix()
	glTranslatef(px,py+4,pz)
	drawBall()
	glPopMatrix()	

	# draw surface 
	glPushMatrix()
	drawGrid()
	glPopMatrix()
	glutSwapBuffers()
	if savingImages:
		SaveTo("saddle%03d_s.png"%i, capturedSize[0], capturedSize[1]) 
	i+=1


def keyPressed(*args):
	if args[0] == ESCAPE:
		glutDestroyWindow(window)
		sys.exit()

def vsimulate():
	global window

	initStates()

	glutInit(sys.argv)
	glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
	glutInitWindowSize(320, 240)
	glutInitWindowPosition(0, 0)

	window = glutCreateWindow("Saddle Point")
	
	# DrawGLScene is called at every animation step
	glutDisplayFunc(DrawGLScene)
	glutIdleFunc(DrawGLScene)
	glutReshapeFunc(ReSizeGLScene)
	
	glutKeyboardFunc(keyPressed)
	InitGL(960, 720)        

vsimulate()
glutMainLoop()
