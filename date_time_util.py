from datetime import datetime

DB2_DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


def extractTimeFromDB2DateTimeString(datetimeStr):
    """

    :param datetimeStr: DB2 datetime format. Example: 2020-12-28 15:45:00.000000
    :return: Time string. Format: HH:mm, Example: 15:45
    """
    timeStr = None
    try:
        parsedDate = datetime.strptime(datetimeStr, DB2_DATE_FORMAT)
        timeStr = parsedDate.strftime("%H:%M")
    except Exception as e:
        print(e)

    return timeStr


def extractDateFromDB2DateTimeString(datetimeStr):
    """

    :param datetimeStr: DB2 datetime format. Example: 2020-12-28 15:45:00.000000
    :return: Date string. Format: dd.MM.yyyy, Example: 28.12.2020
    """
    dateStr = None
    try:
        parsedDate = datetime.strptime(datetimeStr, DB2_DATE_FORMAT)
        dateStr = parsedDate.strftime("%d.%m.%Y")
    except Exception as e:
        print(e)

    return dateStr


def convertDateAndTimeToDB2DateTime(dateStr, timeStr):
    """

    :param dateStr: Date as string. Format dd.MM.yyyy, Example: 28.12.2020
    :param timeStr: Time as string. Format HH:mm, Example: 15:45
    :return: DB2 datetime format (e.g 2020-12-28 15:45:00.000000)
    """
    datetimeStr = None
    try:
        parsedDate = datetime.strptime(dateStr, "%Y-%m-%d")
        parsedTime = datetime.strptime(timeStr, "%H:%M")
        datetimeStr = parsedDate.strftime("%Y-%m-%d") + " " + parsedTime.strftime("%H:%M:%S.%f")
    except Exception as e:
        print(e)

    return datetimeStr


if __name__ == "__main__":
    print(extractDateFromDB2DateTimeString("2022-03-02 08:00:00.000000"))
    print(extractTimeFromDB2DateTimeString("2022-02-02 08:00:00.000000"))
    print(convertDateAndTimeToDB2DateTime("15.04.2022", "12:15"))
