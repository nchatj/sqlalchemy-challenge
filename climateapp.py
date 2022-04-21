#DEPENDENCIES
import pandas as pd
import numpy as np
import datetime as dt

from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#DB

engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)

Base = automap_base()

Base.prepare(engine, reflect=True)

table_m = Base.classes.measurement
table_s = Base.classes.station

session = Session(engine)

#Flask

app = Flask(__name__)

@app.route("/")

def startpage():
    return (
        f"API Static Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"API Dynamic Routes (Dates must be in YYYY-MM-DD format):<br/>"
        f"/api/v1.0/<start>start date<br/>"
        f"/api/v1.0/<start>start date/<end>end date<br/>"
    )

@app.route("/api/v1.0/precipitation")

def precipitation():

    precipitation_1617 = session.query(table_m.date, table_m.prcp).filter(table_m.date >= '2016-08-23').order_by(table_m.date).all()
    session.close()
    prcp_dic = {}
    for date, prcp in  precipitation_1617:
        prcp_dic[date] = prcp
    
    return jsonify(prcp_dic)

@app.route("/api/v1.0/stations")

def stations():

    station_query = session.query(table_s.station, table_s.id, table_s.name, table_s.latitude, table_s.longitude, table_s.elevation).all()
    session.close()
    station_list = list(np.ravel(station_query))

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")

def tobs():

    tobs_query = session.query(table_m.tobs).filter(table_m.date >= '2016-08-23').filter(table_m.station == "USC00519281").all()
    session.close()
    tobs_list = list(np.ravel(tobs_query))

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")

def start(start):

    try:
        start = dt.datetime.strptime(start,"%Y-%m-%d")
        start_date = session.query(func.min(table_m.tobs), func.max(table_m.tobs), func.avg(table_m.tobs)).filter(table_m.date >= start).all()
        session.close()

        start_date_list = list(np.ravel(start_date))
        start_date_dict = {"min_temp" : start_date_list[0], "max_temp" : start_date_list[1], "avg_temp" : start_date_list[2]}

        return jsonify(start_date_dict)

    except ValueError:
        return "Format must be YYYY-MM-DD"

@app.route("/api/v1.0/<start>/<end>")

def startend(start, end):

    try:
        start = dt.datetime.strptime(start,"%Y-%m-%d")
        end = dt.datetime.strptime(end,"%Y-%m-%d")

        if start >= end:
            return "ERROR: Date range incomprehensible"

        else:
            startend_query = session.query(func.min(table_m.tobs),func.max(table_m.tobs),func.avg(table_m.tobs)).filter(table_m.date >= start).filter(table_m.date <= end).all()
            session.close()
            startend_date_list = list(np.ravel(startend_query))
            startend_date_dict = {"date range start" : start, "date range end" : end, "min_temp" : startend_date_list[0], "max_temp" : startend_date_list[1], "avg_temp" : startend_date_list[2]}
        
        return jsonify(startend_date_dict)

    except ValueError:
        return "Format must be YYYY-MM-DD"

if __name__ == '__main__':
    app.run(debug=True)
