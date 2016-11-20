#coding=utf-8

import StringIO
import datetime
import time
import csv
from subprocess import check_output

import requests

from food import Food

class Menu(object):
    TABULA_LOCATION = 'tabula-0.9.1-jar-with-dependencies.jar'
    MENU_LINK = (
        'http://www.camera-zuspann.de/Speiseplan/SpeisenkarteCamera2013.pdf'
    )
    DAY_OF_WEEK_MAPPING = {
        0: u'Montag',
        1: u'Dienstag',
        2: u'Mittwoch',
        3: u'Donnerstag',
        4: u'Freitag',
        5: u'Samstag',
        6: u'Sonntag',
    }


    def __init__(self):
        self.foods = []
        self._init_foods()

    def _download_pdf(self):
        return requests.get(self.MENU_LINK)

    def _write_to_card_pdf(self, content):
        with open('card.pdf', 'a') as card_pdf:
            card_pdf.write(content)

    def _run_table_recognition(self):
        return check_output(
            [
                'java',
                '-Dapple.awt.UIElement=true',
                '-jar', self.TABULA_LOCATION,
                '-p', '1',
                '-a', '75.25375, 85.77875, 502.56875, 725.69875',
                '--spreadsheet',
                'card.pdf'
            ]
        )

    def _create_csv_reader(self, csv_data):
        csv_file = StringIO.StringIO()
        csv_file.write(csv_data.decode('iso-8859-1').encode('utf-8'))
        csv_file.seek(0)
        return csv.reader(csv_file, delimiter=',', quotechar='"')

    def _create_foods_of_row_with_food_type(
        self,
        row,
        food_type,
        food_information
    ):
        for temp_index, food in enumerate(row):
            self.create_and_append_food(
                day_of_week=food_information[temp_index]['day_of_week'],
                day=food_information[temp_index]['day'],
                food_type=food_type,
                food_description=food.replace('\r', ' ')
            )

    def create_and_append_food(
        self,
        day_of_week,
        day,
        food_type,
        food_description
    ):
        self.foods.append(
            Food(
                day_of_week=day_of_week,
                day=day,
                food_type=food_type,
                food_description=food_description,
            )
        )

    def _init_foods(self):
        food_information = {}
        response = self._download_pdf()
        self._write_to_card_pdf(response.content)
        table_data = self._run_table_recognition()
        csv_reader = self._create_csv_reader(table_data)

        for index, row in enumerate(csv_reader):
            row = [
                data.decode('utf-8')
                for data in row
                if data
            ]

            if index == 0:
                for temp_index, day_of_week in enumerate(row):
                    food_information[temp_index] = {'day_of_week': day_of_week}
            if index == 1:
                for temp_index, day in enumerate(row):
                    food_information[temp_index]['day'] = day
            if index == 2:
                self._create_foods_of_row_with_food_type(
                    row,
                    'Stammgericht',
                    food_information
                )
            if index in [3, 4, 5]:
                self._create_foods_of_row_with_food_type(
                    row,
                    'Gericht {}'.format(index - 2),
                    food_information
                )
            if index == 6:
                self._create_foods_of_row_with_food_type(
                    row,
                    'Pastabar',
                    food_information
                )

    def find_food(self, food_type='', day_of_week=''):
        found_food = self.foods[:]
        for food in self.foods:
            if food_type and food.food_type != food_type:
                found_food.remove(food)

            if day_of_week and food.day_of_week != day_of_week:
                found_food.remove(food)
        return found_food

    def foods_string(self, foods):
        return_string = u''
        for index, food in enumerate(foods):
            return_string += u'{}: {}\n'.format(
                food.food_type,
                food.food_description
            )
            if index + 1 != len(foods):
                return_string += '---------------\n'
        return return_string

    def todays_menu(self):
        return_string = u'Das Menü für heute ist:\n'
        return_string += '---------------\n'
        day_of_week = self.DAY_OF_WEEK_MAPPING[
            datetime.datetime.today().weekday()
        ]
        found_food = self.find_food(day_of_week=day_of_week)
        return_string += self.foods_string(found_food)
        return return_string

    def tommorows_menu(self):
        return_string = u'Das Menü für morgen ist:\n'
        return_string += '---------------\n'
        day_of_week = self.DAY_OF_WEEK_MAPPING[
            datetime.datetime.today().weekday() + 1
        ]
        found_food = self.find_food(day_of_week=day_of_week)
        return_string += self.foods_string(found_food)
        return return_string

    def weekly_menu(self):
        return_string = u'Das Menü für die Woche ist:\n'
        return_string += '---------------\n'
        return_string += self.foods_string(self.foods)
        return return_string
