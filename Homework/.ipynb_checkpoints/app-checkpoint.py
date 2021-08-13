from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt



# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup

app = Flask(__name__)

# Flask Routes

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"

    )

@app.route("/api/v1.0/stations")    
def stations():
    session = Session(engine)
    sel = [Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation]
    queryresult = session.query(*sel).all()
    session.close()

    stations = []
    for station,name,lat,lon,el in queryresult:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        stations.append(station_dict)

    return jsonify(stations)
     
       
@app.route("/api/v1.0/precipitation")    
def precipitation():
    session = Session(engine)
    """Return the precipitation data for the last year"""
    
   # Calculate the date 1 year ago from last date in database
    date_yr_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    
 # Query for the date and precipitation for the last year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= date_yr_ago).all()
   # Dict with date as the key and prcp as the value
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    
    # Calculate the date 1 year ago from last date in database
    date_yr_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    tob_data = session.query(Measurement.tobs, Measurement.date).filter(Measurement.date >= date_yr_ago).all()
    session.close()

    
    tobs_list = []
    for result in tob_data:
        temp = {}
        temp["date"] = result[1]
        temp["temprature"] = result[0]
        tobs_list.append(temp)
    return jsonify(tobs_list)


@app.route('/api/v1.0/<start>')
def start_range(start):
    session = Session(engine)
    
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    
    session.close()

    tobsfunc = []
    for min_val, avg, max_val in result:
        tobs_data = {}
        tobs_data["Min"] = min_val
        tobs_data["Average"] = avg
        tobs_data["Max"] = max_val
        tobsfunc.append(tobs_data)

    return jsonify(tobsfunc)

@app.route('/api/v1.0/<start>/<stop>')
def get_t_start_stop(start,stop):
    session = Session(engine)
    
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= stop).all()
    session.close()

    tobsfunc = []
    for min_val,avg,max_val in result:
        tobs_data = {}
        tobs_data["Min"] = min_val
        tobs_data["Average"] = avg
        tobs_data["Max"] = max_val
        tobsfunc.append(tobs_data)

    return jsonify(tobsfunc)

if __name__ == '__main__':
    app.run(debug=True)
