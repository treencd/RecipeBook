# KIVY IMPORTS
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, \
    ListProperty, BooleanProperty, DictProperty, BoundedNumericProperty
from kivy.uix.settings import SettingsWithSidebar
from kivy.uix.label import Label
from kivy.graphics import Color, Mesh, InstructionGroup, Rectangle
from kivy.uix.widget import Widget
from kivy.uix.image import Image as KvImage
from kivy.clock import Clock
# KIVYMD IMPORTS
from kivymd.uix.chip import MDChip
from kivymd.uix.button import MDRectangleFlatButton, MDIconButton, MDRectangleFlatIconButton
from kivymd.theming import ThemeManager
from kivymd.uix.navigationdrawer import NavigationDrawerIconButton
from kivymd.toast import toast
from kivymd.uix.picker import MDThemePicker
from kivymd.uix.textfield import MDTextFieldRound
# OTHER IMPORTS
import os
import re
from PIL import Image
import csv
import json
import random
from collections import deque
# PERSONAL IMPORTS
from include.sqlactions import create_connection, create_table
from include.static_fun import *
from include.widget_cls import *


class MyRecipeBookApp(App):
    # APPLICATION PROPERTIES
    md_theme_picker = ObjectProperty()
    menu_tile_width = NumericProperty(0)
    menu_tile_height = BoundedNumericProperty(210, min=160, max=210,
                                              errorhandler=lambda x: 210 if x > 210 else 160)
    menu_col_num = NumericProperty(4)
    toolbar_title = StringProperty('My Recipe Book')
    child_list = ListProperty([])
    recipe_image = StringProperty('')
    search_focus = BooleanProperty(False)
    # DISPLAY RECIPE PROPERTIES:
    recipe_id = StringProperty('')
    title_display = StringProperty('')
    desc_display = StringProperty('')
    edit_desc_display = StringProperty('')
    tag_display = ListProperty([])
    time_prep_display = StringProperty('')
    time_cook_display = StringProperty('')
    ingredient_display = StringProperty('')
    amt_display = StringProperty('')
    instruction_display = StringProperty('')
    rating_display = NumericProperty(0)
    btn1_pos = ObjectProperty()
    btn2_pos = ObjectProperty()
    return_btn_pos = ObjectProperty()
    accept_btn_pos = ObjectProperty()
    new_rec_btn_pos = ObjectProperty()

    data_height = ObjectProperty(20)
    block_height = ObjectProperty(25)
    headers = ObjectProperty(0)
    ingredient_list = DictProperty({})

    # EDIT RECIPE PROPERTIES
    single_ingred = StringProperty('')
    single_amt = StringProperty('')
    float_crop_pos = ObjectProperty((150, 460))
    float_cancel_pos = ObjectProperty((180, 460))
    float_edit_img_pos = ObjectProperty((120, 460))
    ingredient_groups = DictProperty({})
    ingredients_for_edit = []
    unit_for_edit = []
    group_1_title = StringProperty('')
    group_1_text = StringProperty('')
    # NEW RECIPE PROPERTIES
    recipe_count = 0
    ingredient_block = ''
    # THEME CLASS
    theme_cls = ThemeManager()
    theme_cls.primary_palette = 'Teal'  # ['Red', 'Pink', 'Purple', 'DeepPurple', 'Indigo', 'Blue', 'LightBlue',
    # 'Cyan', 'Teal', 'Green', 'LightGreen', 'Lime', 'Yellow', 'Amber', 'Orange', 'DeepOrange', 'Brown',
    # 'Gray', 'BlueGray']
    theme_cls.accent_palette = 'Cyan'
    theme_cls.theme_style = 'Dark'
    main_widget = None
    filter_items = []
    # CROP TOOL PROPERTIES
    down_pos = ListProperty([])
    new_height = 485
    reset_base_height = 540
    x, y = (150.0, 485.0)
    im_x, im_y = (500, 375)
    image_x = ObjectProperty(500)
    image_y = ObjectProperty(375)
    max_x, max_y = (x + im_x), (y + im_y)
    border = 30
    stencil_pos = ListProperty([x, y])
    select_start_x = BoundedNumericProperty(x + border, min=x, max=(x + im_x),
                                            errorhandler=lambda x, max_x: max_x if x > max_x else x)
    select_start_y = BoundedNumericProperty(y + border, min=y, max=(y + im_y),
                                            errorhandler=lambda y, max_y: max_y if y > max_y else y)
    select_end_x = BoundedNumericProperty((x + im_x - border), min=x, max=(x + im_x),
                                          errorhandler=lambda x, max_x: max_x if x > max_x else x)
    select_end_y = BoundedNumericProperty((y + im_y - border), min=y, max=(y + im_y),
                                          errorhandler=lambda y, max_y: max_y if y > max_y else y)
    button_click = False
    currently_clicked = ''
    corner = [0, 0, 0, 0]
    crop_buttons = [0, 0, 0, 0]
    position = (0, 0)
    canvas_size = (0, 0)
    mesh0 = ObjectProperty(None)
    mesh1 = ObjectProperty(None)
    mesh2 = ObjectProperty(None)
    mesh3 = ObjectProperty(None)
    vertex_0 = ListProperty([])
    vertex_1 = ListProperty([])
    vertex_2 = ListProperty([])
    vertex_3 = ListProperty([])
    btn_1_pos = (0, 0)
    btn_2_pos = (0, 0)
    btn_3_pos = (0, 0)
    btn_4_pos = (0, 0)
    dynamic_ids = DictProperty({})
    objects = []
    # FILE-CHOOSER
    file_selection = StringProperty('')
    image_pattern = r"([a-z A-Z 0-9 \s_\/.\-\'\"\(/):])+(.png|.img|.jpg|.JPG|.PNG|.IMG)$"
    root_path = StringProperty('/home/craig')
    file_location = StringProperty('')
    # SCREENS
    screen_ids = DictProperty({})
    first_run = True
    settings_menu = object
    pop_tag = object
    drop_down = object
    pop_win = object
    file_menu = object
    # DELETE RECIPE PROPERTIES
    highest_id = 0
    orphan_id_list = deque()
    delete_recipe = BooleanProperty(False)
    # SEARCH
    set_filter = 'name'
    filter_order = 'ASC'  # OR 'DESC'
    #  _______________________________ END OF PROPERTIES _______________________________

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # LOAD USER CREATED TAG LIST
        self.tag_file = 'include/tag_list.csv'
        with open(self.tag_file) as File:
            lis = [line.strip('\n').split(',') for line in File]
            self.tag_list = lis[0]

    def build(self):
        # MAY NOT BE NECESSARY IF THE APP IS IN FULL-SCREEN MODE, NEEDS LOGIC OTHERWISE
        # Window.size = 800, 480
        # WINDOW RESIZING WILL RUN THESE FUNCTIONS:
        Window.bind(on_resize=self.update_tile_width)
        Window.bind(on_resize=self.update_label)
        Window.bind(on_resize=self.update_cropper)
        Window.bind(on_keyboard=self._on_keyboard)
        # FULL-SCREEN OPTION:
        # Window.fullscreen = False
        # POSITION FLOATING BUTTONS BASED ON WINDOW SIZE
        self.return_btn_pos = (20, Window.height - 130)
        self.accept_btn_pos = (Window.width - 75, Window.height - 130)
        self.new_rec_btn_pos = (Window.width - 75, 20)
        self.btn1_pos = (20, Window.height - 130)
        self.btn2_pos = (Window.width - 75, Window.height - 130)
        # LOAD FILTER_MENU JSON FILE
        with open('include/filter_menu.json') as json_file:
            self.filter_items = json.load(json_file)
            for filt in self.filter_items:
                filt["callback"] = self.filter_tile_menu
        self.settings_cls = SettingsWithSidebar
        # LOAD ORPHAN ID LIST FILE
        with open('include/orphanids.txt', 'r') as listfile:
            for line in listfile:
                current_place = line[:-1]  # remove linebreak which is the last character of the string
                self.orphan_id_list.extend(current_place)  # add item to the list
        # LOAD KV FILES
        Builder.load_file('include/widgets.kv')
        Builder.load_file('include/display_screen.kv')
        Builder.load_file('include/edit_screen.kv')
        Builder.load_file('include/new_screen.kv')
        self.main_widget = Builder.load_file('main_kv.kv')
        # ADD ALL SCREENS TO THE MANAGER AND ASSIGNED TO THE DictProperty: 'screen_ids'
        idents = ['edit_screen', 'display_screen', 'new_screen']
        self.screen_ids[idents[0]] = EditScreen(id='edit_screen', name='edit_screen')
        self.screen_ids[idents[1]] = DisplayScreen(id='display_screen', name='display_screen')
        self.screen_ids[idents[2]] = NewScreen(id='new_screen', name='new_screen')
        self.main_widget.ids.screen_manager.add_widget(self.screen_ids[idents[0]])
        self.main_widget.ids.screen_manager.add_widget(self.screen_ids[idents[1]])
        self.main_widget.ids.screen_manager.add_widget(self.screen_ids[idents[2]])
        # POPUP/FILE MENUS
        self.settings_menu = SettingsMenu()
        self.pop_tag = TagPopup()
        self.drop_down = CheckboxDropDown()
        self.file_menu = FileMenuDropDown()
        self.pop_win = FilePopup()
        return self.main_widget

    def build_config(self, config):
        # CUSTOM SETTINGS MENU
        config.setdefaults('example', {
            'boolexample': True,
            'numericexample': 10,
            'optionsexample': 'option2',
            'stringexample': 'some_string',
            'pathexample': '/some/path'})

    def build_settings(self, settings):
        """ SETTING PANEL OPTIONS ARE LOCATED IN THIS FILE: """
        settings.add_json_panel('Panel Name', self.config, filename="include/app_settings.json")

    def update_settings(self):
        # Need to figure out how to trigger this
        toast("Applying Settings", 3)
        bool_setting = self.config.get('example', 'boolexample')
        print(bool_setting)

    def on_start(self):
        """ RUNS ON APP STARTUP"""
        # This adjust the recipe tiles to the correct starting width:
        self.update_tile_width()
        # This searches the database in order to find all recipes and generate Tiles:
        self.update_tile_menu()
        toast('Welcome!', 3)

    def _on_keyboard(self, instance, key, scancode, codepoint, modifiers, *args):
        """ RUNS ON EVERY KEYPRESS (KEEP IT SHORT)"""
        # print("Keyboard pressed! {}, {}, {}, {}".format(key, scancode, codepoint, modifiers))
        if codepoint == 's' and 'ctrl' in modifiers:
            toast('Search by Name, Ingredient, or Tag', 3)
            self.search_focus = True

    def theme_picker_open(self):
        """OPENS THE KIVYMD THEME-PICKER WIDGET"""
        if not self.md_theme_picker:
            self.md_theme_picker = MDThemePicker()
        self.md_theme_picker.open()

    def filter_tile_menu(self, set_filter):
        if set_filter == 'All':
            self.set_filter = 'name'
            self.filter_order = 'ASC'
            self.update_tile_menu()
        if set_filter == 'Favourites':
            self.set_filter = 'rating'
            self.filter_order = 'DESC'
            self.update_tile_menu()
        if set_filter == 'Quickest':
            self.set_filter = 'prep_time, cook_time'
            self.filter_order = 'ASC'
            self.update_tile_menu()

    def update_tile_menu(self, search=' ', *args):
        if search != ' ':
            toast(search, 3)
        regex_query = '%' + str(search) + '%'
        conn = create_connection()
        if conn is not None:
            create_table(conn)
            cur = conn.cursor()
            self.root.ids.main_scroll_menu.clear_widgets()
            search_cols = ['name', 'Ingredients', 'Tags']
            self.child_list = []
            for item in search_cols:
                cur.execute("SELECT * FROM recipes WHERE {cn} LIKE '{en}' ORDER BY {fi} {order}".format(
                    cn=item, en=regex_query, fi=self.set_filter, order=self.filter_order))
                rows = cur.fetchall()
                for row in rows:
                    child_id = str(row[0])
                    if int(row[0]) > self.highest_id:
                        self.highest_id = int(child_id)
                    rating = int(row[9])
                    if child_id not in self.child_list:
                        if item == 'name':
                            button_label = '[b]' + str(row[1]) + '[/b]'
                        else:
                            button_label = \
                                '[b]' + str(row[1]) + '\n[color=63116b]' + item + ': ' + str(search) + '[/color][/b]'
                        self.child_list.append(child_id)
                        create_menu_item(button_label, self.root.ids.main_scroll_menu, int(child_id), rating)
            self.recipe_count = len(self.child_list)
            conn.commit()
            conn.close()
            if len(self.child_list) == 0:
                toast('No Results', 4)
        else:
            open_popup('Warning', 'Error! cannot create the database connection.')  # ______

    def update_tile_width(self, *args):
        self.return_btn_pos = (10, Window.height - 130)
        self.accept_btn_pos = (Window.width - 75, Window.height - 130)
        self.new_rec_btn_pos = (Window.width - 75, 20)
        self.btn1_pos = (10, Window.height - 130)
        self.btn2_pos = (Window.width - 75, Window.height - 130)
        if Window.width < 580:
            self.menu_col_num = 3
            if Window.width < 415:
                self.menu_col_num = 2
                if Window.width < 280:
                    self.menu_col_num = 1
        else:
            self.menu_col_num = 4
        self.menu_tile_width = (Window.width - (self.menu_col_num + 1) * 5) / self.menu_col_num
        self.menu_tile_height = Window.height / 2.3

    def update_cropper(self, *args):
        if Window.width >= 800:
            self.reset_cropper_height(6)
        elif Window.width < 800:
            self.reset_cropper_height(8)

    def clear_display(self):
        cur_screen = self.root.ids.screen_manager.current
        self.recipe_id = '0'
        self.title_display = ''
        self.desc_display = ''
        self.edit_desc_display = ''
        self.tag_display = []
        self.time_prep_display = ''
        self.time_cook_display = ''
        self.amt_display = ''
        self.ingredient_display = ''
        self.ingredient_block = ''
        self.instruction_display = ''
        self.recipe_image = ''
        for item in self.ingredient_list.items():
            self.screen_ids['display_screen'].ids.table_data.remove_widget(self.ingredient_list[item[0]])
        self.ingredient_list = {}

    def delete_recipe(self, *args):
        # OPEN CONFIRMATION POPUP
        conformation_dialogue = ConfirmDeletePopup(recipe_id=self.recipe_id)
        conformation_dialogue.open()

    def display_recipe(self, name, *args):  # DISPLAY RECIPE ____________________________________________
        self.clear_display()
        if name != '':
            toast((name.strip('[b]').strip('[/b]')), 3)
        conn = create_connection()
        if conn is not None:
            self.root.ids.screen_manager.current = 'display_screen'
            cur = conn.cursor()
            name_strip = name.strip('[b]').strip('[/b]').split('\n')  # Buttons name can have a newline for category based searches
            cur.execute("SELECT * FROM recipes WHERE name LIKE ?", (name_strip[0],))
            row = cur.fetchone()
            self.recipe_id = str(row[0])  # ______________________  RECIPE ID ________________________
            self.title_display = str(row[1])  # __________________  RECIPE TITLE _____________________
            if row[2] is not None and not row[2] == '':  # _______  RECIPE DESCRIPTION _______________
                self.desc_display = row[2]
                url = re.match("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
                               str(self.desc_display))
                if url:
                    self.desc_display = '[ref=<' + str(row[2] + '>]Website[/ref]')
                self.edit_desc_display = row[2]
            self.screen_ids['display_screen'].ids.view_tag_container.clear_widgets()  # ________  RECIPE TAGS ________
            if row[3] is not None and not row[3] == '':
                self.tag_display = str(row[3]).split(',')
                for item in self.tag_display:
                    if not item == '':
                        self.add_tags(item)
            self.time_prep_display = str(row[4])  # ______________  RECIPE PREP TIME___________________
            self.time_cook_display = str(row[5])  # ______________  RECIPE COOK TIME___________________
            _ingredient_list = row[6].split('$')  # _____________ INGREDIENTS/AMOUNTS ________________
            _units_list = row[7].split('$')
            self.ingredients_for_edit = _ingredient_list
            self.unit_for_edit = _units_list
            self.data_height = 0
            index = 0
            self.headers = 0
            for i in range(len(_ingredient_list)):
                if (i % 2) == 0 and _ingredient_list[i] != '':  # HEADER
                    title = '[b] %s [/b]' % _ingredient_list[i]
                    header = HeaderLabel(label_text=title, label_markup=True)
                    self.screen_ids['display_screen'].ids.table_data.add_widget(header)
                    self.headers += 1
                else:
                    _ingredients = _ingredient_list[i].split('|')
                    _units = _units_list[int((i - 1) / 2)].split('|')
                    height = 0
                    for ind in range(len(_ingredients[:-1])):
                        self.ingredient_list[str(index)] = IngredientBlock()
                        self.ingredient_list[str(index)].ids.label_i.text = _ingredients[ind]
                        self.ingredient_list[str(index)].ids.label_u.text = _units[ind]
                        height += self.ingredient_list[str(index)].height
                        self.screen_ids['display_screen'].ids.table_data.add_widget(self.ingredient_list[str(index)])
                        self.ingredient_list[str(index)].height = \
                            self.ingredient_list[str(index)].ids.label_i.texture_size[1]
                        index += 1
            Clock.schedule_once(self.update_label, .1)
            self.instruction_display = row[8]  # __________ INSTRUCTION DISPLAY __________
            if row[9]:                              # __________ RATING DISPLAY __________
                self.rating_display = int(row[9])
            else:
                self.rating_display = 0
            self.change_star(self.rating_display)
            _image_blob = row[11]
            if _image_blob:
                cwd = os.getcwd()
                try:
                    photo_path = cwd + "/images/bin/" + self.title_display + ".jpg"
                    with open(photo_path, 'wb') as file:
                        file.write(_image_blob)
                    self.recipe_image = str(photo_path)
                except Exception as e:
                    open_popup('ERROR!', str(e))
            else:
                random_num = random.randint(1, 10)
                self.recipe_image = '/images/bin/_icons/food-%s.png' % random_num
        else:
            open_popup('ERROR!', 'cannot create the database connection.')  # ____________

    def update_label(self, *args):
        self.data_height = 0
        self.data_height += self.headers * 60
        for i in range(len(self.ingredient_list)):
            self.ingredient_list[str(i)].height = self.ingredient_list[str(i)].ids.label_i.texture_size[1] + 4
            self.data_height += self.ingredient_list[str(i)].ids.label_i.texture_size[1] + 4

    def change_star(self, rating, *args):
        self.screen_ids['display_screen'].ids.rating_box.clear_widgets()
        self.rating_display = rating
        self.screen_ids['display_screen'].ids.rating_box.add_widget(Widget())
        for i in range(rating):
            star = MDIconButton(icon='star', pos_hint={'center_x': 0.5})
            star.bind(on_release=lambda x: self.change_star(self.rating_display - 1))
            self.screen_ids['display_screen'].ids.rating_box.add_widget(star)
        ind = self.rating_display
        if ind < 0:
            ind = 0
        elif ind > 5:
            ind = 5
        while ind < 5:
            outline_star = MDIconButton(icon='star-outline', pos_hint={'center_x': 0.5})
            outline_star.bind(on_release=lambda x: self.change_star(self.rating_display + 1))
            self.screen_ids['display_screen'].ids.rating_box.add_widget(outline_star)
            ind += 1
        self.screen_ids['display_screen'].ids.rating_box.add_widget(Widget())

    def clear_widgets(self, screen):
        index = 0
        if len(screen.ids.ingredient_panel.tab_list) > 0:
            for item in self.ingredient_groups.items():
                screen.ids.ingredient_panel.remove_widget(self.ingredient_groups[item[0]])
                index += 1
            self.ingredient_groups = {}

    def edit_display(self):
        # __________________ DISPLAY TAGS
        if len(self.screen_ids['edit_screen'].ids.edit_tag_container.children) > 0:
            self.screen_ids['edit_screen'].ids.edit_tag_container.clear_widgets()
        for item in self.tag_display:
            if not item == '':
                self.add_tags(item)
        # __________________ DISPLAY INGREDIENTS
        '''THIS IS ALWAYS AN EVEN NUMBER 'IngredientGroupTitle$IngredientGroup$...' '''
        blocks = len(self.ingredients_for_edit)
        for i in range(int((blocks / 2) - 1)):  # Add panels minus the one to start
            self.ingredient_groups[str(i)] = IngredientGroup()
            self.screen_ids['edit_screen'].ids.ingredient_panel.add_widget(self.ingredient_groups[str(i)])
        _ingredients = ''
        index = 0
        for i in range(int(blocks)):
            if (index % 2) == 0:  # ITS A TITLE
                if index == 0:
                    self.group_1_title = str(self.ingredients_for_edit[0])
                else:
                    self.ingredient_groups[str(int((i - 2)/2))].ids.ingred_title.text = str(self.ingredients_for_edit[index])
            else:       # ITS A TEXT BLOCK OF INGREDIENTS
                if index == 1:
                    ingredient_list = self.ingredients_for_edit[1].split('|')
                    units = self.unit_for_edit[0].split('|')
                    for x in range(len(ingredient_list) - 1):
                        if x != len(ingredient_list) - 1:
                            _ingredients += units[x] + ' ' + ingredient_list[x] + '\n'
                        else:
                            _ingredients += units[x] + ' ' + ingredient_list[x]
                    self.group_1_text = _ingredients.rstrip('\n')
                else:
                    _ingredients = ''
                    ingredient_list = self.ingredients_for_edit[index].split('|')
                    units = self.unit_for_edit[int((index - 1) / 2)].split('|')
                    for x in range(len(ingredient_list) - 1):
                        if x != len(ingredient_list) - 1:
                            _ingredients += units[x] + ' ' + ingredient_list[x] + '\n'
                        else:
                            _ingredients += units[x] + ' ' + ingredient_list[x]
                    self.ingredient_groups[str(int((i - 3) / 2))].ids.edit_ingredients_input.text = _ingredients.rstrip('\n')
            index += 1
        # HOW MANY LINES WERE ADDED
        self.reset_cropper_height()

    def update_db(self):  # ____ UPDATE EDITED RECIPE IN DB _______________________________________
        current_screen = self.root.ids.screen_manager.current
        if len(self.screen_ids[current_screen].ids.edit_recipe_title_input.text) > 40:
            open_popup('Warning', 'Recipe title too long')
        else:
            conn = create_connection()
            if conn is not None:
                print('UPDATING DATABASE')
                cur = conn.cursor()
                _ingred = ''
                _amts = ''
                if current_screen == 'edit_screen':
                    _id = int(self.recipe_id)
                    _rating = int(self.rating_display)
                    list_ing = [self.group_1_title, self.group_1_text]
                    for i in range(len(self.ingredient_groups)):
                        list_ing.append(self.ingredient_groups[str(i)].ids.ingred_title.text)
                        list_ing.append(self.ingredient_groups[str(i)].ids.edit_ingredients_input.text)
                    index = 0
                    for item in list_ing:
                        if (index % 2) != 0:
                            amounts, ingredients = parse_ingredient(item)
                            if index != len(list_ing) - 1:
                                _amts += amounts + '$'
                            else:
                                _amts += amounts
                            _ingred += ingredients
                        else:
                            if index == 0:
                                _ingred += item + '$'
                            else:
                                _ingred += '$' + item + '$'
                        index += 1
                else:
                    if len(self.orphan_id_list) > 0:
                        _id = self.orphan_id_list.popleft()
                        with open('/include/orphanids.txt', 'w') as filehandle:
                            for listitem in self.orphan_id_list:
                                filehandle.write('%s\n' % listitem)
                    else:
                        _id = self.highest_id + 1
                    _rating = 0
                    self.ingredient_block += self.screen_ids[current_screen].ids.ingredient_panel.children[0].children[0].children[1].children[2].text + "$"
                    self.ingredient_block += self.screen_ids[current_screen].ids.ingredient_panel.children[0].children[0].children[0].text
                    list_ing = self.ingredient_block.split('$')
                    index = 0
                    for item in list_ing:
                        if (index % 2) != 0:
                            amounts, ingredients = parse_ingredient(item)
                            if index != len(list_ing) - 1:
                                _amts += amounts + '$'
                            else:
                                _amts += amounts
                            _ingred += ingredients
                        else:
                            if index == 0:
                                _ingred += item + "$"
                            else:
                                _ingred += "$" + item + "$"
                        index += 1
                _title = str(self.screen_ids[current_screen].ids.edit_recipe_title_input.text)
                _description = str(self.screen_ids[current_screen].ids.edit_recipe_desc.text)
                _tags = ''
                for child in self.screen_ids[current_screen].ids.edit_tag_container.children:
                    _tags += str(child.label) + ','
                _preptime = str(self.screen_ids[current_screen].ids.edit_prep_time.text)
                _cooktime = str(self.screen_ids[current_screen].ids.edit_cook_time.text)
                _instructions = str(self.screen_ids[current_screen].ids.edit_instructions_input.text)
                match = re.match('images/bin/_icons/food', self.recipe_image)
                blob_data = ''
                if self.recipe_image != '' and not match:
                    basewidth = 200
                    img = Image.open(self.recipe_image)
                    wpercent = (basewidth / float(img.size[0]))
                    hsize = int((float(img.size[1]) * float(wpercent)))
                    img = img.resize((basewidth, hsize), Image.ANTIALIAS)
                    img.save("images/bin/_thumbnails/thumb-%s.jpg" % _id)
                    with open(self.recipe_image, 'rb') as file:
                        blob_data = file.read()
                    self.file_location = ''
                if current_screen == 'edit_screen':
                    cur.execute("UPDATE recipes SET name = ? where id = ?", (_title, _id,))
                    cur.execute("UPDATE recipes SET description = ? where id = ?", (_description, _id,))
                    cur.execute("UPDATE recipes SET tags = ? where id = ?", (_tags, _id,))
                    cur.execute("UPDATE recipes SET prep_time = ? where id = ?", (_preptime, _id,))
                    cur.execute("UPDATE recipes SET cook_time = ? where id = ?", (_cooktime, _id,))
                    cur.execute("UPDATE recipes SET ingredients = ? where id = ?", (_ingred, _id,))
                    cur.execute("UPDATE recipes SET amounts = ? where id = ?", (_amts, _id,))
                    cur.execute("UPDATE recipes SET instructions = ? where id = ?", (_instructions, _id,))
                    cur.execute("UPDATE recipes SET rating = ? where id = ?", (_rating, _id,))
                    cur.execute("UPDATE recipes SET image = ? where id = ?", (blob_data, _id,))
                else:
                    new_recipe = [_id, _title, _description, _tags, _preptime, _cooktime, _ingred, _amts,
                                  _instructions, _rating, blob_data]
                    regex = '%' + new_recipe[1] + '%'
                    cur = conn.cursor()
                    cur.execute("SELECT * FROM recipes WHERE name LIKE ?", (regex,))
                    rows = cur.fetchall()
                    if len(rows) == 0:
                        cur.execute(
                            "INSERT INTO recipes (id, name,description,tags,prep_time,cook_time,"
                            "ingredients,amounts,instructions,rating,image) VALUES(?,?,?,?,?,?,?,?,?,?,?);", new_recipe)
                    else:
                        open_popup('Warning', 'Recipe with this name already exists')
                conn.commit()
                conn.close()
                # self.update_menu()
                self.clear_widgets(self.screen_ids[current_screen])
            self.root.ids.screen_manager.current = 'display_screen'  # ______________________________

    def remove_ingredient_group(self, *args):
        index = str(len(self.ingredient_groups)-1)
        cur_screen = self.root.ids.screen_manager.current
        if not int(index) < 0:
            self.screen_ids[cur_screen].ids.ingredient_panel.remove_widget(self.ingredient_groups[index])
            del self.ingredient_groups[index]
        else:
            self.screen_ids[cur_screen].ids.ingred_title.text = ''
            self.screen_ids[cur_screen].ids.edit_ingredients_input.text = ''

    def add_ingredient_group(self, *args):
        cur_screen = self.root.ids.screen_manager.current
        index = str(len(self.ingredient_groups))
        self.ingredient_block += \
            self.screen_ids[cur_screen].ids.ingredient_panel.children[0].children[0].children[1].children[2].text + "$"
        self.ingredient_block += self.screen_ids[cur_screen].ids.ingredient_panel.children[0].children[0].children[0].text + "$"
        self.ingredient_groups[index] = IngredientGroup()
        self.screen_ids[cur_screen].ids.ingredient_panel.add_widget(self.ingredient_groups[index])

    def open_filechooser(self):  # __ FILE CHOOSER POPUP METHODS _________________________________
        self.pop_win.path = self.root_path
        self.pop_win.ids.file_chooser._update_files()
        self.pop_win.open(self)

    def submit_file_selection(self, *args):
        try:
            self.file_location = str(self.pop_win.ids.file_chooser.selection[0])
        except IndexError as ind:
            print(ind)
            open_popup("Error", str(ind))
        else:
            img_check = re.match(self.image_pattern, self.file_location)
            if img_check:
                cur_screen = self.root.ids.screen_manager.current
                self.screen_ids[cur_screen].ids.file_selection_edit.text = self.file_location
                self.recipe_image = self.file_location
            else:
                open_popup('Warning', 'Please select a valid image file')
            self.pop_win.dismiss()  # ______________________________________________________________

    def refresh_tag_dd(self):  # ____ ADD/REM TAG POPUP METHODS ________________________________
        self.drop_down.clear_widgets()
        for item in self.tag_list:
            btn = TagMDRectangleFlatIconButton(text=item, size_hint_y=None, height=25, icon='tag')
            btn.bind(on_release=lambda x: self.drop_down.dismiss())
            btn.md_bg_color = (.2, .2, .2, 1)
            self.drop_down.add_widget(btn)
        add_tag_btn = TagMDRectangleFlatIconButton(text='Add/Rem', size_hint_y=None, height=25, icon='plus')
        add_tag_btn.md_bg_color = (.2, .2, .2, 1)
        add_tag_btn.bind(on_release=lambda x: self.drop_down.dismiss())
        add_tag_btn.bind(on_release=lambda x: self.pop_tag.open(self))
        add_tag_btn.bind(on_release=lambda x: self.pop_tag.populate_tag_win(self.tag_list))
        self.drop_down.add_widget(add_tag_btn)

    def add_tags(self, tag):
        cur_screen = self.root.ids.screen_manager.current
        if cur_screen == 'display_screen':
            tag_label = MDChip(label=str(tag), color=(.9215686274509803, 0, 0, 1), icon='check')
            self.screen_ids['display_screen'].ids.view_tag_container.add_widget(tag_label)
        else:  # self.root.ids.screen_manager.current == 'edit_screen':
            tag_label = MDChip(label=str(tag), color=(.9215686274509803, 0, 0, 1), icon='close',
                               height=self.screen_ids[cur_screen].ids.edit_tag_container.height/2)
            tag_label.callback = self.remove_tag
            self.screen_ids[cur_screen].ids.edit_tag_container.add_widget(tag_label)

    def remove_tag(self, *args):
        cur_screen = self.root.ids.screen_manager.current
        for item in self.screen_ids[cur_screen].ids.edit_tag_container.children:
            if item.label == str(args[0]):
                self.screen_ids[cur_screen].ids.edit_tag_container.remove_widget(item)
        return True

    def update_tag_list(self, *args):
        self.tag_list = []
        for child in self.pop_tag.ids.add_rem_tag_container.children:
            self.tag_list.append(child.text)
        with open(self.tag_file, 'w') as File:
            writer = csv.writer(File)
            writer.writerow(self.tag_list)
        self.pop_tag.tag_dismiss()  # ____________________

    def reset_cropper_height(self, index=6, *args):  # _____________________ IMAGE CROPPER TOOL ______________________
        cropper_height = 485
        self.new_height = cropper_height + index * 50
        # (self.x, self.y) = BOTTOM LEFT CORNER OF THE CROPPING TOOL
        self.x, self.y = (0.1875 * Window.width, self.new_height)
        self.stencil_pos = self.x, self.y
        # CROPPING TOOL BUTTONS ARE PLACED UNDER CANVAS IF SCREEN IS NARROWER THAN dp(800)
        if Window.width >= 800:
            self.float_crop_pos = (Window.width * 0.8375, self.new_height + 45)   # CROP IMAGE BUTTON
            self.float_cancel_pos = (Window.width * 0.8375, self.new_height)      # RESET CROPPING MESH BUTTON
            self.float_edit_img_pos = (70, self.new_height + 20)                  # PLACE CROPPING MESH BUTTON
        else:
            self.float_crop_pos = (Window.width * 0.73, self.new_height - 60)      # CROP IMAGE BUTTON
            self.float_cancel_pos = (Window.width * 0.73, self.new_height - 105)  # RESET CROPPING MESH BUTTON
            self.float_edit_img_pos = (70, self.new_height - 85)                  # PLACE CROPPING MESH BUTTON
        # THE WIDTH OF THE IMAGE
        new_width = .625 * Window.width
        '''THE 'image_' VARIABLES ARE THE 'ObjectProperty' USED BY THE IMAGE AND CANVAS '''
        self.im_x, self.im_y = (new_width, ((3 / 4) * new_width))
        '''THE 'im_' VARIABLES ARE TO SET THE BOUNDING PROPERTIES OF THE FOUR 
        'BoundedNumericProperty' USED TO CONSTRAIN THE CROPPING BUTTONS AND MESH'''
        self.image_x = self.im_x
        self.image_y = self.im_y
        self.max_x, self.max_y = (self.x + self.im_x, self.y + self.im_y)
        self.property('select_start_x').set_min(self, self.x)
        self.property('select_start_x').set_max(self, self.max_x)
        self.select_start_x = self.x + self.border
        self.property('select_start_y').set_min(self, self.y)
        self.property('select_start_y').set_max(self, self.max_y)
        self.select_start_y = self.y + self.border
        self.property('select_end_x').set_min(self, self.x)
        self.property('select_end_x').set_max(self, self.max_x)
        self.select_end_x = self.max_x - self.border
        self.property('select_end_y').set_min(self, self.y)
        self.property('select_end_y').set_max(self, self.max_y)
        self.select_end_y = self.max_y - self.border
        self.btn_1_pos = (self.select_start_x, self.select_start_y)
        self.btn_2_pos = (self.select_start_x, self.select_end_y)
        self.btn_3_pos = (self.select_end_x, self.select_end_y)
        self.btn_4_pos = (self.select_end_x, self.select_start_y)
        self.crop_buttons = [self.btn_1_pos, self.btn_2_pos, self.btn_3_pos, self.btn_4_pos]

    def clear_crop_mesh(self):
        cur_screen = self.root.ids.screen_manager.current
        image_canvas = self.screen_ids[cur_screen].ids.stencil_layout.children[0]
        for item in self.objects:
            # REMOVE VERTEX INSTRUCTIONS FROM THE 'self.objects' -> 'InstructionGroup'
            instruction = self.objects.pop(-1)
            image_canvas.canvas.remove(instruction)
        for i in range(4):
            image_canvas.remove_widget(self.corner[i])

    def crop_image(self):
        cur_screen = self.root.ids.screen_manager.current
        if self.recipe_image != '' and len(self.screen_ids[cur_screen].ids.stencil_layout.children[0].children) > 3:
            if cur_screen == 'new_screen':
                save_img_as = "images/bin/" + "new.jpg"
            else:
                save_img_as = "images/bin/" + str(self.title_display) + ".jpg"
            with Image.open(self.recipe_image) as img:
                w, h = img.size
                x_scale = w / self.im_x
                y_scale = h / self.im_y
                if w / h > self.im_x / self.im_y:
                    y_wid = h / x_scale
                    diff = (self.im_y - y_wid) / 2
                    top_left_point = int((x_scale * (self.crop_buttons[1][0] - self.x))), \
                                     int(x_scale * (abs(self.crop_buttons[1][1] - (self.new_height + self.im_y)) - diff))
                    btm_right_point = int(x_scale * (self.crop_buttons[3][0] - self.x)), \
                                      int(x_scale * (self.im_y - (self.crop_buttons[3][1] - self.new_height) - diff))
                    if top_left_point[1] < 0:
                        top_left_point = top_left_point[0], 0
                    if btm_right_point[1] > h:
                        btm_right_point = btm_right_point[0], h
                else:
                    x_wid = w / y_scale
                    diff = (self.im_x - x_wid) / 2
                    top_left_point = int(y_scale * (self.crop_buttons[1][0] - self.x - diff)), \
                                     int(y_scale * abs(self.crop_buttons[1][1] - (self.new_height + self.im_y)))
                    btm_right_point = int((y_scale * (self.crop_buttons[3][0] - self.x - diff))), \
                                      int(y_scale * (self.im_y - (self.crop_buttons[3][1] - self.new_height)))
                    if top_left_point[0] < 0:
                        top_left_point = 0, top_left_point[1]
                    if btm_right_point[0] > w:
                        btm_right_point = w, btm_right_point[1]
                if abs(round((w / h), 6) - 1.33333) < 0.15:
                    while round(((btm_right_point[0] - top_left_point[0]) /
                                 (btm_right_point[1] - top_left_point[1])), 5) != 1.33333:
                        if round(((btm_right_point[0] - top_left_point[0]) /
                                  (btm_right_point[1] - top_left_point[1])), 6) < 1.33333:
                            btm_right_point = btm_right_point[0], btm_right_point[1] - 0.0001
                        elif round(((btm_right_point[0] - top_left_point[0]) /
                                  (btm_right_point[1] - top_left_point[1])), 6) > 1.33333:
                            btm_right_point = btm_right_point[0] - 0.0001, btm_right_point[1]
                area = top_left_point + btm_right_point
                img.crop(area).save(save_img_as)
            self.clear_crop_mesh()
            self.screen_ids[cur_screen].ids.stencil_layout.children[0].children[0].reload()
            self.recipe_image = save_img_as

    def on_click_down(self, *args):
        click = args[0][1].pos
        cur_screen = self.root.ids.screen_manager.current
        if self.screen_ids[cur_screen].ids.stencil_layout.children[0].collide_point(*click):
            click_x, click_y = click
            index = 0
            self.button_click = False
            for item in self.crop_buttons:
                btn_x, btn_y = item
                if abs(btn_x - click_x) <= 20 and abs(btn_y - click_y) <= 20:
                    self.button_click = True
                    self.currently_clicked = index
                index += 1
            if not self.button_click:
                self.position = click
                try:
                    self.select_start_x, self.select_start_y = self.position
                except ValueError as v:
                    print(v)

    def on_click_up(self, *args):
        c_location = True
        collide = False
        cur_screen = self.root.ids.screen_manager.current
        if len(args) > 0:
            click = args[0][1].pos
            try:
                if self.screen_ids[cur_screen].ids.stencil_layout.children[0].collide_point(*click):
                    c_location = True
                    collide = True
                    if not self.button_click:  # initialization step (No-Click)
                        try:
                            self.select_end_x, self.select_end_y = click
                        except ValueError as v:
                            print(v)
            except Exception as e:
                c_location = False
                print(e)
        if not self.button_click and c_location and collide:
            self.reset_buttons()
        elif self.first_run:
            self.reset_buttons()
            self.first_run = False
        elif len(args) > 0:
            click = args[0][1].pos
            try:
                if self.screen_ids[cur_screen].ids.stencil_layout.children[0].collide_point(*click):
                    corner_x, corner_y = click
                    last_corner_x, last_corner_y = self.crop_buttons[self.currently_clicked]
                    minus_index = (self.currently_clicked - 1) % 4
                    plus_index = (self.currently_clicked + 1) % 4
                    if (self.currently_clicked % 2) == 0:
                        if (last_corner_x - corner_x) > (last_corner_y - corner_y):
                            corner_y = last_corner_y - (last_corner_x - corner_x) * (3 / 4)
                            click = corner_x, corner_y
                        elif (last_corner_x - corner_x) < (last_corner_y - corner_y):
                            corner_x = last_corner_x - (last_corner_y - corner_y) * (4 / 3)
                            if corner_x < 150:
                                corner_x = 150
                            elif corner_x > 650:
                                corner_x = 650
                            click = corner_x, corner_y
                        self.crop_buttons[minus_index] = (
                            self.crop_buttons[minus_index][0], corner_y)
                        self.crop_buttons[plus_index] = (
                            corner_x, self.crop_buttons[plus_index][1])
                    else:
                        if (last_corner_x - corner_x) > (last_corner_y - corner_y):
                            corner_y = last_corner_y + (last_corner_x - corner_x) * (3 / 4)
                            click = corner_x, corner_y
                        elif (last_corner_x - corner_x) < (last_corner_y - corner_y):
                            corner_x = last_corner_x + (last_corner_y - corner_y) * (4 / 3)
                            if corner_x < 150:
                                corner_x = 150
                            elif corner_x > 650:
                                corner_x = 650
                            click = corner_x, corner_y
                        self.crop_buttons[minus_index] = (
                            corner_x, self.crop_buttons[minus_index][1])
                        self.crop_buttons[plus_index] = (
                            self.crop_buttons[plus_index][0], corner_y)
                    self.crop_buttons[self.currently_clicked] = click
                    self.update_buttons()
            except Exception as e:
                print(e)

    def reset_buttons(self, *args):
        if len(args) > 0:
            self.select_start_x = self.x + self.border
            self.select_start_y = self.y + self.border
            self.select_end_x = self.x + self.im_x - self.border
            self.select_end_y = self.y + self.im_y - self.border
        self.btn_1_pos = (self.select_start_x, self.select_start_y)
        self.btn_2_pos = (self.select_start_x, self.select_end_y)
        self.btn_3_pos = (self.select_end_x, self.select_end_y)
        self.btn_4_pos = (self.select_end_x, self.select_start_y)
        self.crop_buttons = [self.btn_1_pos, self.btn_2_pos, self.btn_3_pos, self.btn_4_pos]

    def update_buttons(self, *args):
        cur_screen = self.root.ids.screen_manager.current
        image_canvas = self.screen_ids[cur_screen].ids.stencil_layout.children[0]
        '''Prevent the 4 corners from crossing over each other by swapping their position'''
        if self.crop_buttons[0][0] > self.crop_buttons[3][0]:
            btn_1, btn_2, btn_3, btn_4 = self.crop_buttons
            self.crop_buttons = [btn_4, btn_3, btn_2, btn_1]
        if self.crop_buttons[0][1] > self.crop_buttons[1][1]:
            btn_1, btn_2, btn_3, btn_4 = self.crop_buttons
            self.crop_buttons = [btn_2, btn_1, btn_4, btn_3]
        # CREATE CROPPING BUTTONS IF NOT ALREADY CREATED
        for i in range(len(self.crop_buttons)):
            if len(image_canvas.children) < 5:
                self.corner[i] = CropButton()
                self.corner[i].children[0].pos = self.crop_buttons[i]
                self.corner[i].children[0].center = self.crop_buttons[i]
            else:
                self.corner[i].children[0].pos = self.crop_buttons[i]
                self.corner[i].children[0].center = self.crop_buttons[i]
        if len(args) > 0:
            self.update_mesh(args[0])
        else:
            self.update_mesh(image_canvas)

    def update_mesh(self, image_canvas):
        self.vertex_0 = []
        self.vertex_1 = []
        self.vertex_2 = []
        self.vertex_3 = []
        image_width, image_height = image_canvas.size
        if self.crop_buttons[0][0] > self.crop_buttons[3][0]:
            btn_1, btn_2, btn_3, btn_4 = self.crop_buttons
            self.crop_buttons = [btn_4, btn_3, btn_2, btn_1]
        if self.crop_buttons[0][1] > self.crop_buttons[2][1]:
            btn_1, btn_2, btn_3, btn_4 = self.crop_buttons
            self.crop_buttons = [btn_2, btn_1, btn_4, btn_3]

        self.vertex_0.extend([self.x, self.y, 0, 0, self.crop_buttons[0][0], self.crop_buttons[0][1], 0, 0,
                              self.crop_buttons[1][0], self.crop_buttons[1][1], 0, 0, self.x, (self.y + image_height), 0, 0])
        self.vertex_1.extend([self.x, (self.y + image_height), 0, 0, self.crop_buttons[1][0], self.crop_buttons[1][1], 0, 0,
                              self.crop_buttons[2][0], self.crop_buttons[2][1], 0, 0, (self.x + image_width),
                              (self.y + image_height), 0, 0])
        self.vertex_2.extend([(self.x + image_width), (self.y + image_height), 0, 0, self.crop_buttons[2][0],
                              self.crop_buttons[2][1], 0, 0, self.crop_buttons[3][0], self.crop_buttons[3][1], 0, 0,
                              (self.x + image_width), self.y, 0, 0])
        self.vertex_3.extend([(self.x + image_width), self.y, 0, 0, self.crop_buttons[3][0], self.crop_buttons[3][1],
                              0, 0, self.crop_buttons[0][0], self.crop_buttons[0][1], 0, 0, self.x, self.y, 0, 0])
        indices_mesh = list(range(len(self.vertex_0) // 4))
        if len(self.objects) == 0:
            obj = InstructionGroup()
            # with image_canvas.canvas:
            color = Color(1, 1, 1, 0.5)
            self.mesh0 = Mesh(vertices=self.vertex_0, indices=indices_mesh, mode='triangle_fan')
            self.mesh1 = Mesh(vertices=self.vertex_1, indices=indices_mesh, mode='triangle_fan')
            self.mesh2 = Mesh(vertices=self.vertex_2, indices=indices_mesh, mode='triangle_fan')
            self.mesh3 = Mesh(vertices=self.vertex_3, indices=indices_mesh, mode='triangle_fan')
            obj.add(color)
            obj.add(self.mesh0)
            obj.add(self.mesh1)
            obj.add(self.mesh2)
            obj.add(self.mesh3)
            self.objects.append(obj)
            image_canvas.canvas.add(obj)
            for i in range(4):
                image_canvas.add_widget(self.corner[i])
        else:
            self.mesh0.vertices = self.vertex_0
            self.mesh1.vertices = self.vertex_1
            self.mesh2.vertices = self.vertex_2
            self.mesh3.vertices = self.vertex_3  # ______________________________________________________________


if __name__ == '__main__':
    MyRecipeBookApp().run()
