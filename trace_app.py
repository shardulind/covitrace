import json
import csv
import os
import sys
from datetime import datetime
from dateutil import tz
from zipfile import ZipFile
from argparse import ArgumentParser, ArgumentTypeError


def trace_intersections(delta_distance, x, y):
	output = []	#x_dt, y_dt, 
	x_len = len(x)
	y_len = len(y)

	x_itr=0
	y_itr=0

	while(True):
		if( x_itr >= x_len or y_itr >= y_len):
			break

		if(x[x_itr][0] == y[y_itr][0]):
			delta_latitude = abs(float(x[x_itr][1]) - float(y[y_itr][1])) 
			delta_longitude = abs(float(x[x_itr][2]) - float(y[y_itr][2]))
			if((delta_latitude <= 0.0001) and (delta_longitude <=0.0001)):
				#print(delta_latitude)
				#print(delta_longitude)

				output.append([x[x_itr][0], x[x_itr][1],x[x_itr][2],y[y_itr][1],y[y_itr][2],x[x_itr][3],y[y_itr][3], delta_latitude, delta_longitude])
			x_itr+=1
			y_itr+=1
		elif(x[x_itr][0] > y[y_itr][0]):
			y_itr+=1
		elif(x[x_itr][0] < y[y_itr][0]):
			x_itr+=1
	return output


def trace(patient_csv, victim_csv, max_accuracy, allowed_distance, outputfn, print_output_flag):
	patient_l = []
	victim_l  = []
	print("\n\n")
	print(len(patient_csv))
	for row in patient_csv: break;
	for row in patient_csv:
		if int(row[3]) <= max_accuracy:  # row[3] : accuracy of location in meters( lesser good )
			dinank = datetime.strptime(row[0][0:16], '%Y-%m-%d %H:%M')
			patient_l.append([dinank, row[1], row[2], row[3]]) #date, lat, long, accu
			#print(patient_l[-1])

	for row in victim_csv: break;
	for row in victim_csv:
		if int(row[3]) <= max_accuracy:
			dinank = datetime.strptime(row[0][0:16], '%Y-%m-%d %H:%M')
			victim_l.append([dinank, row[1], row[2], row[3]])


	output = trace_intersections(allowed_distance,patient_l, victim_l)
	if(print_output_flag):
		print("Date         Time      Lattitude        Longitude   Accuracy1(in m)     Accuracy2(in m)\n")
		for row in output:
			print(row[0].strftime('%d/%m/%Y, %H:%M') + '  |  ' + str(row[1]) + '  |  ' + str(row[2]) + '  |  ' + str(row[5]) + '         |  ' + str(row[6]))

	print("size patient_locs: " + str(len(patient_l)))
	print("size victim_locs: " + str(len(victim_l)))
	print("intersections: " + str(len(output)))

	return output,[len(patient_l),len(victim_l),len(output)]


def write_output(filename, output):
	with open(filename, 'w', newline='') as file:
		writer = csv.writer(file)
		writer.writerow(["datetime", "p_lat", "p_lng","v_lat","v_lng","p_accu","v_accu","delta_lat","delta_lng"])

		for row in output:
			writer.writerow(row)
	print("Detailed CSV file is saved at path = " + str(str(os.getcwd()) + "/" + filename))




def json_to_csv(json_file1, json_file2):
	from_zone = tz.tzutc()
	to_zone = tz.tzlocal()
	print(os.getcwd())

	try:
		json_data_p = open(json_file1,"r")
		json_data_v = open(json_file2,"r")
		
	except:
		print("Error opening input file")
		return

	try:
		data1 = json.loads(json_data_p.read())
		data2 = json.loads(json_data_v.read())	
	except:
		print("Error decoding json")
		return

	
	items = data1["locations"]
	#print(items)
	
	patient_locs = []
	#patient_locs.append(["Time","Latitude","Longitude","Accuracy","Altitude","VerticalAccuracy","Velocity","Heading"])
	for item in items:
		if 'longitudeE7' in item and 'latitudeE7' in item:
			dt = datetime.utcfromtimestamp(int(item["timestampMs"]) / 1000)
			dt = dt.replace(tzinfo=from_zone)
			dt = dt.astimezone(to_zone)
			dt.strftime("%Y-%m-%d %H:%M:%S")
			#print(dt)
			patient_locs.append([str(dt),
				"%.8f" % (item["latitudeE7"] / 10000000), 
				"%.8f" % (item["longitudeE7"] / 10000000), 
				str(item.get("accuracy", "")), 
				str(item.get("altitude", "")), 
				str(item.get("verticalAccuracy", "")), 
				str(item.get("velocity", "")), 
				str(item.get("heading", ""))
			])

	items = data2["locations"]
	victim_locs = []
	#victim_locs.append(["Time","Latitude","Longitude","Accuracy","Altitude","VerticalAccuracy","Velocity","Heading"])
	for item in items:
		if 'longitudeE7' in item and 'latitudeE7' in item:
			dt = datetime.utcfromtimestamp(int(item["timestampMs"]) / 1000)
			dt = dt.replace(tzinfo=from_zone)
			dt = dt.astimezone(to_zone)
			dt.strftime("%Y-%m-%d %H:%M:%S")
			#print(dt)
			victim_locs.append([str(dt),
				"%.8f" % (item["latitudeE7"] / 10000000), 
				"%.8f" % (item["longitudeE7"] / 10000000), 
				str(item.get("accuracy", "")), 
				str(item.get("altitude", "")), 
				str(item.get("verticalAccuracy", "")), 
				str(item.get("velocity", "")), 
				str(item.get("heading", ""))
			])
	return patient_locs, victim_locs



def save_zip(p_file, v_file, max_accuracy=50, allowed_distance=0.0001):
	#print(os.getcwd())
	#os.chdir('media/')
	#print(os.getcwd())
	with ZipFile(p_file,'r') as zip:
		print("\nExtrectnig files\n")
		zip.extract('Takeout/Location History/Location History.json')
		print("\nExtraction completed")
		os.rename(r'Takeout/Location History/Location History.json',r'patient.json')
	with ZipFile(v_file,'r') as zip:
		print("\nExtracting files\n")
		zip.extract('Takeout/Location History/Location History.json')
		print("\nExtraction completed")
		os.rename(r'Takeout/Location History/Location History.json',r'victim.json')
	
	print("\n\nStarting to trace, hold on for a min.\n\n")
	patient_locs, victim_locs = json_to_csv(r'patient.json',r'victim.json')
	output, metadata = trace(patient_locs, victim_locs, max_accuracy, allowed_distance, 'output', True)
	return output


def main():
	arg_parser = ArgumentParser()
	arg_parser.add_argument("patients_zip", help="eg. $python trace_app.py takeout_p.zip takeout_v.zip\n\nPatients zip file (takeout_p.zip)")
	arg_parser.add_argument("victims_zip", help="Victims zip file (takeout_v.zip)")
	arg_parser.add_argument("-o", "--output",default = 'output.csv', help="Output File name .csv(will be overwritten!)")
	arg_parser.add_argument('-a', "--accuracy",default = 50, help="Allowed Accuracy of location instance (default = 50) Recommended upto 150.. Less value prefered", type=int)

	args = arg_parser.parse_args()
	output = save_zip(args.patients_zip, args.victims_zip, args.accuracy )
	write_output(args.output, output)


if __name__ == "__main__":
    sys.exit(main())