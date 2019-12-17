__author__ = 'sheraz/nibesh'

import re
import os
import random
from itertools import chain
from os.path import join, isdir
import webbrowser
from kivy.uix.popup import Popup, PopupException
from kivy.uix.label import Label
from .utils import normalize, escape_re_string

from include.widget_cls import TileButton


""" ____________________________________________________________________________________
                            PARSING FUNCTIONS AND VARIABLES  
"""

UNITS = {"cup": ["cups", "cup", "c.", "c"],
         "fluid_ounce": ["fl. oz.", "fl oz", "fluid ounce", "fluid ounces"],
         "gallon": ["gal", "gal.", "gallon", "gallons"],
         "ounce": ["oz", "oz.", "ounce", "ounces"],
         "pint": ["pt", "pt.", "pint", "pints"],
         "pound": ["lb", "lb.", "pound", "pounds", "lbs"],
         "quart": ["qt", "qt.", "qts", "qts.", "quart", "quarts"],
         "tablespoon": ["tbsp.", "tbsp", "T", "T.", "tablespoon", "tablespoons", "tbs.", "tbs", "Tbsp"],
         "teaspoon": ["tsp.", "tsp", "t", "t.", "teaspoon", "teaspoons", "Tsp"],
         "gram": ["g", "g.", "gr", "gr.", "gram", "grams"],
         "kilogram": ["kg", "kg.", "kilogram", "kilograms"],
         "liter": ["l", "l.", "liter", "liters"],
         "milligram": ["mg", "mg.", "milligram", "milligrams"],
         "milliliter": ["ml", "ml.", "milliliter", "milliliters"],
         "pinch": ["pinch", "pinches"],
         "dash": ["dash", "dashes"],
         "touch": ["touch", "touches"],
         "handful": ["handful", "handfuls"],
         "stick": ["stick", "sticks"],
         "clove": ["cloves", "clove"],
         "can": ["cans", "can"],
         "large": ["large"],
         "small": ["small"],
         "scoop": ["scoop", "scoops"],
         "filets": ["filet", "filets"],
         "sprig": ["sprigs", "sprig"],
         "rack": ["rack", "racks"]}

NUMBERS = ['seventeen', 'eighteen', 'thirteen', 'nineteen', 'fourteen', 'sixteen', 'fifteen', 'seventy', 'twelve',
           'eleven', 'eighty', 'thirty', 'ninety', 'twenty', 'seven', 'fifty', 'sixty', 'forty', 'three', 'eight',
           'four', 'zero', 'five', 'nine', 'ten', 'one', 'six', 'two', 'an', 'a', '½', '¼']

prepositions = ["of"]

a = list(chain.from_iterable(UNITS.values()))
a.sort(key=lambda x: len(x), reverse=True)
a = map(escape_re_string, a)

PARSER_RE = re.compile(
    r'(?P<quantity>(?:[\d\.,][\d\.,\s/]*)?\s*(?:(?:%s)\s*)*)?(\s*(?P<unit>%s)\s+)?(\s*(?:%s)\s+)?(\s*(?P<name>.+))?' % (
        '|'.join(NUMBERS), '|'.join(a), '|'.join(prepositions)))


def parse_ingredient(input_line):
    list_items = input_line.split('\n')
    amounts = ''
    ingredients = ''
    for item in list_items:
        data = parse(item)
        amounts += str(data['measure']) + '|'
        ingredients += str(data['name']) + '|'
    return amounts, ingredients


def parse(st):
    """
    :param st:
    :return:
    """
    st = normalize(st)
    res = PARSER_RE.match(st)

    return {
        'quantity':(res.group('quantity') or '').strip(),
        'unit':(res.group('unit') or '').strip(),
        'measure': (res.group('quantity') or '').strip() + ' ' + (res.group('unit') or '').strip(),
        'name': (res.group('name') or '').strip()
    }


""" ____________________________________________________________________________________
                                STATIC APPLICATION FUNCTIONS
"""


# _________________ GENERIC WARNING POPUP ___________________________________
def open_popup(pop_title='Warning', pop_text=''):
    popup = Popup(title=pop_title,
                  content=Label(text=pop_text),
                  size_hint=(None, None), size=(300, 100))
    popup.open()


def is_dir(directory, filename):
    return isdir(join(directory, filename))


def open_link(*args):
    link = args[0][1].strip('<').strip('>')
    webbrowser.open(link)


def create_menu_item(name, scroll_menu, _id=999999, rating=0):
    """ RECEIVES 'name' FROM 'update_tile_menu' TO POPULATE MAIN MENU SCREEN """
    button_title = str(name)
    recipe_button = TileButton()
    rate_img = 'images/bin/_icons/%s_star.png' % str(rating)
    # recipe_button.bind(on_release=lambda x: self.display_recipe(button_title))  # DISPLAYS RECIPE
    thumbnail = 'images/bin/_thumbnails/thumb-%s.jpg' % _id
    if os.path.isfile(thumbnail):
        recipe_button.ids.tile_box.source = thumbnail
    else:
        random_num = random.randint(1, 10)
        recipe_button.ids.tile_box.source = 'images/bin/_icons/food-%s.png' % random_num
    recipe_button.ids.btn_title.text = button_title
    scroll_menu.add_widget(recipe_button)
    recipe_button.ids.rating_img.source = rate_img
