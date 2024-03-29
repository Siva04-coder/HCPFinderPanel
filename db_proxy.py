import os
import mail
import EnDe
import datetime
import requests
import pandas as pd
import mysql.connector

from uszipcode import SearchEngine
engine = SearchEngine()

from flask import request, session
from werkzeug.utils import secure_filename

root_path = os.path.dirname(os.path.abspath(__file__))

hs = "aGNwZmluZGVyLmNrcXVvcGpvdGVpYi51cy1lYXN0LTIucmRzLmFtYXpvbmF3cy5jb20="
us = "bWFzb3JpYWRtaW4="
ps = "YiVFWnVYOGtMaGdqZSFMIw=="
ds = "aGNwZmluZGVy"
API_KEY = "AIzaSyCUCzgqm0XAkC68zLwI2hwoLwpwJEw6_Dc"

def register():
    if request.method == 'POST':

        conn = mysql.connector.connect(
            host=str(EnDe.decode(hs)), 
            user=str(EnDe.decode(us)), 
            port='3306', 
            password=str(EnDe.decode(ps)),
            database=str(EnDe.decode(ds)))

        cur=conn.cursor()
        firstname = request.form['FirstName']
        lastname = request.form['LastName']
        email=request.form['Email']
        password=request.form['Password']
        password = EnDe.encode(password).decode()
        contactnumber= request.form['ContactNumber']
        designation=request.form['Designation']
        street=request.form['Street']
        city=request.form['City']
        state=request.form['State']
        country=request.form['Country']
        zipcode=request.form['Zipcode']
        License=request.form['license']
        Npi=request.form['Npi']

        
        check_email = pd.read_sql_query("Select Email from register_data Where Email='" +email+"'", conn)

        if check_email.empty:

            address = str(street)+","+str(city)+","+str(state) + \
            ", United States,"+str(zipcode)

            params = {
                'key': API_KEY,
                'address': address
            }
            base_url = "https://maps.googleapis.com/maps/api/geocode/json?"
            response = requests.get(base_url, params=params).json()

            geometry = response['results'][0]['geometry']
            lat = geometry['location']['lat']
            lng = geometry['location']['lng']

            cur.execute("insert into register_data (Firstname,Lastname,Password,ContactNumber,Email,Street,City,State,Country,Zipcode,Designation,Latitude,Longitude,License,NPI) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(firstname,lastname,password,contactnumber,email,street,city,state,country,zipcode,designation,lat,lng,License,Npi))
            conn.commit()
            cur.close()

            register_mail(firstname, lastname, email)
            
            return True

        else:
            return False    
   
    
def check_user(email,password):
    conn = mysql.connector.connect(
        host=str(EnDe.decode(hs)), 
        user=str(EnDe.decode(us)), 
        port='3306', 
        password=str(EnDe.decode(ps)),
        database=str(EnDe.decode(ds)))   

    password = EnDe.encode(password).decode()
    usertype = ''

    user = pd.read_sql_query("Select * from register_data Where Email='" +
                        email+"' and Password='"+password+"' and Status='Approved'", conn)
    if user.empty:
        admin = pd.read_sql_query("Select * from Admins Where username='" +
                        email+"' and password='"+password+"'", conn)

        if admin.empty:
            name = usertype
            return False, usertype, name

        else:
            usertype = 'Admin'
            name = usertype
            return True, usertype, name

    else:
        usertype = 'User'
        name = user['Firstname'].to_list()[0] + " " + user['Lastname'].to_list()[0]
        return True, usertype, name


def get_register_table():
    conn = mysql.connector.connect(
        host=str(EnDe.decode(hs)), 
        user=str(EnDe.decode(us)), 
        port='3306', 
        password=str(EnDe.decode(ps)),
        database=str(EnDe.decode(ds))) 

    data = pd.read_sql_query("Select * from register_data", conn)

    new_dfs = []
    for idx, row in data.iterrows():
        new_df={
                "Id":row["ID"],
                "Firstname":row["Firstname"],
                "Lastname":row["Lastname"],
                "ContactNumber":row["ContactNumber"],
                "Email":row["Email"],
                "Address":row["Street"]+','+row["City"]+','+row["State"]+','+row["Country"]+','+str(row["Zipcode"]),
                "Designation":row["Designation"],
                "Status":row["Status"],
                "Reason":row["Reason"],
                "License":row["License"],
                "NPI":row["NPI"]
            }
        new_dfs.append(new_df)
    
    ret_data = pd.DataFrame(new_dfs)
    
    return ret_data


def get_pagination_data():
    conn = mysql.connector.connect(
            host=str(EnDe.decode(hs)), 
            user=str(EnDe.decode(us)), 
            port='3306', 
            password=str(EnDe.decode(ps)),
            database=str(EnDe.decode(ds)))


    if request.method == 'POST':
        draw = request.form['draw'] 
        row = int(request.form['start'])
        rowperpage = int(request.form['length'])
        searchValue = request.form["search[value]"]
        
        count_data = pd.read_sql_query("select count(*) as total from register_data", conn)
        totalRecords = count_data['total'].iloc[0]
        
        likeString = "%" + str(searchValue) +"%"
        filter_count_data = pd.read_sql_query("SELECT count(*) as total from register_data WHERE Firstname LIKE '"+likeString+"' OR Lastname LIKE '"+likeString+"' OR Designation LIKE '"+likeString+"' OR ContactNumber LIKE '"+likeString+"' OR Email LIKE '"+likeString+"' OR Street LIKE '"+likeString+"' OR City LIKE '"+likeString+"' OR State LIKE '"+likeString+"';", conn)
        totalRecordwithFilter = filter_count_data['total'].iloc[0]

        if searchValue=='':
            data = pd.read_sql_query("SELECT * FROM register_data ORDER BY ID asc limit "+ str(row) +", "+ str(rowperpage) +";", conn)
        else:
            data = pd.read_sql_query("SELECT * FROM register_data WHERE Firstname LIKE '"+likeString+"' OR Lastname LIKE '"+likeString+"' OR Designation LIKE '"+likeString+"' OR ContactNumber LIKE '"+likeString+"' OR Email LIKE '"+likeString+"' OR Street LIKE '"+likeString+"' OR City LIKE '"+likeString+"' OR State LIKE '"+likeString+"' limit "+str(row)+", "+str(rowperpage)+";", conn)
        
        
        new_dfs = []
        for idx, row in data.iterrows():
            new_df={
                    "Id":row["ID"],
                    "Firstname":row["Firstname"],
                    "Lastname":row["Lastname"],
                    "ContactNumber":row["ContactNumber"],
                    "Email":row["Email"],
                    "Address":row["Street"]+','+row["City"]+','+row["State"]+','+row["Country"]+','+str(row["Zipcode"]),
                    "Designation":row["Designation"],
                    "Status":row["Status"],
                    "Reason":row["Reason"],
                    "License":row["License"],
                    "NPI":row["NPI"]
                }
            new_dfs.append(new_df)

        response = {
            'draw': draw,
            'iTotalRecords': totalRecords,
            'iTotalDisplayRecords': totalRecordwithFilter,
            'aaData': new_dfs,
        }
        
    return response


def bulk_upload():
    conn = mysql.connector.connect(
        host=str(EnDe.decode(hs)), 
        user=str(EnDe.decode(us)), 
        port='3306', 
        password=str(EnDe.decode(ps)),
        database=str(EnDe.decode(ds))) 

    folder_path = 'static/upload_data'
 
    if request.method == 'POST':

        status = True
        files = request.files.getlist('files')

        for file in files:
            filename = secure_filename(file.filename)
            file_path = os.path.join(folder_path, filename)
            file.save(file_path)

            data = pd.read_excel(file_path, engine='openpyxl')
            for idx, row in data.iterrows():
                try:
                    firstname = row['Firstname']
                    lastname = row['Lastname']
                    email=str(row['Email'])
                    if email == "nan":
                        email = ""
                    # password=row['Password']
                    # if password != None:
                        # if str(password) != "" and str(password) != "nan":
                            # password = EnDe.encode(password).decode()
                    # password = EnDe.encode(password).decode()
                    contactnumber= row['ContactNumber']
                    designation=row['Speciality']
                    street=row['Street']
                    city=row['City']
                    state=row['State']
                    country=row['Country']
                    zipcode=row['Zipcode']
                    npi=row['NPI']
    
                    # check_email = pd.read_sql_query("Select Email from register_data Where Email='" +email+"'", conn)
    
                    # if check_email.empty:
                    address = str(street)+","+str(city)+","+str(state) + \
                    ", United States,"+str(zipcode)
    
                    params = {
                        'key': API_KEY,
                        'address': address
                    }
                    base_url = "https://maps.googleapis.com/maps/api/geocode/json?"
                    response = requests.get(base_url, params=params).json()
    
                    geometry = response['results'][0]['geometry']
                    lat = geometry['location']['lat']
                    lng = geometry['location']['lng']
    
                    cur=conn.cursor()
                    cur.execute("insert into register_data (Firstname,Lastname,Password,ContactNumber,Email,Street,City,State,Country,Zipcode,Designation,NPI,Latitude,Longitude,Status) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(firstname,lastname,password,contactnumber,email,street,city,state,country,zipcode,designation,npi,lat,lng,'Pending'))
                    conn.commit()
                    cur.close()
                except Exception as e:
                    print("Error: ", str(e))
                # else:
                    # status = email
                    # break

        return status


def reject_doctor():
    if request.method=="POST":
        conn = mysql.connector.connect(
            host=str(EnDe.decode(hs)), 
            user=str(EnDe.decode(us)), 
            port='3306', 
            password=str(EnDe.decode(ps)),
            database=str(EnDe.decode(ds)))

        id=request.form['id']
        firstname=request.form['firstname']
        lastname=request.form['lastname']
        email=request.form['email']

        cur=conn.cursor()
        cur.execute("Update register_data SET Status='Rejected' WHERE ID='" + id +"'")
        conn.commit()
        cur.close()
        
        reject_mail(firstname, lastname, email)


def reject_reason_doctor():
    if request.method=="POST":
        conn = mysql.connector.connect(
            host=str(EnDe.decode(hs)), 
            user=str(EnDe.decode(us)), 
            port='3306', 
            password=str(EnDe.decode(ps)),
            database=str(EnDe.decode(ds)))

        id=request.form['id']
        reason=request.form['reason']

        cur=conn.cursor()
        cur.execute("Update register_data SET Reason='" + reason +"' WHERE ID='" + id +"'")
        conn.commit()
        cur.close()


def approve_doctor():
    if request.method=="POST":
        conn = mysql.connector.connect(
            host=str(EnDe.decode(hs)), 
            user=str(EnDe.decode(us)), 
            port='3306', 
            password=str(EnDe.decode(ps)),
            database=str(EnDe.decode(ds)))

        id=request.form['id']
        firstname=request.form['firstname']
        lastname=request.form['lastname']
        email=request.form['email']

        cur=conn.cursor()
        cur.execute("Update register_data SET Status='Approved' WHERE ID='" + id +"'")
        conn.commit()
        cur.close()
        
        approve_mail(firstname, lastname, email)


def pending_doctor():
    if request.method=="POST":
        conn = mysql.connector.connect(
            host=str(EnDe.decode(hs)), 
            user=str(EnDe.decode(us)), 
            port='3306', 
            password=str(EnDe.decode(ps)),
            database=str(EnDe.decode(ds)))

        id = request.form['Id']
        status = request.form['Status']

        if status == 'Rejected':
            cur=conn.cursor()
            cur.execute("Update register_data SET Status='Pending' Where ID='" + id +"'")
            conn.commit()
            cur.close()


def delete_doctor():
    if request.method=="POST":
        conn = mysql.connector.connect(
            host=str(EnDe.decode(hs)), 
            user=str(EnDe.decode(us)), 
            port='3306', 
            password=str(EnDe.decode(ps)),
            database=str(EnDe.decode(ds)))

        id=request.form['id']

        cur=conn.cursor()
        cur.execute("Delete from register_data WHERE ID='" + id +"'")
        conn.commit()
        cur.close()


def change_password():
    
    if request.method=="POST":
        conn = mysql.connector.connect(
            host=str(EnDe.decode(hs)), 
            user=str(EnDe.decode(us)), 
            port='3306', 
            password=str(EnDe.decode(ps)),
            database=str(EnDe.decode(ds)))
        cur=conn.cursor()
        email = session["email"]

        currentpassword=request.form['currentpassword']
        newpassword=request.form['newpassword']
        currentpassword = EnDe.encode(currentpassword).decode()
        newpassword = EnDe.encode(newpassword).decode()
 
        user = pd.read_sql_query("Select Password from register_data Where Email='" + email +"' and Password='"+currentpassword+"' ", conn)
        if user.empty:
            conn.commit()
            cur.close()
            return False
        else:
            updatequery=("Update register_data SET Password='"+newpassword+"' WHERE Email='"+email+"' and Password='"+currentpassword+"'")
            cur.execute(updatequery)
            conn.commit()
            cur.close()
            return True


def update_data():

    if request.method == 'POST':
        conn = mysql.connector.connect(
            host=str(EnDe.decode(hs)), 
            user=str(EnDe.decode(us)), 
            port='3306', 
            password=str(EnDe.decode(ps)),
            database=str(EnDe.decode(ds)))

        cur=conn.cursor()
        email = session["email"]
        
        id = request.form['Id']
        firstname = request.form['FirstName']
        lastname = request.form['LastName']
        email=request.form['Email']
        contactnumber= request.form['ContactNumber']
        designation=request.form['Designation']
        street=request.form['Street']
        city=request.form['City']
        state=request.form['State']
        country=request.form['Country']
        zipcode=request.form['Zipcode']
        License=request.form['license']
        Npi=request.form['Npi']
        
        address = str(street)+","+str(city)+","+str(state) + \
            ", United States,"+str(zipcode)

        params = {
            'key': API_KEY,
            'address': address
        }

        base_url = "https://maps.googleapis.com/maps/api/geocode/json?"
        response = requests.get(base_url, params=params).json()
        geometry = response['results'][0]['geometry']
        lat = geometry['location']['lat']
        lng = geometry['location']['lng']

        print(firstname, email, city, zipcode)
        update=("Update register_data SET Firstname=%s,Lastname=%s,ContactNumber=%s,Email=%s,Street=%s,City=%s,State=%s,Country=%s,Zipcode=%s,Designation =%s,Latitude=%s,Longitude=%s,License=%s,NPI=%s where ID='"+ id +"'")
        value=([firstname,lastname,contactnumber,email,street,city,state,country,zipcode,designation,lat,lng,License,Npi])
        cur.execute(update,value)
        conn.commit()
        cur.close()


def update_profile():
    
    if request.method == 'POST':
        conn = mysql.connector.connect(
            host=str(EnDe.decode(hs)), 
            user=str(EnDe.decode(us)), 
            port='3306', 
            password=str(EnDe.decode(ps)),
            database=str(EnDe.decode(ds)))

        cur=conn.cursor()
        email = session["email"]
        firstname = request.form['FirstName']
        lastname = request.form['LastName']
        email=request.form['Email']
        contactnumber= request.form['ContactNumber']
        designation=request.form['Designation']
        street=request.form['Street']
        city=request.form['City']
        state=request.form['State']
        country=request.form['Country']
        zipcode=request.form['Zipcode']
        License=request.form['license']
        Npi=request.form['Npi']
        user_check="Select * from register_data Where Email='"+email+"'"
        cur.execute(user_check)
        value=cur.fetchall()
        if len(value) > 0:
            for val in value:
                firstname1=val[2]
                lastname1=val[3]
                contactnumber1=val[5]
                email1=val[6]
                street1=val[7]
                city1=val[9]
                state1=val[10]
                country1=val[11]
                zipcode1=val[12]
                designation1=val[13]
                License1=val[16]
                Npi1=val[17]

        if (firstname1==firstname or lastname1==lastname or contactnumber1==contactnumber or email1==email or street1==street or city1==city or state1==state or country1==country or designation1==designation or zipcode1==zipcode or License1==License or Npi1==Npi):       
            address = str(street)+","+str(city)+","+str(state) + \
            ", United States,"+str(zipcode)
            
            params = {
                'key': API_KEY,
                'address': address
            }
            base_url = "https://maps.googleapis.com/maps/api/geocode/json?"
            response = requests.get(base_url, params=params).json()
            geometry = response['results'][0]['geometry']
            lat = geometry['location']['lat']
            lng = geometry['location']['lng']
            update=("Update register_data SET Firstname=%s,Lastname=%s,ContactNumber=%s,Email=%s,Street=%s,City=%s,State=%s,Country=%s,Zipcode=%s,Designation =%s,Latitude=%s,Longitude=%s,License=%s,NPI=%s where Email='"+email+"'")
            value=([firstname,lastname,contactnumber,email,street,city,state,country,zipcode,designation,lat,lng,License,Npi])
            cur.execute(update,value)
            conn.commit()
            cur.close()
            
        else: 
            address = str(street)+","+str(city)+","+str(state) + \
            ", United States,"+str(zipcode)
            
            params = {
                'key': API_KEY,
                'address': address
            }
            base_url = "https://maps.googleapis.com/maps/api/geocode/json?"
            response = requests.get(base_url, params=params).json()
            geometry = response['results'][0]['geometry']
            lat = geometry['location']['lat']
            lng = geometry['location']['lng']
            update=("Update register_data SET Firstname=%s,Lastname=%s,ContactNumber=%s,Email=%s,Street=%s,City=%s,State=%s,Country=%s,Zipcode=%s,Designation =%s,Latitude=%s,Longitude=%s,License=%s,NPI=%s,Status='Pending' where Email='"+email+"'")
            value=([firstname,lastname,contactnumber,email,street,city,state,country,zipcode,designation,lat,lng,License,Npi])
            cur.execute(update,value)
            conn.commit()
            cur.close()
               
def fetch():
    if request.method == 'GET':
        email = session['email']
        conn = mysql.connector.connect(
            host=str(EnDe.decode(hs)), 
            user=str(EnDe.decode(us)), 
            port='3306', 
            password=str(EnDe.decode(ps)),
            database=str(EnDe.decode(ds)))
        cursor=conn.cursor()
        user_check="Select * from register_data Where Email='"+email+"'"
        cursor.execute(user_check)
        row=cursor.fetchall()
        if len(row) > 0:
            new_list=[]
            for value in row:
                for val in value:
                    new_list.append(val)
    
            conn.commit()
            cursor.close()
            return new_list

def fetch_opt(Npinumber):
        conn = mysql.connector.connect(
            host=str(EnDe.decode(hs)), 
            user=str(EnDe.decode(us)), 
            port='3306', 
            password=str(EnDe.decode(ps)),
            database=str(EnDe.decode(ds)))
        
        check_npi = pd.read_sql_query("Select NPI from register_data Where NPI='"+Npinumber+"' and Status='Approved'", conn)
        if check_npi.empty:
            return False
        else:
            return True

def update_opt():
    if request.method=="POST":
        conn = mysql.connector.connect(
            host=str(EnDe.decode(hs)), 
            user=str(EnDe.decode(us)), 
            port='3306', 
            password=str(EnDe.decode(ps)),
            database=str(EnDe.decode(ds)))

        Npinumber=request.form['Npi']
        firstname=request.form['firstname']
        lastname=request.form['lastname']
        Contact=request.form['Contact']
        contact_num = ''.join(i for i in Contact if i.isdigit())
        City=request.form['City']
        
        check_npi = pd.read_sql_query("Select Firstname, Lastname, ContactNumber, City, Email, NPI from register_data Where NPI='"+Npinumber+"'", conn)
        if check_npi.empty:
            return False
        else:
            for idx, row in check_npi.iterrows():
                if row['Firstname'].lower() != firstname.lower().strip():
                    return 'Firstname'
                elif row['Lastname'].lower() != lastname.lower().strip():
                    return 'Lastname'
                elif len(row['ContactNumber']) > 5 and ''.join(i for i in row['ContactNumber'] if i.isdigit()) != contact_num:
                        return 'ContactNumber'
                elif row['City'].lower() != City.lower():
                    return 'City'
                else:
                    cur=conn.cursor()
                    cur.execute("Update register_data SET Status='Opt-Out' WHERE NPI='" + Npinumber +"'")
                    conn.commit()
                    cur.close()
                    
                    optout_mail(row['Firstname'],row['Lastname'],row['ContactNumber'],row['City'],row['NPI'],row['Email'])

                    return True
                

def get_dashboard_data():
    
    if request.method=="POST":

        conn = mysql.connector.connect(
            host=str(EnDe.decode(hs)), 
            user=str(EnDe.decode(us)), 
            port='3306', 
            password=str(EnDe.decode(ps)),
            database=str(EnDe.decode(ds)))
        
        month=request.form['month']
        year=request.form['year']

        df = pd.read_sql_query("Select * from search_logs", conn)
        hcps = pd.read_sql_query("Select * from register_data", conn)
        hcps = hcps.rename({'ID':'hcpid'}, axis=1)
        
        #dates conversion    
        for idx, row in df.iterrows():
            try:
                if '-' not in str(row['created_on']):
                    re_date = row['created_on'].replace('/', ' ').replace(',', '')
                    format_date = datetime.datetime.strptime(re_date, '%m %d %Y %H:%M:%S %p').strftime('%m-%d-%Y')
                    df['created_on'] = df['created_on'].replace(row['created_on'], str(format_date))
            except:
                df = df[df['created_on'] != row['created_on']]
                

        df['created_on'] = pd.to_datetime(df['created_on'], errors='coerce')
        df['month'] =  df['created_on'].dt.month_name()
        df['year'] =  df['created_on'].dt.year

        df = df.sort_values(by='created_on', ascending=False)
        df['created_on'] = df['created_on'].astype(str)

        df['year'] = df['year'].astype(str)
        df = df[(df['month'] == month) & (df['year'] == year)]


        #total search
        search_df = df[df['hcpid'] == 0]
        total_search = 0
        if search_df.shape[0] > 0:
            total_search = search_df.shape[0]
            
        #total hcp
        hcp_df = df[df['hcpid'] > 0]
        total_hcp = 0
        if hcp_df.shape[0] > 0:
            total_hcp = hcp_df.shape[0]

        #lead table
        hcps = hcp_df.merge(hcps, on='hcpid')

        hcp_dfs = []
        for idx, row in hcps.iterrows():
            new_df={"Name":row["Firstname"] + ' ' + row['Lastname'],
                    "Designation":row["Designation"],
                    "Address":row["Street"] + ', ' + row["City"] + ', ' + row["State"] + ', ' + row["Zipcode"] + '.',
                    "ConnectedDate": row['created_on']}
            hcp_dfs.append(new_df)


        # top hcp
        top_connected_hcp = 0
        if len(hcp_dfs) > 0 :
            hcp_dict_df = pd.DataFrame(hcp_dfs)
            top_hcp = hcp_dict_df['Name'].value_counts()
            top_hcp = top_hcp.to_dict()

            top_hcp_list = list(top_hcp.keys())
            top_connected_hcp = top_hcp_list[0]


        # top week hcp
        top_week_hcp_df = pd.DataFrame(hcp_dfs)
        top_week_names = []
        if not top_week_hcp_df.empty:
            top_week_dates = top_week_hcp_df["ConnectedDate"].explode().unique()[:7]
            top_week_hcp_df =  top_week_hcp_df[top_week_hcp_df['ConnectedDate'] >= top_week_dates[-1]]

            top_week_name_cnt = top_week_hcp_df['Name'].value_counts()
            top_week_names = list(top_week_name_cnt.to_dict().keys())

        top_week_designation = []
        for name in top_week_names:
            top_week_designation.append(str(top_week_hcp_df[top_week_hcp_df['Name']==name]['Designation'].values[0])) 
        
        #city details
        zipcodes_df = search_df['zipcode_searched'].value_counts()
        zipcodes_dict = zipcodes_df.to_dict()

        city_dict = {}
        for key, val in zipcodes_dict.items():
            zipcode = engine.by_zipcode(key)

            if str(zipcode.state) in city_dict:
                val += int(city_dict[zipcode.state])
                city_dict[zipcode.state] = val
            else:
                city_dict[zipcode.state] = val

        #city calculation
        city_list = list(city_dict.values())
        city_cal = []
        if len(city_list) > 0:
            city_cal = [min(city_list), round(sum(city_list)/len(city_list)), max(city_list)]

        #top 5 dates
        dates_df = search_df['created_on'].value_counts()
        dates_dict = dates_df.to_dict()
        hcp_dates_df = hcp_df['created_on'].value_counts()
        hcp_dates_dict = hcp_dates_df.to_dict()

        top_dates = list(dates_dict.keys())
        search_date_cnt = list(dates_dict.values())
        
        hcp_date_cnt = []
        if len(top_dates) > 0:
            for i in top_dates:
                if i in hcp_dates_dict:
                    hcp_date_cnt.append(hcp_dates_dict[i])

        #top city
        top_city_dict = {}
        for key, val in zipcodes_dict.items():
            zipcode = engine.by_zipcode(key)
            
            if str(zipcode.major_city) in top_city_dict:
                val += int(top_city_dict[zipcode.major_city])
                top_city_dict[zipcode.major_city] = val
            else:
                top_city_dict[zipcode.major_city] = val
                
        top_city_dict = dict(sorted(top_city_dict.items(), key=lambda kv: kv[1], reverse=True))
        top_city_dict = {k:v for i, (k, v) in enumerate(top_city_dict.items()) if i < 6}
        top_cities = list(top_city_dict.keys())
        top_cities_cnt = list(top_city_dict.values())

        engine.close()

        data = {}
        data["total_search"] = total_search
        data["total_hcp"] = total_hcp
        data["top_connected_hcp"] = top_connected_hcp
        data["city_count"] = city_dict
        
        data["city_cal"] = city_cal

        data["top_dates"] = top_dates[:5]
        data["search_date_cnt"] = search_date_cnt[:5]
        data["hcp_date_cnt"] = hcp_date_cnt[:5]

        if len(top_cities) > 0:
            data['top_one_city'] = top_cities[0]
            data['top_one_city_cnt'] = top_cities_cnt[0]

        data["top_cities"] = top_cities[1:]
        data["top_cities_cnt"] = top_cities_cnt[1:]

        data["top_week_names"] = top_week_names[:5]
        data["top_week_designation"] =top_week_designation[:5]

        data["hcp_table_data"] = hcp_dfs

        return data
    


def get_gmkey():
    return API_KEY

def register_mail(firstname, lastname, email):
    body = """
    <html>
        <body>
            <p>
                Dear """ + firstname + " " + lastname + """,
            </p>
            <p>
                You have been registered with HCP finder.
            </p>
            <p>
                Thank you in advance,<br>
                <b>The MASORI Help Desk</b>
            </p>
        </body>
    </html>
    """
    mail.SendMail(email, "You have been Registered - HCP Finder", body, [])
    return


def approve_mail(firstname, lastname, email):
    body = """
    <html>
        <body>
            <p>
                Dear """ + firstname + " " + lastname + """,
            </p>
            <p>
                Your staus have been changed by HCP finder.
            </p>
            <p>
                <b>Staus: </b><b style="color: green;">Approved</b>
            </p>
            <p>
                Thank you in advance,<br>
                <b>The MASORI Help Desk</b>
            </p>
        </body>
    </html>
    """
    mail.SendMail(email, "Your staus have been changed - HCP Finder", body, [])
    return               
                

def reject_mail(firstname, lastname, email):
    body = """
    <html>
        <body>
            <p>
                Dear """ + firstname + " " + lastname + """,
            </p>
            <p>
                Your staus have been changed by HCP finder.
            </p>
            <p>
                <b>Staus: </b><b style="color: red;">Rejected</b>  
            </p>
            <p>
                Thank you in advance,<br>
                <b>The MASORI Help Desk</b>
            </p>
        </body>
    </html>
    """
    mail.SendMail(email, "Your staus have been changed - HCP Finder", body, [])
    return       


def optout_mail(firstname, lastname, contact, city, npi, email):
    body = """
    <html>
        <body>
            <p>
                Dear Acadia Pharmaceuticals,
            </p>
            <p>
            The following HCP has requested to opt-out from the Acadia HCP Locator 
            and will be removed from the search results within 72 hours.
            </p>
            <p>
                """ + npi + """ - Verified<br>
                """ + firstname + """<br>
                """ + lastname + """<br>
                """ + contact + """<br>
                """ + city + """<br>
            </p>
            <p>
                Thank you in advance,<br>
                <b>The MASORI Help Desk</b>
            </p>
        </body>
    </html>
    """
    mail.SendMail(email, "You have been Requested to Opt-Out - HCP Finder", body, [])
    return

