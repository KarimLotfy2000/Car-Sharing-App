import jaydebeapi
import os
import csv
import re

def csv_reader(path):
    with open(path, "r") as csvfile:
        tmp = {}
        reader = csv.reader(csvfile, delimiter='=')
        for line in reader:
            tmp[line[0]] = line[1]
    return tmp

config = csv_reader("properties.settings")

rechnername = config["rechnername"]
username = config["username"]
password = config["password"]
database = config["database"]

class DBUtil:

    def __init__(self):
        pass

    def getConnection(self):
        try:
            import jpype
            if jpype.isJVMStarted() and not jpype.isThreadAttachedToJVM():
                jpype.attachThreadToJVM()
                jpype.java.lang.Thread.currentThread().setContextClassLoader(
                    jpype.java.lang.ClassLoader.getSystemClassLoader())
            conn = jaydebeapi.connect("com.ibm.db2.jcc.DB2Driver",
                                      "jdbc:db2:{database}".format(
                                          database=database
                                      ),
                                      {
                                          'securityMechanism': "4"
                                      },
                                      "jdbc-1.0.jar"
                                      )
            return conn
        except Exception as e:
            print(e)

    def getExternalConnection(self):

        try:
            # Fix
            import jpype
            if jpype.isJVMStarted() and not jpype.isThreadAttachedToJVM():
                jpype.attachThreadToJVM()
                jpype.java.lang.Thread.currentThread().setContextClassLoader(
                    jpype.java.lang.ClassLoader.getSystemClassLoader())
            conn = jaydebeapi.connect("com.ibm.db2.jcc.DB2Driver",
                                      "jdbc:db2://"
                                      "{rechnername}.is.inf.uni-due.de:50{gruppennummer}/{database}".format(
                                          rechnername=rechnername,
                                          gruppennummer=re.match(r"([a-z]+)([0-9]+)", username, re.I).groups()[1],
                                          database=database
                                          # user=username.strip()
                                      ),
                                      {
                                          'user': username,
                                          'password': password,
                                          'securityMechanism': "3"
                                      },
                                      os.path.join(os.getcwd(), 'jdbc-1.0.jar')
                                      )
            return conn
        except Exception as e:
            print(e)

    def checkDatabaseExists(self):
        exists = False
        conn = False

        try:
            conn = self.getConnection()
            if conn is not None:
                exists = True
        except Exception as e:
            print(e)
        finally:
            conn.close()

        return exists

    def checkDatabaseExistsExternal(self):
        exists = False
        conn = False

        try:
            conn = self.getExternalConnection()
            if conn is not None:
                exists = True
        except Exception as e:
            print(e)
        finally:
            conn.close()

        return exists
