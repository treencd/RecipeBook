from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.dropdown import DropDown
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.properties import ObjectProperty, BooleanProperty, StringProperty
from kivy.uix.label import Label
from kivymd.uix.button import MDRectangleFlatIconButton


from include.sqlactions import create_connection


class MDFloatButtonCancel(FloatLayout):
    pass


class MDFloatButtonCrop(FloatLayout):
    pass


class RoundedButton(Button):
    pass


class TileButton(Button):
    pass


class SettingsMenu(BoxLayout):
    pass


class CheckboxDropDown(DropDown):
    pass


class FileMenuDropDown(DropDown):
    pass


class FilePopup(Popup):
    pass


class IngredientGroup(TabbedPanelItem):
    pass


class CropButton(FloatLayout):
    pass


class TagPopup(Popup):
    def __init__(self, *args, **kwargs):
        super(TagPopup, self).__init__(**kwargs)

    def add_tags_input(self, tag_input, *args):
        tags = tag_input.strip('').split(',')
        for item in tags:
            if not item == '' or not item == ' ':
                tag_button = RoundedButton(text=str(item), size_hint_y=None, height=25)
                tag_button.bind(on_release=lambda x: self.ids.add_rem_tag_container.remove_widget(tag_button))
                self.ids.add_rem_tag_container.add_widget(tag_button)
        self.ids.new_tag_input_edit.text = ''

    def tag_dismiss(self):
        self.ids.add_rem_tag_container.clear_widgets()
        self.dismiss()

    def populate_tag_win(self, listing):
        for item in listing:
            tag_button = RoundedButton(text=str(item), size_hint_y=None, height=25)
            tag_button.bind(on_release=lambda x: self.ids.add_rem_tag_container.remove_widget(tag_button))
            self.ids.add_rem_tag_container.add_widget(tag_button)


class MDSearchField(Label):
    search_focus = BooleanProperty(False)
    bg_color = ObjectProperty((1, 1, 1, .6))

    def on_focus(self, instance, value):
        print(value)
        if value:
            self.search_focus = True
        else:
            self.search_focus = False


class DisplayScreen(Screen):  # DISPLAY RECIPES
    @staticmethod
    def update_rating(_rating, _id):
        conn = create_connection()
        if conn is not None:
            cur = conn.cursor()
            cur.execute("UPDATE recipes SET rating = ? where id = ?", (_rating, _id,))
            conn.commit()
            conn.close()


class NewScreen(Screen):  # CREATE RECIPES
    pass


class EditScreen(Screen):  # EDIT RECIPES
    pass


class IngredientBlock(GridLayout):
    pass


class HeaderLabel(BoxLayout):
    label_text = StringProperty('')
    label_markup = BooleanProperty(True)


class ConfirmDeletePopup(Popup):
    recipe_id = ObjectProperty(9999)

    def delete_confirmed(self, *args):
        print('DELETING:  ', int(self.recipe_id))
        try:
            sql = 'DELETE FROM recipes WHERE id=?'
            conn = create_connection()
            if conn is not None:
                cur = conn.cursor()
                cur.execute(sql, (int(self.recipe_id),))
                conn.commit()
            orphan = [str(self.recipe_id)]

            with open('include/orphanids.txt', 'a') as filehandle:
                for listitem in orphan:
                    filehandle.write('%s\n' % listitem)
        except Exception as e:
            print(e)
        self.dismiss()


class TagMDRectangleFlatIconButton(MDRectangleFlatIconButton):
    pass
