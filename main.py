import random
import math
from functools import partial

from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.core.audio import SoundLoader
from kivy.metrics import dp
from kivy.properties import StringProperty

from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, Line, Ellipse
from kivy.storage.jsonstore import JsonStore

from kivymd.uix.tab import MDTabsBase, MDTabs
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRoundFlatButton, MDRaisedButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.slider import MDSlider


class Tab(MDFloatLayout, MDTabsBase):
    """Class implementing content for a tab."""
    content_text = StringProperty("")


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


class WrappedLabel(MDLabel):
    # Based on https://stackoverflow.com/a/58227983
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(
            width=lambda *x: self.setter('text_size')(self, (self.width, None)),
            texture_size=lambda *x: self.setter('height')(self, self.texture_size[1])
        )


class CircleWidget(Widget):
    def __init__(self, **kwargs):
        super(CircleWidget, self).__init__(**kwargs)

        self.pointer_position_code = None
        self.ignore_vals = (None, 'H', 'rH', 'L', 'rL', 'M', 'rM', 'G', 'rG', 'T')

        with self.canvas:
            self.color = Color(240, 255, 0, 1)
            self.circle = Ellipse(
                pos=self.center,
                size=(self.width * 0.05, self.height * 0.05)
            )

        self.bind(pos=self.update_circle, size=self.update_circle)

    def calculate_coordinates(self, *_):
        center_x, center_y = self.center
        x = self.width / 2
        y = self.height / 2
        part_x = x * 0.66
        part_y = y * 0.66

        offset = min(self.width * 0.05, self.height * 0.05)

        if self.pointer_position_code in self.ignore_vals:
            return center_x - offset, center_y - offset
        elif self.pointer_position_code == '9':
            return center_x - offset, center_y - offset
        elif self.pointer_position_code == '1':
            return center_x - x - offset, center_y - y - offset
        elif self.pointer_position_code == '2':
            return center_x + x - offset, center_y - y - offset
        elif self.pointer_position_code == '3':
            return center_x - x - offset, center_y + y - offset
        elif self.pointer_position_code == '4':
            return center_x + x - offset, center_y + y - offset
        elif self.pointer_position_code == '5':
            return center_x - x - offset, center_y - offset
        elif self.pointer_position_code == '6':
            return center_x + x - offset, center_y - offset
        elif self.pointer_position_code == '7':
            return center_x - offset, center_y - y - offset
        elif self.pointer_position_code == '8':
            return center_x - offset, center_y + y - offset
        else:
            raise ValueError('Invalid pointer_position_code.')

    def update_circle(self, *_):
        offset = min(self.width * 0.05, self.height * 0.05)
        self.circle.pos = self.calculate_coordinates()
        self.circle.size = (offset * 2, offset * 2)

        if self.pointer_position_code in self.ignore_vals:
            self.color.rgba = (0, 0, 0, 0)
        else:
            self.color.rgba = (240, 255, 0, 1)


class RectangleWidget(Widget):
    def __init__(self, **kwargs):
        super(RectangleWidget, self).__init__(**kwargs)

        self.pointer_position_code = '9'

        with self.canvas:
            Color(0, 0, 0, 0.1)
            self.rect1 = Rectangle(
                pos=self.center,
                size=(-self.width / 2., self.height / 2.)
            )

            Color(0, 0, 0, 0.1)
            self.rect2 = Rectangle(
                pos=self.center,
                size=(self.width / 2., self.height / 2.)
            )

            Color(0, 0, 0, 0.1)
            self.rect3 = Rectangle(
                pos=self.center,
                size=(-self.width / 2., -self.height / 2.)
            )

            Color(0, 0, 0, 0.1)
            self.rect4 = Rectangle(
                pos=self.center,
                size=(self.width / 2., -self.height / 2.)
            )

            self.line_1_4_color = Color(1, 1, 1, 0.9)
            self.line_1_4 = Line(
                points=[0, self.height, self.width, 0],
                width=2
            )
            self.line_2_3_color = Color(1, 1, 1, 0.9)
            self.line_2_3 = Line(
                points=[0, self.height, self.width, 0],
                width=2
            )
            self.line_5_6_color = Color(1, 1, 1, 0.9)
            self.line_5_6 = Line(
                points=[self.width, self.height / 2, 0, self.height / 2],
                width=2
            )
            self.line_7_8_color = Color(1, 1, 1, 0.9)
            self.line_7_8 = Line(
                points=[self.width / 2, self.height, self.width / 2, 0],
                width=2
            )

            self.line_h_color = Color(1, 1, 1, 0.0)
            self.line_h = Line(
                points=[self.width / 2, self.height, self.width / 2, 0],
                width=2,
                cap='square'
            )

            self.line_g_color = Color(1, 1, 1, 0.0)
            self.line_g = Line(
                points=[self.width / 2, self.height, self.width / 2, 0],
                width=2,
                cap='square'
            )

            self.line_rh_color = Color(1, 1, 1, 0.0)
            self.line_rh = Line(
                points=[self.width / 2, self.height, self.width / 2, 0],
                width=2,
                cap='square'
            )

            self.line_rg_color = Color(1, 1, 1, 0.0)
            self.line_rg = Line(
                points=[self.width / 2, self.height, self.width / 2, 0],
                width=2,
                cap='square'
            )

            self.line_l_color = Color(1, 1, 1, 0.0)
            self.line_l = Line(
                points=[self.width / 2, self.height, self.width / 2, 0],
                width=2,
                cap='square'
            )

            self.line_m_color = Color(1, 1, 1, 0.0)
            self.line_m = Line(
                points=[self.width / 2, self.height, self.width / 2, 0],
                width=2,
                cap='square'
            )

            self.line_rl_color = Color(1, 1, 1, 0.0)
            self.line_rl = Line(
                points=[self.width / 2, self.height, self.width / 2, 0],
                width=2,
                cap='square'
            )

            self.line_rm_color = Color(1, 1, 1, 0.0)
            self.line_rm = Line(
                points=[self.width / 2, self.height, self.width / 2, 0],
                width=2,
                cap='square'
            )

            self.line_t_color = Color(1, 1, 1, 0.0)
            self.line_t = Line(
                points=[self.width / 2, self.height, self.width / 2, 0],
                width=2,
                cap='square'
            )

        self.bind(pos=self.update_rect, size=self.update_rect)
        self.bind(pos=self.update_lines, size=self.update_lines)

    def update_rect(self, *_):
        self.rect1.pos = self.center
        self.rect1.size = (-self.width / 2., self.height / 2.)

        self.rect2.pos = self.center
        self.rect2.size = (self.width / 2., self.height / 2.)

        self.rect3.pos = self.center
        self.rect3.size = (-self.width / 2., -self.height / 2.)

        self.rect4.pos = self.center
        self.rect4.size = (self.width / 2., -self.height / 2.)

        self.line_1_4.points = [
            self.center[0] + (self.width / 2),
            self.center[1] + (self.height / 2),
            self.center[0] - (self.width / 2),
            self.center[1] - (self.height / 2)
        ]

        self.line_2_3.points = [
            self.center[0] - (self.width / 2),
            self.center[1] + (self.height / 2),
            self.center[0] + (self.width / 2),
            self.center[1] - (self.height / 2)
        ]

        self.line_5_6.points = [
            self.center[0] + (self.width / 2),
            self.center[1],
            self.center[0] - (self.width / 2),
            self.center[1]
        ]

        self.line_7_8.points = [
            self.center[0],
            self.center[1] + (self.height / 2),
            self.center[0],
            self.center[1] - (self.height / 2)
        ]

        self.line_h.points = [
            self.center[0] + (self.width / 2),
            self.center[1] + (self.height * 0.25),
            self.center[0] - (self.width * 0.4),
            self.center[1] + (self.height * 0.5)
        ]

        self.line_g.points = [
            self.center[0] + (self.width / 2),
            self.center[1] + (self.height * 0.5),
            self.center[0] - (self.width * 0.25),
            self.center[1] + (self.height * 0.1)
        ]

        self.line_rh.points = [
            self.center[0] - (self.width / 2),
            self.center[1] + (self.height * 0.25),
            self.center[0] + (self.width * 0.4),
            self.center[1] + (self.height * 0.5)
        ]

        self.line_rg.points = [
            self.center[0] - (self.width / 2),
            self.center[1] + (self.height * 0.5),
            self.center[0] + (self.width * 0.25),
            self.center[1] + (self.height * 0.1)
        ]

        self.line_m.points = [
            self.center[0] + (self.width / 2),
            self.center[1] - (self.height * 0.1),
            self.center[0] - (self.width * 0.4),
            self.center[1] + (self.height * 0.4)
        ]

        self.line_rm.points = [
            self.center[0] - (self.width / 2),
            self.center[1] - (self.height * 0.1),
            self.center[0] + (self.width * 0.4),
            self.center[1] + (self.height * 0.4)
        ]

        self.line_l.points = [
            self.center[0] + (self.width / 2),
            self.center[1] - (self.height * 0.1),
            self.center[0] - (self.width * 0.4),
            self.center[1] - (self.height * 0.4)
        ]

        self.line_rl.points = [
            self.center[0] - (self.width / 2),
            self.center[1] - (self.height * 0.1),
            self.center[0] + (self.width * 0.4),
            self.center[1] - (self.height * 0.4)
        ]

        self.line_t.points = [
            self.center[0] - (self.width * 0.4),
            self.center[1] - (self.height * 0.1),
            self.center[0] - (self.width * 0.5),
            self.center[1] - (self.height * 0.4)
        ]

    def update_lines(self, *_):
        self.line_1_4_color.rgba = (1, 1, 1, 0.9)
        self.line_2_3_color.rgba = (1, 1, 1, 0.9)
        self.line_5_6_color.rgba = (1, 1, 1, 0.9)
        self.line_7_8_color.rgba = (1, 1, 1, 0.9)
        self.line_h_color.rgba = (1, 1, 1, 0.0)
        self.line_g_color.rgba = (1, 1, 1, 0.0)
        self.line_rh_color.rgba = (1, 1, 1, 0.0)
        self.line_rg_color.rgba = (1, 1, 1, 0.0)
        self.line_m_color.rgba = (1, 1, 1, 0.0)
        self.line_l_color.rgba = (1, 1, 1, 0.0)
        self.line_rm_color.rgba = (1, 1, 1, 0.0)
        self.line_rl_color.rgba = (1, 1, 1, 0.0)
        self.line_t_color.rgba = (1, 1, 1, 0.0)

        self.line_1_4.width = 2
        self.line_2_3.width = 2
        self.line_5_6.width = 2
        self.line_7_8.width = 2
        self.line_h.width = 2
        self.line_g.width = 2
        self.line_rh.width = 2
        self.line_rg.width = 2
        self.line_m.width = 2
        self.line_l.width = 2
        self.line_rm.width = 2
        self.line_rl.width = 2
        self.line_t.width = 2

        if self.pointer_position_code in ('1', '4'):
            self.line_1_4_color.rgba = (240, 255, 0, 1)
            self.line_1_4.width = 10
        elif self.pointer_position_code in ('2', '3'):
            self.line_2_3_color.rgba = (240, 255, 0, 1)
            self.line_2_3.width = 10
        elif self.pointer_position_code in ('5', '6'):
            self.line_5_6_color.rgba = (240, 255, 0, 1)
            self.line_5_6.width = 10
        elif self.pointer_position_code in ('7', '8'):
            self.line_7_8_color.rgba = (240, 255, 0, 1)
            self.line_7_8.width = 10
        elif self.pointer_position_code == 'H':
            self.line_h_color.rgba = (250, 0, 0, 1)
            self.line_h.width = 10
        elif self.pointer_position_code == 'G':
            self.line_g_color.rgba = (250, 0, 0, 1)
            self.line_g.width = 10
        elif self.pointer_position_code == 'rH':
            self.line_rh_color.rgba = (250, 0, 0, 1)
            self.line_rh.width = 10
        elif self.pointer_position_code == 'rG':
            self.line_rg_color.rgba = (250, 0, 0, 1)
            self.line_rg.width = 10
        elif self.pointer_position_code == 'M':
            self.line_m_color.rgba = (250, 0, 0, 1)
            self.line_m.width = 10
        elif self.pointer_position_code == 'L':
            self.line_l_color.rgba = (250, 0, 0, 1)
            self.line_l.width = 10
        elif self.pointer_position_code == 'rM':
            self.line_rm_color.rgba = (250, 0, 0, 1)
            self.line_rm.width = 10
        elif self.pointer_position_code == 'rL':
            self.line_rl_color.rgba = (250, 0, 0, 1)
            self.line_rl.width = 10
        elif self.pointer_position_code == 'T':
            self.line_t_color.rgba = (250, 0, 0, 1)
            self.line_t.width = 10
        elif self.pointer_position_code in (None, '9'):
            pass
        else:
            raise ValueError(f'Invalid pointer_position_code: {self.pointer_position_code}')


class HistoricalFencingDrillsApp(MDApp):

    def __init__(self, **kwargs):
        super(HistoricalFencingDrillsApp, self).__init__(**kwargs)
        self.total_time_widget = None
        self.call_wait_widget = None
        self.combo_wait_widget = None
        self.combo_repeat_widget = None
        self.combo_expand_widget = None
        self.min_combo_length_widget = None
        self.max_combo_length_widget = None
        self.mode_widget = None
        self.current_tab = 'General'
        self.cuts = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        self.guards = ['H', 'rH', 'L', 'rL', 'M', 'rM', 'G', 'rG', 'T']
        self.cut_checkboxes = dict()
        self.guard_checkboxes = dict()
        self.settings = JsonStore('settings.json')
        self.transitions = JsonStore('transitions.json')

    def build(self):
        # from kivy.utils import platform
        # if platform == 'android':
        #     from android.permissions import request_permissions, Permission
        #     request_permissions([
        #         Permission.READ_EXTERNAL_STORAGE,
        #         Permission.WRITE_EXTERNAL_STORAGE
        #     ])

        self.theme_cls.primary_palette = "Gray"
        parent = self.create_navigation()
        return parent

    def create_navigation(self):
        parent = MDBoxLayout(orientation='vertical')
        bottom_navigation = MDBottomNavigation()
        bottom_navigation_item1 = MDBottomNavigationItem(
            name='screen 1',
            text='Settings',
            icon='fountain-pen-tip',
            on_tab_press=self.cancel_all_events
        )
        bottom_navigation_item2 = MDBottomNavigationItem(
            name='screen 2',
            text='Drills',
            icon='sword',
            on_tab_press=self.schedule_calls
        )
        bottom_navigation_item3 = MDBottomNavigationItem(
            name='screen 3',
            text='Help',
            icon='book',
            on_tab_press=self.open_screen3
        )

        screen1 = self._create_screen_1()
        screen2 = self._create_screen_2()
        screen3 = self._create_screen_3()

        bottom_navigation_item1.add_widget(screen1)
        bottom_navigation_item2.add_widget(screen2)
        bottom_navigation_item3.add_widget(screen3)

        bottom_navigation.add_widget(bottom_navigation_item1)
        bottom_navigation.add_widget(bottom_navigation_item2)
        bottom_navigation.add_widget(bottom_navigation_item3)

        parent.add_widget(bottom_navigation)

        return parent

    def open_screen3(self, *_):
        self.cancel_all_events()
        self.set_dims()

    def schedule_calls(self, _):
        for row in self._create_buffer():
            Clock.schedule_once(
                partial(
                    self._update_screen2,
                    row
                ),
                row[0]
            )

    def _get_patterns(self):
        m, s = self.total_time_widget.text.split(':')
        total_time = int(m) * 60 + int(s)
        min_size = int(self.min_combo_length_widget.text)
        max_size = int(self.max_combo_length_widget.text)

        manual_options = ('Manual', 'Manual (cuts only)', 'Manual (guards only)')
        if self.mode_widget.text in manual_options:
            transitions_dict = dict()
            for t, v in self.transitions.find():
                if not v['value']:
                    continue
                a, b = t.split('|')
                if self.mode_widget.text == 'Manual (cuts only)':
                    if (a in self.guards) or (b in self.guards):
                        continue
                if self.mode_widget.text == 'Manual (guards only)':
                    if (a in self.cuts) or (b in self.cuts):
                        continue
                if a not in transitions_dict:
                    transitions_dict[a] = list()
                transitions_dict[a].append(b)

            transitions_set = set(transitions_dict.keys())
            transitions_dict = {k: list(transitions_set.intersection(v)) for k, v in transitions_dict.items()}
            transitions_set = list(transitions_set)

            call = random.choice(transitions_set)
            patterns = list()
            while total_time > 0:
                combo_length = random.randrange(min_size, max_size + 1)
                call = random.choice(transitions_dict[call])
                combo = [call]
                while len(combo) < combo_length:
                    call = random.choice(transitions_dict[call])
                    combo.append(call)
                    total_time -= 1
                patterns.append(combo)

        elif self.mode_widget.text == 'Pre-programmed':
            with open('assets/combos.txt', 'r') as f:
                patterns = [
                    line.strip().split(' ')
                    for line in f.readlines()
                ]

            patterns = random.choices(
                [
                    pat for pat in patterns
                    if (len(pat) >= min_size) and (len(pat) <= max_size)
                ],
                k=total_time
            )
        else:
            raise ValueError('Valid values are `Pre-programmed` and `Custom`.')

        return patterns

    def _update_screen2(self, row, _):
        call_time, call_length, time_text, call_text, full_call_text, play_sound = row
        self.time_label.text = time_text
        self.call_label.text = call_text
        self.full_call_label.text = full_call_text

        if play_sound:
            self.call_diagram.pointer_position_code = call_text
            self.call_diagram.update_lines()
            self.call_pointer.pointer_position_code = call_text
            self.call_pointer.update_circle()

            play_sound.play()

    def _create_buffer(self):

        call_wait = float(self.call_wait_widget.text)
        combo_wait = float(self.combo_wait_widget.text)
        m, s = self.total_time_widget.text.split(':')
        total_time = int(m) * 60 + int(s)
        min_size = int(self.min_combo_length_widget.text)
        max_size = int(self.max_combo_length_widget.text)
        combo_expand = True if self.combo_expand_widget.text == 'ON' else False
        combo_repeat = True if self.combo_repeat_widget.text == 'ON' else False

        patterns = self._get_patterns()

        sounds = {
            s: SoundLoader.load(f'assets/sounds/{s}.wav')
            for s in set().union(*patterns)
        }

        buffer = list()
        i = 0
        time_left = total_time + 10
        while i < (total_time + 10):
            if i < 10:

                row = (i, None, self.total_time_widget.text, 'READY', str(10 - i), None)
                buffer.append(row)
                time_left -= 1
                i += 1
            elif i == 10:
                time_string = clock_time_from_seconds(round(time_left))
                row = (i, None, time_string, 'BEGIN', '', None)
                buffer.append(row)
                time_left -= 1
                i += 1
            else:
                if len(patterns) == 0:
                    patterns = self._get_patterns()

                pat = patterns.pop()
                start = 2 if combo_expand else len(pat)
                for end in range(start, len(pat) + 1):
                    for call in range(end):
                        call_text = pat[call]
                        call_list = ' '.join(pat[:call + 1])
                        call_sound = sounds[call_text]
                        call_length = call_sound.length + call_wait

                        time_string = clock_time_from_seconds(math.floor(time_left))
                        row = (i, call_length, time_string, call_text, call_list, call_sound)
                        buffer.append(row)

                        i += call_length
                        time_left -= call_length
                        if time_left <= 0:
                            break

                    if time_left <= 0:
                        break
                    i += combo_wait
                    time_left -= combo_wait

                if combo_repeat and (time_left > 0):
                    end = len(pat)
                    for call in range(end):
                        call_text = pat[call]
                        call_list = ' '.join(pat[:call + 1])
                        call_sound = sounds[call_text]
                        call_length = call_sound.length + call_wait

                        time_string = clock_time_from_seconds(math.floor(time_left))
                        row = (i, call_length, time_string, call_text, call_list, call_sound)
                        buffer.append(row)

                        i += call_length
                        time_left -= call_length
                        if time_left <= 0:
                            break

                    if time_left <= 0:
                        break
                    i += combo_wait
                    time_left -= combo_wait

        j = 12
        prev_row = buffer[11]
        for row in buffer:
            if j >= (total_time + 10):
                break
            val = row[0]
            while math.floor(val) >= j:
                new_time = total_time + 9 - j
                if new_time <= 0:
                    break
                time_string = clock_time_from_seconds(new_time)
                new_row = (j, None, time_string) + prev_row[3:-1] + (None, )
                buffer.append(new_row)
                j += 1
            prev_row = row

        buffer = sorted(buffer, key=lambda t: t[0])
        buffer.append((
            total_time + 11,
            0,
            self.total_time_widget.text,
            'READY',
            '',
            None
        ))

        return buffer

    def _create_screen_1(self):

        container = MDGridLayout(
            cols=1,
            padding=dp(10),
            spacing=dp(10)
        )

        box = MDGridLayout(cols=1)
        title = MDLabel(text='Mode:', font_style='Button')
        self.mode_widget = DropdownClass(
            menu_items=[
                'Pre-programmed',
                'Manual', 'Manual (cuts only)', 'Manual (guards only)'
            ],
            truncate_label=None,
            position='center',
            width_mult=100,
            size_hint=(0.35, None),
            pos_hint={'center_x': .5, 'center_y': 0.5}
        )
        self.mode_widget.set_item(self.settings.get('Mode:')['text'])
        self.mode_widget.ids['title'] = 'Mode:'
        self.mode_widget.bind(text=self.store_new_value)
        box.add_widget(title)
        box.add_widget(self.mode_widget)
        container.add_widget(box)

        box = MDGridLayout(cols=1)
        title = MDLabel(text='Drill duration:', font_style='Button')
        self.total_time_widget = DropdownClass(
            menu_items=[
                str(h).zfill(2) + flag
                for h in range(1, 20)
                for flag in (':00', ':30')
            ][:-1],
            truncate_label=None,
            position='center',
            width_mult=100,
            size_hint=(0.35, None),
            pos_hint={'center_x': .5, 'center_y': 0.5}
        )
        self.total_time_widget.set_item(self.settings.get('Drill duration:')['text'])
        self.total_time_widget.ids['title'] = 'Drill duration:'
        self.total_time_widget.bind(text=self.store_new_value)
        box.add_widget(title)
        box.add_widget(self.total_time_widget)
        container.add_widget(box)

        pause_box = MDGridLayout(cols=2, rows=2, orientation='tb-lr', spacing=dp(5))
        title = MDLabel(text='Seconds after call:', font_style='Button')
        self.call_wait_widget = DropdownClass(
            menu_items=[str(x / 100) for x in range(5, 205, 5)],
            truncate_label=None,
            position='center',
            width_mult=2,
            size_hint=(0.35, None),
            pos_hint={'center_x': .5, 'center_y': 0.5}
        )
        self.call_wait_widget.set_item(self.settings.get('Seconds after call:')['text'])
        self.call_wait_widget.ids['title'] = 'Seconds after call:'
        self.call_wait_widget.bind(text=self.store_new_value)
        pause_box.add_widget(title)
        pause_box.add_widget(self.call_wait_widget)

        title = MDLabel(text='Seconds after combo:', font_style='Button')
        self.combo_wait_widget = DropdownClass(
            menu_items=[str(x / 100) for x in range(5, 205, 5)],
            truncate_label=None,
            position='center',
            width_mult=2,
            size_hint=(0.35, None),
            pos_hint={'center_x': .5, 'center_y': 0.5}
        )
        self.combo_wait_widget.set_item(self.settings.get('Seconds after combo:')['text'])
        self.combo_wait_widget.ids['title'] = 'Seconds after combo:'
        self.combo_wait_widget.bind(text=self.store_new_value)
        pause_box.add_widget(title)
        pause_box.add_widget(self.combo_wait_widget)

        container.add_widget(pause_box)

        length_box = MDGridLayout(cols=2, rows=2, orientation='tb-lr', spacing=dp(5))

        title = MDLabel(text='Minimum combo:', font_style='Button')
        self.min_combo_length_widget = DropdownClass(
            menu_items=[str(v) for v in range(2, 11)],
            truncate_label=None,
            position='center',
            width_mult=2,
            size_hint=(0.35, None),
            pos_hint={'center_x': .5, 'center_y': 0.5}
        )
        self.min_combo_length_widget.set_item(self.settings.get('Minimum combo:')['text'])
        self.min_combo_length_widget.ids['title'] = 'Minimum combo:'
        self.min_combo_length_widget.bind(text=self.store_new_value)
        length_box.add_widget(title)
        length_box.add_widget(self.min_combo_length_widget)

        title = MDLabel(text='Maximum combo:', font_style='Button')
        self.max_combo_length_widget = DropdownClass(
            menu_items=[str(v) for v in range(2, 11)],
            truncate_label=None,
            position='center',
            width_mult=2,
            size_hint=(0.35, None),
            pos_hint={'center_x': .5, 'center_y': 0.5}
        )
        self.max_combo_length_widget.set_item(self.settings.get('Maximum combo:')['text'])
        self.max_combo_length_widget.ids['title'] = 'Maximum combo:'
        self.max_combo_length_widget.bind(text=self.store_new_value)
        length_box.add_widget(title)
        length_box.add_widget(self.max_combo_length_widget)

        container.add_widget(length_box)

        box = MDGridLayout(cols=1)
        title = MDLabel(text='Repeat full combo at end:', font_style='Button')
        self.combo_repeat_widget = DropdownClass(
            menu_items=['OFF', 'ON'],
            truncate_label=None,
            position='center',
            width_mult=100,
            size_hint=(0.35, None),
            pos_hint={'center_x': .5, 'center_y': 0.5}
        )
        self.combo_repeat_widget.set_item(self.settings.get('Repeat full combo at end:')['text'])
        self.combo_repeat_widget.ids['title'] = 'Repeat full combo at end:'
        self.combo_repeat_widget.bind(text=self.store_new_value)
        box.add_widget(title)
        box.add_widget(self.combo_repeat_widget)
        container.add_widget(box)

        box = MDGridLayout(cols=1)
        title = MDLabel(
            text='Progressively expand combos:', font_style='Button'
        )
        self.combo_expand_widget = DropdownClass(
            menu_items=['OFF', 'ON'],
            truncate_label=None,
            position='center',
            width_mult=100,
            size_hint=(0.35, None),
            pos_hint={'center_x': .5, 'center_y': 0.5}
        )
        self.combo_expand_widget.set_item(self.settings.get('Progressively expand combos:')['text'])
        self.combo_expand_widget.ids['title'] = 'Progressively expand combos:'
        self.combo_expand_widget.bind(text=self.store_new_value)
        box.add_widget(title)
        box.add_widget(self.combo_expand_widget)
        container.add_widget(box)

        self.tabs = MDTabs()
        self.tabs.bind(on_tab_switch=self._switch_tabs)

        for tab_label in (
                'General',
                'Cut Transitions',
                'Guard Transitions'
        ):
            tab = Tab(title=tab_label)
            if tab_label == 'General':
                table = container
            elif tab_label == 'Cut Transitions':
                table = MDGridLayout(rows=19, cols=10, padding=dp(20))
                for b in (['', ] + self.cuts):
                    lab = MDLabel(
                        text=b,
                        font_style='Caption',
                        halign='center'
                    )
                    table.add_widget(lab)

                for a in self.cuts + self.guards:
                    lab = MDLabel(text=a, font_style='Caption', valign='center')
                    table.add_widget(lab)
                    for b in self.cuts:
                        transition_string = f'{a}|{b}'
                        lab = MDCheckbox(
                            size_hint=(None, None),
                            size=("18dp", "18dp"),
                            pos_hint={'center_x': 0.5, 'center_y': 0.5},
                            active=self.transitions.get(transition_string)['value']
                        )
                        lab.ids['transition'] = transition_string
                        lab.bind(active=self._set_transition)
                        self.cut_checkboxes[transition_string] = lab
                        table.add_widget(lab)

            elif tab_label == 'Guard Transitions':
                table = MDGridLayout(rows=19, cols=10, padding=dp(20))
                for b in (['', ] + self.guards):
                    lab = MDLabel(
                        text=b,
                        font_style='Caption',
                        halign='center'
                    )
                    table.add_widget(lab)

                for a in self.cuts + self.guards:
                    lab = MDLabel(text=a, font_style='Caption', valign='center')
                    table.add_widget(lab)
                    for b in self.guards:
                        transition_string = f'{a}|{b}'
                        lab = MDCheckbox(
                            size_hint=(None, None),
                            size=("18dp", "18dp"),
                            pos_hint={'center_x': 0.5, 'center_y': 0.5},
                            active=self.transitions.get(transition_string)['value']
                        )
                        lab.ids['transition'] = transition_string
                        lab.bind(active=self._set_transition)
                        self.guard_checkboxes[transition_string] = lab
                        table.add_widget(lab)

            if tab_label != 'General':
                layout = MDBoxLayout(
                    orientation='vertical'
                )
                button = MDRaisedButton(
                    text='Restore Defaults',
                    pos_hint={'center_x': 0.5, 'center_y': 0.5},
                    size_hint_x=1.0,
                    on_press=self._reset_transition_defaults
                )

                layout.add_widget(table)
                layout.add_widget(button)

                tab.add_widget(layout)
            else:
                tab.add_widget(table)
            self.tabs.add_widget(tab)
        self._disable_tabs()
        return self.tabs

    def _reset_transition_defaults(self, *_):
        for k, d in self.transitions.find():
            value = d['value']
            default = d['default']

            change_cuts = self.current_tab == 'Cut Transitions'
            in_cuts = k in self.cut_checkboxes
            is_different = value != default

            if change_cuts and in_cuts and is_different:
                self.cut_checkboxes[k].active = default
            elif (not change_cuts) and (not in_cuts) and is_different:
                self.guard_checkboxes[k].active = default

    def _set_transition(self, element, value):
        key = element.ids['transition']
        d = self.transitions.get(key)
        d['value'] = value
        self.transitions.put(key, **d)

    def _switch_tabs(self, tabs, tab, label, tab_text):

        self.current_tab = tab_text

    def _disable_tabs(self):
        manual_options = ('Manual', 'Manual (cuts only)', 'Manual (guards only)')
        flag = self.mode_widget.text not in manual_options
        for tab in self.tabs.get_slides():
            if tab.title != 'General':
                tab.tab_label.disabled_color = [0.0, 0.0, 0.0, 0.1]
                tab.tab_label.disabled = flag
                tab.disabled = flag

    def store_new_value(self, widget, text):
        key = widget.ids['title']
        a, b = None, None
        if key.upper() == 'Minimum combo:':
            a = self.min_combo_length_widget.text
            b = self.max_combo_length_widget.text
            if int(a) > int(b):
                self.max_combo_length_widget.set_item(a)
        if key.upper() == 'Maximum combo:':
            a = self.min_combo_length_widget.text
            b = self.max_combo_length_widget.text
            if int(b) < int(a):
                self.min_combo_length_widget.set_item(b)
        if key == 'Mode:':
            self._disable_tabs()
        self.settings.put(key, text=text)

    def _create_screen_2(self):
        container = MDFloatLayout()
        with container.canvas:
            Color(0, 0, 0, 0.75)

            Rectangle(
                pos=(0, 0),
                size=(Window.width, Window.height)
            )

        self.time_label = MDLabel(
            text=self.total_time_widget.text,
            halign='center',
            font_style='H2',
            pos_hint={'center_x': .5, 'center_y': .9},
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)
        )
        self.call_label = MDLabel(
            text='READY',
            halign='center',
            font_style='H3',
            pos_hint={'center_x': .5, 'center_y': .15},
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)
        )

        self.full_call_label = MDLabel(
            text='',
            halign='center',
            font_style='H4',
            pos_hint={'center_x': .5, 'center_y': .05},
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)
        )

        self.call_diagram = RectangleWidget(
            size_hint=(0.5, 0.6),
            pos_hint={'center_x': .5, 'center_y': .5}
        )
        self.call_pointer = CircleWidget(
            size_hint=(0.5, 0.6),
            pos_hint={'center_x': .5, 'center_y': .5}
        )
        self.call_diagram.pointer_position_code = None
        self.call_pointer.pointer_position_code = None

        container.add_widget(self.time_label)
        container.add_widget(self.call_diagram)
        container.add_widget(self.call_pointer)
        container.add_widget(self.call_label)
        container.add_widget(self.full_call_label)

        return container

    def change_value(self, widget, text):
        self.call_diagram.pointer_position_code = text
        self.call_diagram.update_lines()

    def _create_screen_3(self):

        self.scroll_container = ScrollView(
            do_scroll_x=False
        )

        from kivy.uix.gridlayout import GridLayout
        self.container = GridLayout(
            cols=1, spacing=10, size_hint_x=1, size_hint_y=None
        )
        self.container.bind(minimum_height=self.container.setter('height'))

        self.paragraph1 = WrappedLabel(
            text=(
                "In the 1560s, Joachim Meyer created a manuscript "
                "for one of his private students, providing instruction "
                "in longsword, dussack, and side sword. Though less "
                "extensive than Meyer's later 1570 publication, the early manuscript "
                "contained several cutting diagrams that serve as a useful basis"
                "for constructing individual drills."
            ),
            halign='center',
            font_style='Body1',
            size_hint_y=None,
            size_hint_x=1,
            text_size=(None, None)
        )

        self.image1 = Image(
            source='assets/images/meyer_ms.jpg',
            allow_stretch=True,
            keep_ratio=True,
            size_hint_y=None,
            size_hint_x=None,
            width=self.container.width,
            height=self.container.width,
        )

        self.paragraph2 = WrappedLabel(
            text=(
                "This app adapts those cutting diagrams to provide audio "
                "callouts of cut and thrust combinations to serve for individual "
                "training. The app assumes a simplified system of eight cuts and "
                "9 thrusts. The cuts are illustrated here, witih the cut begining "
                "at the position of its respective number and continuing along the "
                "line that extends from that number. This differs from the user "
                "interface, where the yellow dot marks where the cut should end. The"
                "one addition 'cut' - the '9' - is actually a thrust, to center of"
                "the body."
            ),
            halign='center',
            font_style='Body1',
            size_hint_y=None,
            size_hint_x=1,
            text_size=(None, None)
        )

        self.image2 = Image(
            source='assets/images/cut_patterns.png',
            allow_stretch=True,
            keep_ratio=True,
            size_hint_y=None,
            size_hint_x=None,
            width=self.container.width,
            height=self.container.width
        )

        self.paragraph3 = WrappedLabel(
            text=(
                "The app provides multiple ways to adjust the training program:\n\n"
                "   \u2022 [b]Round duration (minutes):[/b] the amount of time "
                "you want to train for.\n\n"
                "   \u2022 [b]Pause between calls (seconds):[/b] the number of seconds "
                "to wait calling out the next cut or thrust.\n\n"
                "   \u2022 [b]Pause between combos (seconds):[/b] the number of seconds "
                "to wait after a combination of multiple cuts and/or thrusts have been called out.\n\n"
                "   \u2022 [b]Combo size:[/b] this indicates the numbers of unique"
                "drill combinations the app has available for each length. For example, if "
                "'4' is selected, then each drill will involve four cuts.\n\n"
                "   \u2022 [b]Repeat full combo at end:[/b] the number of times to repeat "
                "the combo before moving on to the next one. If progressive expansion is on, "
                "then the repetition will only apply to the full combo, not each progressive subset.\n\n"
                "   \u2022 [b]Progressively expand combos:[/b] if ON, the app will "
                " start by calling out hte first two moves of the combo, then expand to "
                " three, then four, and so on, until the full combo is recited.\n\n"
            ),
            markup=True,
            halign='center',
            font_style='Body1',
            size_hint_y=None,
            size_hint_x=1,
            text_size=(None, None)
        )

        self.container.add_widget(self.paragraph1)
        self.container.add_widget(self.image1)
        self.container.add_widget(self.paragraph2)
        self.container.add_widget(self.image2)
        self.container.add_widget(self.paragraph3)

        self.scroll_container.add_widget(self.container)

        return self.scroll_container

    def set_dims(self, *_):
        width = Window.width
        adjusted_width = width  # * 0.66
        self.image1.width = adjusted_width
        self.image1.height = adjusted_width / self.image1.image_ratio
        self.image2.width = adjusted_width
        self.image2.height = adjusted_width / self.image2.image_ratio

    def cancel_all_events(self, *_):
        for event in Clock.get_events():
            event.cancel()
        self.time_label.text = self.total_time_widget.text
        self.call_label.text = 'READY'
        self.full_call_label.text = ''
        self.call_diagram.pointer_position_code = None
        self.call_pointer.pointer_position_code = None
        self.call_diagram.update_lines()
        self.call_pointer.update_circle()


def convert_value(v):
    if ':' in v:
        m, s = v.split(':')
        return int(m) * 60 + int(s)
    elif '.' in v:
        return float(v)
    elif '(' in v:
        return int(v.split(' (')[0])
    elif v.isnumeric():
        return int(v)
    else:
        return True if (v == 'ON') else False


def clock_time_from_seconds(seconds):
    m, s = divmod(seconds, 60)
    return f'{m:02d}:{s:02d}'


if __name__ == '__main__':

    Window.size = (720 / 2, 1280 / 2)
    HistoricalFencingDrillsApp().run()
