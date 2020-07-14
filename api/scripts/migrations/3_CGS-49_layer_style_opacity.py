from os import environ
import re


def run_migration(app):

    sql = """ SELECT id, styleqml FROM public.layer_styles; """

    cur = app._db.execute_sql(sql)
    regex = r"(\d+,\d+,\d+,[\d+,.]+)"

    for row in cur.fetchall():
        qml = row[1]
        colors = re.findall(regex, qml)
        for color in colors:
            qml = qml.replace(color, convert_opacity(color))
        u_sql = """ UPDATE public.layer_styles SET styleqml = %s WHERE id = %s; """
        app._db.execute_sql(u_sql, (qml, row[0]))


def convert_opacity(color):
    splitted = color.split(',')
    if float(splitted[3]) <= 1:
        splitted[3] = str(int((float(splitted[3]) * 100 * 255) / 100))
    return ','.join(splitted)
