import os
from functools import partial

from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView

from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.button import MDRoundFlatButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.uix.image import Image
from kivymd.uix.button import MDIconButton, MDRaisedButton
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.progressbar import MDProgressBar

from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineAvatarIconListItem, CheckboxLeftWidget, MDList


class CheckBoxDialog(MDFlatButton):

    """
    widget = CheckBoxDialog(
        text='OPEN THIS',
        dialog_title='rG',
        item_names=['1', '2', '3'],
        source=None
    )
    """

    def __init__(
        self,
        dialog_title,
        item_names,
        source,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.source = source
        self. item_list = MDList()
        for name in item_names:
            item = self.create_item(name)
            self.item_list.add_widget(item)

        self.from_code = dialog_title

        self.dialog = MDDialog(
            title=f'Transitions from: {dialog_title}',
            type='custom',
            content_cls=self.item_list,
            buttons=[
                MDFlatButton(
                    text="OK",
                    text_color=self.theme_cls.primary_color,
                )
            ]
        )
        self.dialog.buttons[0].on_press = self.dismiss_dialog

        self.on_press = self.dialog.open

    def dismiss_dialog(self):
        for item in self.item_list.children:
            a = self.from_code
            b = item.ids['check'].ids['name']
            key = f'{a}|{b}'
            if item.ids['check'].active:
                print(key, 'SET')
            else:
                print(key, 'UNSET')
        self.dialog.dismiss()

    @staticmethod
    def create_item(name):
        item = OneLineAvatarIconListItem(text=name, divider=None)
        check = CheckboxLeftWidget()
        item.add_widget(check)
        check.ids['name'] = name
        check.ids['item'] = item
        item.ids['check'] = check

        return item


class ScrollScreen(ScrollView):

    screen_populated = BooleanProperty(False)

    def __init__(
            self,
            item_list,
            **kwargs
    ):
        super().__init__(**kwargs)

        self.screen_populated = False
        self.item_list = item_list
        self.n_items = len(item_list)
        self.container = MDGridLayout(
            cols=1,
            padding=10,
            spacing=10,
            size_hint_x=1,
            size_hint_y=None
        )
        self.container.bind(minimum_height=self.container.setter('height'))
        self.add_widget(self.container)

        self.progress_bar = MDProgressBar(
            value=5,
            pos_hint={'center_x': 0.5, 'center_y': 1.0},
            color=(0, 0, 0, 1)
        )

        self.container.add_widget(self.progress_bar)

    def fill_container(self):
        i = 1
        denom = self.n_items * 2
        for defs in self.item_list:
            dt = i / denom
            pct = int((1 / self.n_items) * 100)
            if defs['_pattern'] in ('text', 'textfile'):
                Clock.schedule_once(partial(self.add_text, defs, pct), dt)
            if defs['_pattern'] in ('image', 'imagecard'):
                Clock.schedule_once(partial(self.add_image, defs, pct), dt)
            i += 1
        self.screen_populated = True
        self.container.remove_widget(self.progress_bar)

    def add_text(self, definitions, pct, dt):

        pattern = definitions.pop('_pattern')
        text = definitions.pop('text')
        if pattern == 'textfile':
            with open(text, 'r') as f:
                text = f.read()

        widget = WrappedLabel(
            text=text,
            size_hint_y=None,
            size_hint_x=1,
            text_size=(None, None),
            width_padding=20,
            **definitions
        )
        self.container.add_widget(widget)
        self.set_progress_bar(pct)

    def add_image(self, definitions, pct, dt):
        pattern = definitions.pop('_pattern')

        if pattern == 'image':
            widget = Image(
                allow_stretch=True,
                keep_ratio=True,
                size_hint_y=None,
                size_hint_x=None,
                **definitions
            )
            self.container.add_widget(widget)

            widget.width = Window.width
            widget.height = Window.width / widget.image_ratio
        elif pattern == 'imagecard':
            widget = ImageCard(
                orientation="vertical",
                padding="8dp",
                size_hint=(None, None),
                size=("280dp", "180dp"),
                pos_hint={"center_x": .5, "center_y": .5},
                **definitions
            )
            self.container.add_widget(widget)

            widget.width = Window.width
            widget.height = Window.width

        self.set_progress_bar(pct)

    def set_progress_bar(self, set_at):
        self.progress_bar.value = set_at

class LabeledDropdown(MDGridLayout):

    def __init__(
            self,
            label,
            options,
            store,
            value_key='value',
            width_mult=100,
            **kwargs
    ):
        super().__init__(**kwargs)

        self.label = label
        self.store = store
        self.value_key = value_key

        title = MDLabel(text=label, font_style='Button')
        self.widget = DropdownClass(
            menu_items=options,
            truncate_label=None,
            position='center',
            width_mult=width_mult,
            size_hint=(0.35, None),
            pos_hint={'center_x': .5, 'center_y': 0.5}
        )
        self.widget.set_item(self.store.get(label)[self.value_key])
        self.widget.bind(text=self.store_new_value)
        self.add_widget(title)
        self.add_widget(self.widget)

    def store_new_value(self, _, text):

        self.store.put(self.label, **{self.value_key: text})


class DropdownTable(MDFloatLayout):

    table_populated = BooleanProperty(False)
    calls = NumericProperty(0)

    def __init__(
            self,
            items,
            options,
            store,
            shape,
            value_key='value',
            create_table=True,
            **kwargs
    ):
        super().__init__(**kwargs)

        self.options = options
        self.items = items
        self.store = store
        self.value_key = value_key
        self.calls = 0
        self.n_rows, self.n_cols = shape
        self.n_cells = len(self.items)
        self.table_populated = False
        self.bind(table_populated=lambda *x: Clock.schedule_once(lambda dt: self.create_table_layout(), 0.5))

        self.table = MDGridLayout(
            rows=self.n_rows,
            cols=self.n_cols,
            padding=dp(10),
            size_hint=(0.95, 0.9),
            pos_hint={'center_x': 0.5, 'center_y': 0.55}
        )

        self.progress_bar = MDProgressBar(
            value=5,
            pos_hint={'center_x': 0.5, 'center_y': 0.999},
            color=(0, 0, 0, 1)
        )

        self.add_widget(self.progress_bar)

        if create_table:
            self.append_table()

    def append_table(self):
        self.set_progress_bar(5)
        self.table_populated = True

    def create_table_layout(self, *_):
        denom = self.n_cells
        for i, label in enumerate(self.items):
            j = (i + 1) / denom
            pct = int(((i + 1) / self.n_cells) * 100)

            Clock.schedule_once(partial(self.create_cell, label, pct), j)

        Clock.schedule_once(lambda dt: self.add_widget(self.table), (i + 3) / denom)
        Clock.schedule_once(lambda dt: self.remove_widget(self.progress_bar), (i + 4) / denom)

    def create_cell(self, label, pct, dt):

        box = MDBoxLayout(orientation='vertical', spacing=dp(0))
        lab = MDLabel(
            text=label, font_style='H6',
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(1.0, 1.0),
            halign='center',
            valign='center'
        )
        ddc = DropdownClass(
            menu_items=self.options,
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        value = self.store.get(label)[self.value_key]
        ddc.set_item(value)
        ddc.ids['key'] = label
        ddc.bind(text=self._set_weight)

        box.add_widget(lab)
        box.add_widget(ddc)
        self.table.add_widget(box)
        self.set_progress_bar(pct)

    def set_progress_bar(self, set_at):
        self.progress_bar.value = set_at

    def _set_weight(self, widget, text):
        self.store.put(widget.ids['key'], **{self.value_key: text})
        self.calls += 1


class CheckboxTable(MDFloatLayout):

    table_populated = BooleanProperty(False)

    def __init__(
            self,
            row_items,
            col_items,
            store,
            create_table=True,
            **kwargs
    ):
        super().__init__(**kwargs)

        self.table = MDGridLayout(
            rows=len(row_items) + 1,
            cols=len(col_items) + 1,
            padding=dp(10),
            size_hint=(0.95, 0.9),
            pos_hint={'center_x': 0.5, 'center_y': 0.55}
        )
        self.n_rows = len(row_items) + 1
        self.n_cols = len(col_items) + 1
        self.row_items = row_items
        self.col_items = col_items
        self.store = store
        self.table_populated = False
        self.bind(table_populated=lambda *x: Clock.schedule_once(lambda dt: self.create_table_layout(), 0.5))
        self.checkbox_dict = dict()

        button = MDRaisedButton(
            text='Restore Defaults',
            size_hint=(0.95, 0.1),
            pos_hint={'center_x': 0.5, 'center_y': 0.05},
            on_press=self._reset_transition_defaults
        )

        self.progress_bar = MDProgressBar(
            value=5,
            pos_hint={'center_x': 0.5, 'center_y': 0.999},
            color=(0, 0, 0, 1)
        )

        self.add_widget(button)
        self.add_widget(self.progress_bar)

        if create_table:
            self.append_table()

    def set_progress_bar(self, set_at):
        self.progress_bar.value = set_at

    def append_table(self):
        self.set_progress_bar(5)
        self.table_populated = True

    def create_table_layout(self, *_):
        for col in (['', ] + self.col_items):
            lab = MDLabel(
                text=col,
                font_style='Caption',
                halign='center',
                size_hint=(1 / self.n_cols, 1 / self.n_rows),
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
            )
            self.table.add_widget(lab)
        denom = self.n_rows / 3
        for i, row in enumerate(self.row_items):
            j = (i + 1) / denom
            pct = int(((i + 1) / self.n_rows) * 100)
            cells = [row, ] + self.col_items
            cells = cells[:]

            Clock.schedule_once(partial(self.create_row, cells, pct), j)

        Clock.schedule_once(lambda dt: self.add_widget(self.table), (i + 3) / denom)
        Clock.schedule_once(lambda dt: self.remove_widget(self.progress_bar), (i + 4) / denom)

    def create_row(self, cells, pct, dt):
        row = cells.pop(0)
        lab = MDLabel(
            text=row,
            font_style='Caption',
            valign='center',
            size_hint=(1 / self.n_cols, 1 / self.n_rows),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.table.add_widget(lab)

        for col in cells:
            transition_string = f'{row}|{col}'
            lab = MDCheckbox(
                size_hint=(1 / 10, 1 / 19),
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                active=self.store.get(transition_string)['value']
            )
            lab.ids['transition'] = transition_string
            lab.bind(active=self._set_transition)
            self.checkbox_dict[transition_string] = lab
            self.table.add_widget(lab)

        self.set_progress_bar(pct)

    def _reset_transition_defaults(self, *_):
        for k, d in self.store.find():
            value = d['value']
            default = d['default']

            if value != default:
                self.checkbox_dict[k].active = default

    def _set_transition(self, element, value):
        key = element.ids['transition']
        d = self.store.get(key)
        d['value'] = value
        self.store.put(key, **d)


class ImageCard(MDCard):

    def __init__(
            self,
            image_list,
            image_path,
            **kwargs
    ):
        super().__init__(**kwargs)

        if isinstance(image_list, dict):
            image_list, caption_list = zip(*image_list.items())
            self.caption_list = list(caption_list)
        else:
            self.caption_list = [''] * len(image_list)
        self.image_list = list(image_list)
        self.image_path = image_path
        self.image_ind = 0

        self.image = Image(
            source=os.path.join(self.image_path, self.image_list[self.image_ind]),
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(1.0, 1.0)
        )

        self.add_widget(self.image)

        button_backward = MDIconButton(
            icon='skip-previous',
            on_press=self.page_image,
            size_hint_x=0.5
        )

        button_forward = MDIconButton(
            icon='skip-next',
            on_press=self.page_image,
            size_hint_x=0.5
        )

        self.label = WrappedLabel(
            text=self.caption_list[self.image_ind],
            markup=True,
            halign='center',
            font_style='Caption',
        )
        button_box = MDBoxLayout(
            orientation='horizontal',
            size_hint=(1.0, 0.15)
        )
        button_box.add_widget(button_backward)
        button_box.add_widget(self.label)
        button_box.add_widget(button_forward)
        self.add_widget(button_box)

    def page_image(self, button):
        if button.icon == 'skip-next':
            self.image_ind += 1
        elif button.icon == 'skip-previous':
            self.image_ind -= 1

        if self.image_ind >= len(self.image_list):
            self.image_ind = 0
        if self.image_ind < 0:
            self.image_ind = len(self.image_list) - 1

        new_path = os.path.join(self.image_path, self.image_list[self.image_ind])
        self.label.text = self.caption_list[self.image_ind]
        self.image.source = new_path
        self.image.reload()


class Tab(MDFloatLayout, MDTabsBase):
    """Class implementing content for a tab."""
    content_text = StringProperty("")


class WrappedLabel(MDLabel):
    # Based on https://stackoverflow.com/a/58227983
    def __init__(self, width_padding=0, **kwargs):
        super().__init__(**kwargs)
        self.bind(
            width=lambda *x: self.setter('text_size')(self, (self.width - width_padding, None)),
            texture_size=lambda *x: self.setter('height')(self, self.texture_size[1])
        )


class DropdownClass(MDRoundFlatButton):

    def __init__(
            self,
            menu_items,
            truncate_label=None,
            width_mult=None,
            position='auto',
            **kwargs
    ):
        super().__init__(**kwargs)

        self.truncate_label = truncate_label
        if width_mult is None:
            n_char = max(len(x) for x in menu_items)
            if n_char < 3:
                width_mult = 1
            elif n_char < 10:
                width_mult = 2
            else:
                width_mult = 4

        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": f"{v}",
                "height": dp(42),
                "on_release": lambda x=f"{v}": self.set_item(x)
            } for v in menu_items
        ]
        self.current_item = None
        self.on_press = self.open_menu

        self.menu = MDDropdownMenu(
            caller=self,
            items=menu_items,
            position=position,
            width_mult=width_mult,
            max_height=dp(42 * 3)
        )
        self.menu.bind()
        self.set_item(menu_items[0]['text'])

    def set_item(self, text_item):
        if text_item not in [d['text'] for d in self.menu.items]:
            raise ValueError('Target text not in menu.')
        self.current_item = text_item
        if self.truncate_label is not None:
            if len(text_item) > self.truncate_label:
                i = self.truncate_label - 3
                if i < 1:
                    i = 1
                self.text = text_item[:i] + '...'
            else:
                self.text = text_item
        else:
            self.text = text_item
        self.menu.dismiss()

    def open_menu(self, *_):
        self.menu.open()
        text_list = [d['text'] for d in self.menu.items]
        n_items = len(text_list)
        ind = text_list.index(self.current_item)
        self.menu.ids.md_menu.scroll_y = 1.0 - (ind / n_items)
