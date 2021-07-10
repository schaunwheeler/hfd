import random
import math
from functools import partial

from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.metrics import dp
from kivy.storage.jsonstore import JsonStore

from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Rectangle, Color
from kivy.uix.image import Image

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.tab import MDTabs
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.selectioncontrol import MDCheckbox

from utils import clock_time_from_seconds
from components import DropdownClass, Tab, WrappedLabel, ImageCard
from graphics import CircleWidget, RectangleWidget


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
            text='About',
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

    def _create_buffer(self):

        call_wait = float(self.call_wait_widget.text)
        combo_wait = float(self.combo_wait_widget.text)
        m, s = self.total_time_widget.text.split(':')
        total_time = int(m) * 60 + int(s)
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
                'Manual', 'Manual (cuts)', 'Manual (guards)'
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
                tab.add_widget(container)
            elif tab_label == 'Cut Transitions':
                container = MDGridLayout(rows=19, cols=10, padding=dp(20))
                for b in (['', ] + self.cuts):
                    lab = MDLabel(
                        text=b,
                        font_style='Caption',
                        halign='center',
                        size_hint=(1 / 10, 1 / 19),
                        pos_hint={'center_x': 0.5, 'center_y': 0.5},
                    )
                    container.add_widget(lab)

                for a in self.cuts + self.guards:
                    lab = MDLabel(
                        text=a,
                        font_style='Caption',
                        valign='center',
                        size_hint=(1 / 10, 1 / 19),
                        pos_hint={'center_x': 0.5, 'center_y': 0.5}
                    )
                    container.add_widget(lab)
                    for b in self.cuts:
                        transition_string = f'{a}|{b}'
                        lab = MDCheckbox(
                            size_hint=(1 / 10, 1 / 19),
                            pos_hint={'center_x': 0.5, 'center_y': 0.5},
                            active=self.transitions.get(transition_string)['value']
                        )
                        lab.ids['transition'] = transition_string
                        lab.bind(active=self._set_transition)
                        self.cut_checkboxes[transition_string] = lab
                        container.add_widget(lab)

            elif tab_label == 'Guard Transitions':
                container = MDGridLayout(rows=19, cols=10, padding=dp(20))
                for b in (['', ] + self.guards):
                    lab = MDLabel(
                        text=b,
                        font_style='Caption',
                        halign='center',
                        size_hint=(1 / 10, 1 / 19),
                        pos_hint={'center_x': 0.5, 'center_y': 0.5},

                    )
                    container.add_widget(lab)

                for a in self.cuts + self.guards:
                    lab = MDLabel(
                        text=a,
                        font_style='Caption',
                        valign='center',
                        size_hint=(1 / 10, 1 / 19),
                        pos_hint={'center_x': 0.5, 'center_y': 0.5}
                    )
                    container.add_widget(lab)
                    for b in self.guards:
                        transition_string = f'{a}|{b}'
                        lab = MDCheckbox(
                            size_hint=(1 / 10, 1 / 19),
                            pos_hint={'center_x': 0.5, 'center_y': 0.5},
                            active=self.transitions.get(transition_string)['value']
                        )
                        lab.ids['transition'] = transition_string
                        lab.bind(active=self._set_transition)
                        self.guard_checkboxes[transition_string] = lab
                        container.add_widget(lab)

            if tab_label != 'General':
                layout = MDBoxLayout(
                    orientation='vertical'
                )
                button = MDRaisedButton(
                    text='Restore Defaults',
                    size_hint=(None, None),
                    pos_hint={'center_x': 0.5, 'center_y': 0.5},
                    on_press=self._reset_transition_defaults
                )

                layout.add_widget(container)
                layout.add_widget(button)

                tab.add_widget(layout)

            self.tabs.add_widget(tab)
        self._disable_tabs()
        return self.tabs

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

    def _create_screen_3(self):

        self.scroll_container = ScrollView(
            do_scroll_x=False
        )

        self.container = GridLayout(
            cols=1, padding=10, spacing=10, size_hint_x=1, size_hint_y=None
        )
        self.container.bind(minimum_height=self.container.setter('height'))

        self.header = WrappedLabel(
            text='Historical Fencing Drills',
            halign='left',
            font_style='H3',
            size_hint_y=None,
            size_hint_x=1,
            text_size=(None, None),
            width_padding=20
        )

        with open('assets/texts/paragraph1.txt', 'r') as f:
            self.paragraph1 = WrappedLabel(
                text=f.read(),
                halign='left',
                font_style='Body1',
                size_hint_y=None,
                size_hint_x=1,
                text_size=(None, None),
                width_padding=20
            )

        image_files = {
            'fiore_getty.png': "[i]The Segno della Spada[/i] of Fiore dei Libieri, 1409.",
            'vadi_gladiatoria.jpg': "Filippo Vadi’s [i]De Arte Gladiatoria[/i], c.1482",
            'marozzo_opera.png': "Achille Marozzo's [i]Opera Nova[/i], 1536.",
            'meyer_1560_end.png': "Cutting drill diagrams from the end of Joachim Meyer's first manual, 1561.",
            'meyer_1570_longsword.png': "Longsword cut patterns from Joachim Meyer's second manual, 1570.",
            'meyer_1570_dussack.gif': "Instruction for Dussak from Joachim Meyer's second manual, 1570.",
            'fabris_science.png': "Salvatore Fabris's [i]Science and Practice of Arms[/i], 1606.",
            'marchant_rules.png': "Le Marchant’s [i]Rules and Regulations for the Sword Exercise of the Cavalry[/i], 1796.",
            'starzewski_fencing.png': "Michal Starzewski's [i]On Fencing[/i], 1830.",
            'angelo_infantry.png': "Angelo the Younger's [i]Infantry Sword Exercises[/i], 1845.",
            'burton_exercises.png': "Richard F. Burton's [i]The New Sword Exercise for Infantry[/i], 1876.",
            'happo_giri.png': "[i]The Happo Giri[/i] of Toyama Ryu Nakamura-ha, 1952.",
            'self_defense.png': "A diagram commonly used in modern self-defense courses.",
        }

        self.image1 = ImageCard(
            image_list=image_files,
            image_path='assets/images/',
            orientation="vertical",
            padding="8dp",
            size_hint=(None, None),
            size=("280dp", "180dp"),
            pos_hint={"center_x": .5, "center_y": .5}
        )

        with open('assets/texts/paragraph2.txt', 'r') as f:
            self.paragraph2 = WrappedLabel(
                text=f.read(),
                halign='left',
                font_style='Body1',
                size_hint_y=None,
                size_hint_x=1,
                text_size=(None, None),
                width_padding=20
            )

        self.image2 = Image(
            source='assets/images/cut_and_thrust_abbreviations.png',
            allow_stretch=True,
            keep_ratio=True,
            size_hint_y=None,
            size_hint_x=None,
            width=self.container.width,
            height=self.container.width
        )
        with open('assets/texts/paragraph3.txt', 'r') as f:
            self.paragraph3 = WrappedLabel(
                text=f.read(),
                markup=True,
                halign='left',
                font_style='Body1',
                size_hint_y=None,
                size_hint_x=1,
                text_size=(None, None),
                width_padding=20
            )

        self.container.add_widget(self.header)
        self.container.add_widget(self.paragraph1)
        self.container.add_widget(self.image1)
        self.container.add_widget(self.paragraph2)
        self.container.add_widget(self.image2)
        self.container.add_widget(self.paragraph3)

        self.scroll_container.add_widget(self.container)

        return self.scroll_container

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

    def open_screen3(self, *_):
        self.cancel_all_events()
        self.set_dims()

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

    def change_value(self, _, text):
        self.call_diagram.pointer_position_code = text
        self.call_diagram.update_lines()

    def set_dims(self, *_):
        width = Window.width
        adjusted_width = width - 20  # * 0.66
        self.image1.width = adjusted_width
        self.image1.height = adjusted_width
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


if __name__ == '__main__':

    # Window.size = (720 / 2, 1280 / 2)
    HistoricalFencingDrillsApp().run()
