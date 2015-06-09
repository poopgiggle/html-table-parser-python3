from html_table_parser import HTMLTableParser
import sys
import re
import json

pattern = re.compile('(.*?) \((.*?)(/(.*?))?\)')
def get_param_pgn_pid(param_string):
	match = pattern.search(param_string)
	(name,pgn_or_pid,dont_care,pid) = match.groups()
	return (name,pgn_or_pid,pid)
	
def build_dict_list(header,list_of_lists):
	dicts = []
	for l in list_of_lists:
		dicts.append(dict(zip(header,l)))

	return dicts

record_dict = {}

if len(sys.argv) < 3:
	print('''USAGE: %s <infile> <outfile>
		infile: DG Diagnostics html report
		outfile: json filename''' % sys.argv[0]
		)
	sys.exit()


try:
	with open(sys.argv[1],'r') as f:
		reportfile = f.read()
except:
	print("Could not open report file.")
	sys.exit()

p = HTMLTableParser()
try:
	p.feed(reportfile)
except:
	print("Could not parse report file.")
	sys.exit()

J1587faultheader = ['Type', 'MID', 'MID Description', 'Code', 'FMI', 
 					'Code/FMI Description', 'Count', 'STD/PP2', 'SID/PID']



if len(p.tables[0]) >= 5:
	J1587_faults = p.tables[0][4:]
else:
	J1587_faults = []

j1587_fault_records = build_dict_list(J1587faultheader,J1587_faults)

record_dict.update({"J1587Fault": j1587_fault_records})

J1939_fault_header = ['Type', 'ECU', 'ECU Description', 'SPN', 'FMI', 
					'Count', 'SPN/FMI Description', 'MIL', 'RSL', 'AWL', 'PL', 
					'fMIL', 'fRSL', 'fAWL', 'fPL', 'CM']

if len(p.tables[2]) >= 2:
	J1939_faults = p.tables[2][1:]
else:
	J1939_faults = []

j1939_fault_record = build_dict_list(J1939_fault_header,J1939_faults)

record_dict.update({"J1939Fault":j1939_fault_record})

J1587_component_header = ['MID', 'MID Description', 'VIN', 'Make', 
						'Model', 'Serial #', 'Unit #', 'Software ID']

if len(p.tables[6]) > 2:
	J1587_component = p.tables[2:]
else:
	J1587_component = []

j1587_component_record = build_dict_list(J1587_component_header,J1587_component)
record_dict.update({"J1587Component":j1587_component_record})

J1939_component_header = ['ECU', 'ECU Description', 'VIN', 'Make', 'Model', 
						'Serial #', 'Unit #', 'Software ID', 'ECU Part #', 
						'ECU Serial #', 'ECU Location', 'ECU Type']

if len(p.tables[7]) > 2:
	J1939_component = p.tables[2:]
else:
	J1939_component = []

j1939_component_record = build_dict_list(J1939_component_header,J1939_component)
record_dict.update({"J1939Component":j1939_component_record})

total_truck_header = ['Parameter', 'PGN','PID', 'J1939Metric', 'J1587Metric', 
					  'Metric', 'J1939English', 'J1587English', 'English']

total_truck = []
if len(p.tables[8]) > 2:
	for i in range(2,len(p.tables[8])):
		(name,pgn,pid) = get_param_pgn_pid(p.tables[8][i][0])
		total_truck.append([name,pgn,pid]+p.tables[8][i][1:])

total_truck_record = build_dict_list(total_truck_header,total_truck)
record_dict.update({"TotalTruck":total_truck_record})

try:
	with open(sys.argv[2],'w') as f:
		json.dump(record_dict,f)
except:
	print("Could not open %s for writing." % sys.argv[2])
	sys.exit()