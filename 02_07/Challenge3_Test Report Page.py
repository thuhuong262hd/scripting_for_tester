import csv
import gspread
from google.oauth2.service_account import Credentials

def cal_average(num):
    sum_num = 0
    for t in num:
        sum_num = sum_num + int(t)

    avg = sum_num / len(num)
    return avg

scopes = ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive']

creds = Credentials.from_service_account_file('client_secret.json', scopes=scopes)
client = gspread.authorize(creds)
sheet = client.open('TestRunData').sheet1

#read in the data from the spreadsheet
spreadsheet_data = sheet.get_all_values()

#a note to help you out here
#   We don't need the Test Name or Average Run Time
#   data, so we can remove those from each row using
#   del row_data[x] where x is the index of the element
#   we want to remove
run_times = []
for row in spreadsheet_data:
    del row[1]
    del row[1]
    run_times.append(row)
    #Remove the first 2 items from the row since we are not
    #interested in the Test Name or Avg Run time

#read in csv data
csv_data = []
with open('LatestTestRunData.csv') as csv_file:
    #read in data using csv reader
    file_reader = csv.reader(csv_file)
    for row in file_reader:
        csv_data.append(row)

    #for the sake of simplicity we are going to assume a few things:
# 1. All of the tests in the csv data were run on the same date
# 2. The test are in the same order in the csv file as they are in the
#    spreadsheet data
#
#find the run date
#remember that we can assume that all the tests in the csv file were run on the same date
#which means we can get the run date from the 3rd column of the 2nd row in the csv data

run_date = csv_data[1][2]
#now get the first row of the run_times list and modify it to remove the oldest value
#and add in the new run date

#similar to above, do this for each remaining row
#loop over the run_times and csv_data lists and for each time through the loop,
#get the new value from the csv_data and add it to the end of the run_times row
#and then remove the oldest value from that row
#note that you can use zip to iterate over multiple lists at the same time
spreadsheet_data = []
for spreadsheet_row,csv_row in zip(run_times[1:],csv_data[1:]):
    spreadsheet_row.append(csv_row[1])
    spreadsheet_row.insert(1, cal_average(spreadsheet_row[1:]))
    spreadsheet_data.append(spreadsheet_row)

column_names = run_times[0];
column_names.insert(1, 'Average Run Time')
column_names.append(run_date)

spreadsheet_data.insert(0, column_names)
print('spreadsheet_data')
print(spreadsheet_data)

#write the new spreadsheet data back into the spreadsheet
#don't forget that lists are indexed starting from 0 and the
#spreadsheet index starts at 1.  Also remember that we want to
#start writing the data in the 3rd column in the spreadsheet
#since the first two columns have the test name and the average run time.
#As a reminder, if you want both the value and the index
#of a list you can use the enumerate function
sheet.update('A1', spreadsheet_data)

#read in the average data from the spreadsheet
#Hint: use sheet.col_values
# avg_data = sheet.col_values(1)

#intializing the chart_data list with the headers
chart_data = [["Test Name","Diff From Avg"]]
for row in spreadsheet_data[1:]:
    test_name = row[0]
    print(row[1])
    print(row[6])
    diff_from_avg = row[1] - float(row[6])
    chart_data.append([test_name, diff_from_avg])
#add test names and the difference from the average for each
#of the test to the chart_data list
#hint: use zip again to loop over both the avg_data and the
#csv_data lists at the same time


from string import Template
#first substitution is the header, the rest is the data
htmlString = Template("""<html><head><script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
<script type="text/javascript">
  google.charts.load('current', {packages: ['corechart']});
  google.charts.setOnLoadCallback(drawChart);

  function drawChart(){
      var data = google.visualization.arrayToDataTable([
      $labels,
      $data
      ],
      false);

      var chart = new google.visualization.ColumnChart(document.getElementById('chart_div'));
      chart.draw(data);
  }
</script>
</head>
<body>
<div id = 'chart_div' style='width:800; height:600'><div>
</body>

</html>""")

#format the data correctly
chart_data_str = ''
for row in chart_data[1:]:
    #create the data string
    chart_data_str += '%s, \n'%row

#substitute the data into the template
completed_html = htmlString.substitute(labels=chart_data[0], data=chart_data_str)

with open('Chart1.html','w') as f:
    #write the html string you've create to a file
    f.write(completed_html)
