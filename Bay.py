import csv
import math
import cv2
import numpy as np
from collections import Counter


#Loading the data extracted previously
class Brain(object):
	def loadCsv(self,filename):
		lines = csv.reader(open(filename, "rb"))
		dataset = list(lines)
		for i in range(len(dataset)):
			dataset[i]=[float(x) for x in dataset[i]]
		return dataset

#Seperates the datas according to shape

	def separateByClass(self,dataset):
		separated = {}
		for i in range(len(dataset)):
			vector = dataset[i]
			if (vector[-1] not in separated):
				separated[vector[-1]] = []
			separated[vector[-1]].append(vector)
			#print separated
		return separated

#Finding mean

	def mean(self,numbers):
		return sum(numbers)/float(len(numbers))

#Finding Standard Deviation

	def stdev(self,numbers):
		avg=self.mean(numbers)
		variance=sum([pow(x-avg,2) for x in numbers])/float(len(numbers)-1)
		return math.sqrt(variance)

#Getting mean and varianace of each attributes in all extracted rows

	def summarize(self,dataset):
		summaries = [(self.mean(attribute), self.stdev(attribute)) for attribute in zip(*dataset)]
		del summaries[-1]
		return summaries

#Doing the above function according to seperated class

	def summarizeByClass(self,dataset):
		separated = self.separateByClass(dataset)
		summaries = {}
		for classValue, instances in separated.iteritems():
			summaries[classValue] = self.summarize(instances)
		return summaries
	
#Probablity of x being in that class

	def calculateProbability(self,x, mean, stdev):
		exponent = math.exp(-(math.pow(x-mean,2)/(2*math.pow(stdev,2))))
		return (1 / (math.sqrt(2*math.pi) * stdev)) * exponent

#Calculating probablity of a particular complete group

	def calculateClassProbabilities(self,summaries, inputVector):
		probabilities = {}
		for classValue, classSummaries in summaries.iteritems():
			probabilities[classValue] = 1
			for i in range(len(classSummaries)):
				mean, stdev = classSummaries[i]
				x = inputVector[i]
				probabilities[classValue] *= self.calculateProbability(x, mean, stdev)
		return probabilities

#Extracting moments of input test image

	def testImg1(self,org_img):
		img=cv2.cvtColor(org_img,cv2.COLOR_BGR2GRAY)
		thresh=cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
		Humom=cv2.HuMoments(cv2.moments(thresh)).flatten()
		#print(Humom)
		return Humom

	def testImg2(self,org_img):
		means = cv2.mean(org_img)
		means = means[:3]
		#print(means)
		return means

	def testImg3(self,org_img):
		(means2, stds) = cv2.meanStdDev(org_img)
		stats = np.concatenate([means2, stds]).flatten()
		#print(stats)
		return stats

#To predict to which class the input image belongs to

	def predict(self,summaries, inputVector):
		probabilities = self.calculateClassProbabilities(summaries, inputVector)
		#print (probabilities)
		bestLabel, bestProb = None, -1
		for classValue, probability in probabilities.iteritems():
			if bestLabel is None or probability > bestProb:
				bestProb = probability
				bestLabel = classValue
		return bestLabel

#main function being called

	def detect(self,img):
		filename1='HuMoments.csv'
		filename2='RGB.csv'
		filename3='MeanStdDev.csv'
		dataset1=self.loadCsv(filename1)
		dataset2=self.loadCsv(filename2)
		dataset3=self.loadCsv(filename3)
		summary1=self.summarizeByClass(dataset1)
		summary2=self.summarizeByClass(dataset2)
		summary3=self.summarizeByClass(dataset3)
		result = [10,10,10]
		img = cv2.flip(img, 1)
		inputvector1 = self.testImg1(img)
		inputvector2 = self.testImg2(img)
		inputvector3 = self.testImg3(img)
		result[0] = self.predict(summary1 , inputvector1)
		result[1] = self.predict(summary2 , inputvector2)
		result[2] = self.predict(summary3 , inputvector3)
		prediction = Counter(result)
		print prediction.most_common(1)[0][0]
		return prediction.most_common(1)[0][0]
			
			


