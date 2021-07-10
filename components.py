import os

from kivy.properties import StringProperty
from kivy.metrics import dp

from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.button import MDRoundFlatButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.uix.image import Image
from kivymd.uix.button import MDIconButton


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
