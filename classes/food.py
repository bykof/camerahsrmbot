

class Food(object):
    def __init__(self, day_of_week, day, food_type, food_description):
        self.day_of_week = day_of_week
        self.day = day
        self.food_type = food_type
        self.food_description = food_description

    def bot_representation(self):
        return u'{}\n{}'.format(
            self.food_type,
            self.food_description,
        )

    def __str__(self):
        return '{}'.format(self.food_description)
