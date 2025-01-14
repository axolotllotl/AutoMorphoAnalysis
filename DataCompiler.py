import csv
import os.path
import math
import sys

def findMiddleThree( image, particles ):
	"This locates the three clusters closest to the middle of the image"
	Cx = int(image['Width']) / 2 
	Cy = int(image['Height']) / 2


	first, second, third = {}, {}, {}

	for part in particles:
		part['centerDistance'] = math.sqrt((Cx - float(part['X']))**2 + (Cy - float(part['Y'])) **2)

		if part['centerDistance'] < (first.get('centerDistance') or sys.maxsize):
			third = second 
			second = first 
			first = part 
		elif part['centerDistance'] < (second.get('centerDistance') or sys.maxsize):
			third = second 
			second = part 
		elif part['centerDistance'] < (third.get('centerDistance') or sys.maxsize):
			third = part

	return first, second, third

def findCroppedClusters( image, particles, width, height):
	"This locates all the clusters in a box cropped by width and height"

	clusters = []

	for part in particles:
		if (float(part['X']) > width and float(part['X']) < float(image['Width']) - width):
			if (float(part['Y']) > height and float(part['Y']) < float(image['Height']) - height):
				clusters.append(part)

	return clusters

def calculateDistance( ref, particles ):
	"This calculates the distance between the reference cluster and all others, returning a list of distances"

	distances = []
	for part in particles:
		if part != ref: 
			distance =  math.sqrt((float(ref['X']) - float(part['X']))**2 + (float(ref['Y']) - float(part['Y'])) **2) 
			distances.append(distance)

	return distances


#  Takes the directory from the macro 
directory = getArgument()
f = open(directory + "/output.csv", 'w')
f.close()
i = 0
j = 0

#  Loops through the csv files (with precise naming) if they exist 

while os.path.isdir(directory + chr(ord('A')+i)):
	di = directory + chr(ord('A')+i)
	while os.path.isfile(di+ "/particle_data_" + str(j) + ".csv"):


		# opens the measurement data file and adds the information to the 'image' dictionary 
		#	'Mean' 'StdDev'	'Min' 'Max'	'Witdh'	'Height'

		with open(di + "/measure_data_" + str(j) + ".csv") as mfile:
			reader = csv.DictReader(mfile, delimiter=',')
			for index in reader:
				image = index

#		os.remove(di+ "/measure_data_" + str(j) + ".csv")
		# opens the particle data file and adds the information to the 'particles' dictionary table  
		#	'Area' 'X' 'Y' 'Perim.'	'Circ' 'AR'	'Round'	'Solidity'
		
		with open(di + "/particle_data_" + str(j) + ".csv", 'rb') as pfile:
			buf = csv.DictReader(pfile, delimiter=',')

			# writing all of the particle data into dictionary list "particles"

			particles = []
			count = 0
			for row in buf:
				particles.append(row)
				count += 1

			for item in particles:
				item['Image'] = j
				item['Cell Line'] = chr(ord('A')+i)

			references = findMiddleThree(image, particles)

			for ref in references:
				if ref:
					distances = calculateDistance(ref, particles)
					ref['Distances'] = distances
					if len(distances) > 0:
						ref['Average Distance'] = sum(distances) / len(distances)

			# marks the clusters that are near the edge

			edgeClusters = findCroppedClusters(image, particles, 100, 100)

			for item in edgeClusters:
				item['Include'] = True

#		os.remove(di+ "/particle_data_" + str(j) + ".csv")

		with open(di + "/output.csv", 'a') as csvfile:
			
			fieldnames = ['Cell Line', 'Image', 'Area', 'X', 'Y', 'Solidity', 'Circ.', 'Round', 'Perim.', 'Include', 'Average Distance']
			writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore', lineterminator = '\n')
			if os.path.getsize(di + "/output.csv") < 1:
				writer.writeheader()
			for item in particles:
				writer.writerow(item)

		j += 1

	with open(di + "/output.csv", 'rb') as ofile:
		
		buf = csv.DictReader(ofile, delimiter=',')
		particles = []
		for row in buf:
			particles.append(row)


	line = {}
	total_size = 0
	total_distance = 0
	line['Num. particles'] = len(particles)
	count = 0

	for item in particles:
		if 'Include' in item:
			total_size = total_size + int(item['Area']) 
		if item['Average Distance']:
			total_distance = total_distance + float(item['Average Distance'])
			count = count + 1

	line['Cell Line'] = chr(ord('A')+i)
	line['Ave. Size'] = total_size / len(particles)
	line['Ave. Distance'] = total_distance / count

	with open(directory + "/output.csv", 'a') as csvfile:
			
			fieldnames = ['Cell Line', 'Num. particles', 'Ave. Size', 'Ave. Distance']
			writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore', lineterminator = '\n')
			if os.path.getsize(directory + "/output.csv") < 1:
				writer.writeheader()
			writer.writerow(line)

	i += 1