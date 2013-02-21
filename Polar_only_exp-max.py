#! /usr/bin/python2

import numpy
import random
import Gnuplot

def BlankArrayWithBackground(rMax,qMax):
  polarImageArray = numpy.zeros((rMax,qMax)) #makes a blank numpy array
	for n in range(rMax): #Set all values to a background level
		for m in range(qMax):
			polarImageArray[n][m]=0.1 #defines the overall back ground for array
	return polarImageArray

def DrawSpiral(rMax,angStep,qMax): 
	polarImageArray=BlankArrayWithBackground(rMax,qMax)
	for r in range(rMax):
		q=r
		if q>qMax-1: #draws a nice spiral shape
			q=q-(qMax*(q//qMax))
		polarImageArray[r][q]=1
	outputFile="SpiralPrint"
	polarImageArray.tofile(outputFile, sep="	", format="%s")	
	return polarImageArray
	
#def PrintArrayToFile(fid, sep, 
	
def RandomPixel(imageArray):
	while True:
		i=[]
		rRan=random.randrange(len(imageArray)) #picks a random r coord
		qRan=random.randrange(len(imageArray[0])) #picks a random q coord	print coords
		i.append(imageArray[rRan][qRan])
		if i[0]>0.1:
			i.append(rRan),i.append(qRan)
			break
	return i
	
def RotatePixel(frameStack,frameNo,pixelNo,rotAngle):
	q=frameStack[frameNo][pixelNo][2]+rotAngle
	if (q>359): #stops q values of greater than 360 entering the system
		q=q-360
	return q

def RotateFrame(frameStack,frameNo,angStep):
	#frameStackTemp=copy.deepcopy(frameStack) #make a new temporary frame stack
	for n in range(len(frameStack[frameNo])): #run for all pixels in frame
		frameStack[frameNo][n][2]=frameStack[frameNo][n][2]+angStep
		if (frameStack[frameNo][n][2]>359): #simple rotation roll function
			frameStack[frameNo][n][2]=frameStack[frameNo][n][2]-360
	return frameStack
	
def RotateArray(polarImageArray, rotVal):
	rotImageArray=numpy.roll(polarImageArray,rotVal,axis=1)
	return rotImageArray 

def MakeFrame(polarImageArray,angStep,frameSizeUpper,frameSizeLower): #make a lower resolution image 
	frame=[] #make a list to store the two or three pixels that make up a frame	
	for n in range(random.randrange(frameSizeLower,frameSizeUpper)): # generates an average number of pixels between thoughs points
		i=RandomPixel(polarImageArray)
		i[2]=i[2]*angStep
		piPhi={}
		i.append(piPhi)
		frame.append(i)
	return frame

def MakeFrameStack(polarImageArray,angStep,frameSizeUpper=12,frameSizeLower=9,stackSize=10):
	frameStack={} #make dictionary to store all the individual frames
	for n in range(stackSize): #makes dictionary with a stated number of frames set by stackSize
		frameStack[n]=MakeFrame(polarImageArray,angStep,frameSizeUpper,frameSizeLower) #add randomly generated to a dictionary
		rotVal=random.randrange(qMax) #randomly choose a value to shift the rotation by	
		framStack=RotateFrame(frameStack,n,rotVal) #rotate the frame through a random angle 
	return frameStack
	
def RandomIntensityModelGen(rMax,angStep,qMax):
	W=[]
	W = numpy.zeros(shape=(rMax,qMax)) #makes a blank numpy array
	for n in range(rMax): #runs through every r
		for m in range(qMax): #runs through every angle for q
			W[n][m]=random.random() #fills blank numpy array with random noise
	#print "You made a circle of randomly placed grey dots, congratulations."
	return W
	
def FrameProbAssign(W, frameStack, frameNo, phi): #calculates 
	Pf=1
	for pixNo in range(len(frameStack[frameNo])): #run through each pixel in the given frame
		r=frameStack[frameNo][pixNo][1] #find the first matching r value in the intensity model
		q=frameStack[frameNo][pixNo][2]/angStep		#jump to the correct q
		Pi=W[r][q]*frameStack[frameNo][pixNo][0]		
		frameStack[frameNo][pixNo][3][phi] = Pi
		Pf=Pf*Pi
	return Pf #return the product of the probabilities for each pixel
	
def ProbDistAssign(W, frameStack, angStep, frameNo): #makes a probability for each rotation and adds them to a list
	pF={}
	for n in range(360/angStep): #runs for 360 devided by the number of steps the user request
		phi=n*angStep
		frameStack=RotateFrame(frameStack,frameNo,angStep) #rotate the frame
		m=FrameProbAssign(W, frameStack, frameNo, phi) #calculate probability
		pF[phi]=m #make a dictionary entry with the angle of rotation as key and the probability
	return pF #returns a list of tuples with the rotation and probability
	
def CalcProbs(W, frameStack, angStep):
	pF=[]
	for n in range((len(frameStack))-1):
		pF.append(ProbDistAssign(W, frameStack, angStep, n))
	return pF
	
def IntensityModelGen(frameStack, rMax, qMax, angStep, pF):
	intensityModel=BlankArrayWithBackground(rMax,qMax) #make a background intensity map to add the probability ditributions to
	for frameNo in range((len(frameStack))-1): #for every frame
		for pixelNo in range(len(frameStack[frameNo])): #and every pixel in that frame
			n=0
			for n in range(360/angStep): #and ever rotation of that pixel
				q=int((RotatePixel(frameStack,frameNo,pixelNo,n*angStep))/angStep )
				r=int(frameStack[frameNo][pixelNo][1])
				i=(frameStack[frameNo][pixelNo][3][n*angStep])*pF[frameNo][n*angStep]
				intensityModel[r][q]=intensityModel[r][q]+i
	#for m in range(len(W)): #old normalisation step, needs rewriting as a new function
	#	if not W[m][3]==0:
	#		W[m][0]=W[m][0]/W[m][3]
	return intensityModel #returns an un-normalised intensity model
	
def PlotStuff(pF, angStep, frameStack): 
		for n in range(len(pF)): #chacks the number of frames in the probability dictionary
			probList=[]
			for m in range(len(pF[n])): #runs through all the rotations given
				degProb=(m*angStep, pF[n][m*angStep])
				probList.append(degProb) #makes a list of tuples that GnuPlot can read
			gp = Gnuplot.Gnuplot()
			gp.title('Plot of frame (%d)s probability with regards to an intensity model at a set of rotations' % n)
			gp.xlabel("degrees of rotation")
			gp.ylabel("calculated probability value")
			gp('set style data linespoints')
			gp.plot(probList)
			gp.hardcopy("AngvsProb(%d)" % n)
			#sampleIMG=WriteFramesImage(frameStack, n)
			#sampleIMG.save("Frame (%d) unrotated.jpg" % n)

rMax=256
angStep=1
qMax=int(360/angStep)
polarImageArray=DrawSpiral(rMax,angStep,qMax)
frameStack=MakeFrameStack(polarImageArray,angStep)
#intensityModel=RandomIntensityModelGen(rMax,angStep)
#iterateFor=5
#for a in range(iterateFor):
#pF=CalcProbs(intensityModel, frameStack, angStep)
#print ("probability distribution %d calculated" %a)
#del intensityModel[:]

pF=CalcProbs(polarImageArray, frameStack, angStep)
#PlotStuff(pF, angStep, frameStack)
intensityModel=IntensityModelGen(frameStack, rMax, qMax, angStep, pF)
raw_input("Break point, hit enter.")
