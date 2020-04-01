# covitrace
usage: trace_app.py [-h] [-o OUTPUT] [-a ACCURACY] patients_zip victims_zip

positional arguments:
  patients_zip          eg. $python trace_app.py takeout_p.zip takeout_v.zip
                        Patients zip file (takeout_p.zip)
  victims_zip           Victims zip file (takeout_v.zip)

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output File name .csv(will be overwritten!)
  -a ACCURACY, --accuracy ACCURACY
                        Allowed Accuracy of location instance (default = 50)
                        Recommended upto 150.. Less value prefered
