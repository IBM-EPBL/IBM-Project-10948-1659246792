from flask import Flask,render_template,request
import pickle


model=pickle.load(open('flightclf.pkl','rb'))


app=Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/prediction',methods=["POST"])
def predict():
    if request.method=="POST":
        name=request.form["name"]
        month=request.form["month"]
        if(int(month)>12):
            ans="Please Enter the correct Month"
            return render_template("index.html" ,y=ans)

        dayofmonth=request.form["dayofmonth"]
        if(int(dayofmonth)>31):
            ans="Please Enter the correct Day of Month"
            return render_template("index.html" ,y=ans)

        dayofweek=request.form["dayofweek"]
        if(int(dayofweek)>7):
            ans="Please Enter the correct Day of Week"
            return render_template("index.html" ,y=ans)
       
        
        origin=request.form["origin"]
        destination=request.form['destination']
        
        if(origin==destination):
            ans="Origin airport and destination airport can't be same"
            return render_template("index.html" ,y=ans)
       
        if(origin=="msp"):
            origin1,origin2,origin3,origin4,origin5=0,0,0,1,0
        if(origin=="dtw"):
            origin1,origin2,origin3,origin4,origin5=0,1,0,0,0
        if(origin=="jfk"):
            origin1,origin2,origin3,origin4,origin5=0,0,1,0,0
        if(origin=="sea"):
            origin1,origin2,origin3,origin4,origin5=0,0,0,0,1
        if(origin=="alt"):
            origin1,origin2,origin3,origin4,origin5=1,0,0,0,0
    
        
        
        if(destination=="msp"):
            destination1,destination2,destination3,destination4,destination5=0,0,0,1,0
        if(destination=="dtw"):
            destination1,destination2,destination3,destination4,destination5=0,1,0,0,0
        if(destination=="jfk"):
            destination1,destination2,destination3,destination4,destination5=0,0,1,0,0
        if(destination=="sea"):
            destination1,destination2,destination3,destination4,destination5=0,0,0,0,1
        if(destination=="alt"):
           destination1,destination2,destination3,destination4,destination5=1,0,0,0,0

        depthr=request.form['depthr']
        deptmin=request.form['deptmin']
        if(int(depthr)>23 or int(deptmin)>59):
            ans="Please enter the correct Departure time"
            return render_template("index.html" ,y=ans)
        else:
            dept=depthr+deptmin
       
        actdepthr=request.form['actdepthr']
        actdeptmin=request.form['actdeptmin']
        if(int(actdepthr)>23 or int(actdeptmin)>59):
            ans="Please enter the correct Actual Departure time"
            return render_template("index.html" ,y=ans)
        else:
            actdept=actdepthr+actdeptmin

       

        arrtimehr=request.form['arrtimehr']
        arrtimemin=request.form['arrtimemin']
        if(int(arrtimehr)>23 or int(arrtimemin)>59):
            ans="Please enter the correct Arrival time"
            return render_template("index.html" ,y=ans)
        else:
            arrtime=arrtimehr+arrtimemin
        
       
        if((int(actdept)-int(dept))<15):
            dept15=0
        else:
            dept15=1    

        print(dept15)
        total=[[month,dayofmonth,dayofweek,origin1,origin2,origin3,origin4,origin5,destination1,destination2,destination3,destination4,destination5,dept,actdept,dept15,arrtime]]

        value=model.predict(total)
        print(value)
        if(value==[0.]):
            ans="THE FLIGHT WILL BE ON TIME"
        else:
            ans="THE FLIGHT WILL BE DELAYED"    

    return render_template("results.html" ,y=ans)


if __name__=="__main__":
    app.run(debug=False)    



