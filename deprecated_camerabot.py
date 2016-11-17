import StringIO
import datetime
import time
import csv
from pytgbot import Bot
from subprocess import check_output
import requests

from passwords import TOKEN
from classes.food import Food

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

DAY_OF_WEEK_MAPPING = {
    0: u'Montag',
    1: u'Dienstag',
    2: u'Mittwoch',
    3: u'Donnerstag',
    4: u'Freitag',
    5: u'Samstag',
    6: u'Sonntag',
}

def find_food(food_type='', day_of_week=''):
    found_food = foods[:]
    for food in foods:
        if food_type and food.food_type != food_type:
            found_food.remove(food)

        if day_of_week and food.day_of_week != day_of_week:
            found_food.remove(food)
    return found_food

def handle(msg):
    """
    {
        u'date': 1479164735,
        u'text': u'hi',
        u'from': {
            u'username': u'bykof',
            u'first_name': u'Michael',
            u'last_name': u'B',
            u'id': 8930064
        },
        u'message_id': 19,
        u'chat': {
            u'username': u'bykof',
            u'first_name': u'Michael',
            u'last_name': u'B',
            u'type': u'private',
            u'id': 8930064
        }
    }
    """
    print(msg)
    day_of_week = DAY_OF_WEEK_MAPPING[datetime.datetime.today().weekday()]
    bot.sendMessage(
        msg['chat']['id'],
        u'Heute ({}) gibt es folgendes in der Camera: \n'.format(day_of_week)
    )
    bot.sendMessage(
        msg['chat']['id'],
        u'\n-------------------------\n'.join(
            [
                food.bot_representation() for food in find_food(
                    day_of_week=day_of_week
                )
            ]
        )
    )

bot = Bot(TOKEN)
while(True):
    time.sleep(1)
    for x in bot.get_updates():
        print x

foods = []
def initialize_food():
    global foods
    response = requests.get(
        'http://www.camera-zuspann.de/Speiseplan/SpeisenkarteCamera2013.pdf'
    )

    with open('card.pdf', 'a') as card_pdf:
        card_pdf.write(response.content)

    output = check_output(
        [
            'java',
            '-Dapple.awt.UIElement=true',
            '-jar', 'tabula-0.9.1-jar-with-dependencies.jar',
            '-p', '1',
            '-a', '75.25375, 85.77875, 502.56875, 725.69875',
            '--spreadsheet',
            'card.pdf'
        ]
    )

    csv_file = StringIO.StringIO()
    csv_file.write(output.decode('ISO-8859-1'))
    csv_file.seek(0)

    csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
    information = {}
    foods = []

    for index, row in enumerate(csv_reader):
        row = [unicode(data, 'utf-8') for data in row if data]

        if index == 0:
            for temp_index, day_of_week in enumerate(row):
                information[temp_index] = {'day_of_week': day_of_week}
        if index == 1:
            for temp_index, day in enumerate(row):
                information[temp_index]['day'] = day
        if index == 2:
            food_type = 'Stammgericht'
            for temp_index, food in enumerate(row):
                foods.append(
                    Food(
                        day_of_week=information[temp_index]['day_of_week'],
                        day=information[temp_index]['day'],
                        food_type=food_type,
                        food_description=food.replace('\r', ' ')
                    )
                )
        if index in [3, 4, 5]:
            for temp_index, food in enumerate(row):
                foods.append(
                    Food(
                        day_of_week=information[temp_index]['day_of_week'],
                        day=information[temp_index]['day'],
                        food_type='Gericht {}'.format(index - 2),
                        food_description=food.replace('\r', ' ')
                    )
                )
        if index == 6:
            for temp_index, food in enumerate(row):
                foods.append(
                    Food(
                        day_of_week=information[temp_index]['day_of_week'],
                        day=information[temp_index]['day'],
                        food_type='Pastabar',
                        food_description=food
                    )
                )
    print('Food initialized...')
    print('Foods: {}'.format(len(foods)))

initialize_food()

# Keep the program running.
while 1:
    last_day = datetime.datetime.now().day

    time.sleep(10)
    if last_day != datetime.datetime.now().day:
        initialize_food()
