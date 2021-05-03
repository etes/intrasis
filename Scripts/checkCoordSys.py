# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        Intrasis
# Purpose:
#
# Author:      Ermias B. Tesfamariam
#
# Created:     12.11.2018
# Copyright:   (c) ermiasbt 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import arcpy
import os
import sys
import subprocess
import csv
from utils import runcmd

reload(sys)
sys.setdefaultencoding("utf-8")

#global variables
#set environment variables for Postgresql
my_env = os.environ.copy()
my_env["PGHOST"] = 'localhost'
my_env["PGPORT"] = '5432'


class CheckCoordSys(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Check Coordinate System"
        self.description = "Sjekkes kooridnat system til Intrasis geometriene"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        """
        in_csv = arcpy.Parameter(
            displayName="Input CSV",
            name="in_csv",
            datatype="DEFile",
            parameterType="Required",
            direction="Input")
        in_csv.filter.list = ['txt', 'csv']
        in_csv.description = "Input csv file containing IntrasisIds"
        """

        pg_version = arcpy.Parameter(
            displayName="Select PostgreSQL version",
            name="pg_version",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        pg_version.filter.type = "ValueList"
        pg_version.filter.list= ["12", "11", "10", "9.6", "9.5", "9.4", "9.3", "9.2", "9.1", "9"]
        pg_version.value = "9.6"

        db_user = arcpy.Parameter(
            displayName="Database user",
            name="db_user",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        db_user.value = "postgres"

        db_password = arcpy.Parameter(
            displayName="Database password",
            name="db_password",
            datatype="GPStringHidden",
            parameterType="Required",
            direction="Input")

        db_name = arcpy.Parameter(
            displayName="Database name",
            name="db_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        db_name.parameterDependencies = [pg_version.name, db_user.name, db_password.name]

        params = [pg_version, db_user, db_password, db_name]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        if parameters[0].valueAsText:
            pg_version = parameters[0].valueAsText
            psql = "C:\\Program Files\\PostgreSQL\\{0}\\bin\\psql.exe".format(
                pg_version)

        if parameters[1].value and parameters[2].value:
            my_env["PGUSER"] = str(parameters[1].value)
            my_env["PGPASSWORD"] = str(parameters[2].value)
            args = [psql, "-Atc", "select datname from pg_database"]
            return_message = runcmd(args, my_env)
            parameters[3].filter.list = return_message[1].split()
        else:
            parameters[3].filter.list = []
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        if parameters[0].valueAsText:
            pg_version = parameters[0].valueAsText
            psql = "C:\\Program Files\\PostgreSQL\\{0}\\bin\\psql.exe".format(
                pg_version)
            if not os.path.isfile(psql):
                parameters[0].setErrorMessage("PostgreSQL version is invalid \
                    Please select the correct PostgreSQL version.")
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        #global psql
        #in_csv = parameters[0].valueAsText
        pg_version = parameters[0].valueAsText
        db_user = parameters[1].valueAsText
        db_password = parameters[2].valueAsText
        db_name = parameters[3].valueAsText

        psql = "C:\\Program Files\\PostgreSQL\\{0}\\bin\\psql.exe".format(pg_version)

        my_env["PGUSER"] = str(db_user)
        my_env["PGPASSWORD"] = str(db_password)
        my_env["PGDATABASE"]= str(db_name)

        srid_null = ("""select count(st_srid(the_geom)) """
                    """from "GeoObject" where st_srid(the_geom) = 0;""")
        geobject_total = """select count(*) from "GeoObject";"""
        return_msg_srid = runcmd([psql, '-Atc', srid_null], my_env)
        return_msg_total = runcmd([psql, '-Atc', geobject_total], my_env)
        messages.addMessage(
            """{0} geometrier av {1} uten koordinat system
            """.format(return_msg_srid[1], return_msg_total[1]))
        return
