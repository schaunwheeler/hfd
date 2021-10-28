import random
import math
from functools import partial

from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.metrics import dp
from kivy.storage.jsonstore import JsonStore

from kivy.graphics import Rectangle, Color

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.tab import MDTabs
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDSeparator

from utils import clock_time_from_seconds
from components import Tab, DropdownTable, LabeledDropdown, ScrollScreen, DialogTable
from graphics import CircleWidget, RectangleWidget


class HistoricalFencingDrillsApp(MDApp):

    def __init__(self, **kwargs):
        super(HistoricalFencingDrillsApp, self).__init__(**kwargs)

        # placeholders for settings widgets
        self.mode_widget = None
        self.pct_widget = None
        self.total_time_widget = None
        self.call_wait_widget = None
        self.combo_wait_widget = None
        self.combo_repeat_widget = None
        self.combo_expand_widget = None
        self.min_combo_length_widget = None
        self.max_combo_length_widget = None
        self.transitions = None
        self.cut_box = None
        self.guard_box = None
        self.cut_transitions_box = None
        self.guard_transitions_box = None

        # placeholders for layouts
        self.screen3 = None
        self.screen_3_populated = False

        # Default settings
        self.current_settings_tab = 'General'
        self.current_about_tab = 'Swage'
        self.cuts = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        self.guards = ['H', 'rH', 'L', 'rL', 'M', 'rM', 'G', 'rG', 'T']
        self.cut_checkboxes = dict()
        self.guard_checkboxes = dict()
        self.settings = JsonStore('settings.json')
        self.transitions = JsonStore('transitions.json')
        self.weights = JsonStore('weights.json')
        self.weight_dict = dict()
        self.compile_weight_dict()

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
            on_tab_press=lambda x: self._switch_about_tabs(None, None, None, self.current_about_tab)
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

    def _create_pattern_generator(self):
        m, s = self.total_time_widget.widget.text.split(':')
        total_time = int(m) * 60 + int(s)
        min_size = int(self.min_combo_length_widget.widget.text)
        max_size = int(self.max_combo_length_widget.widget.text)

        randomized = ('Random', 'Return to Guard')
        if self.mode_widget.widget.text in randomized:
            transitions_dict = dict()
            for t, v in self.transitions.find():
                if not v['value']:
                    continue
                a, b = t.split('|')
                if a not in transitions_dict:
                    transitions_dict[a] = list()
                transitions_dict[a].append(b)

            transitions_set = set(transitions_dict.keys())
            transitions_dict = {k: list(transitions_set.intersection(v)) for k, v in transitions_dict.items()}
            transitions_set = list(transitions_set)

            def draw_from_options(options):
                weights = [self.weight_dict[o] for o in options]
                if max(weights) == 0.0:
                    weights = [1.0] * len(weights)

                return random.choices(options, weights=weights)[0]

            if self.mode_widget.widget.text == 'Random':
                def generator_function():
                    call = draw_from_options(transitions_set)
                    while True:
                        combo_length = random.randrange(min_size, max_size + 1)
                        call = draw_from_options(transitions_dict[call])
                        combo = [call]
                        while len(combo) < combo_length:
                            call = draw_from_options(transitions_dict[call])
                            combo.append(call)

                        yield combo
            elif self.mode_widget.widget.text == 'Return to Guard':
                def generator_function():
                    while True:
                        combo_length = random.randrange(min_size, max_size + 1)
                        call = draw_from_options(self.guards)
                        combo = [call]
                        while len(combo) < combo_length:
                            if (combo_length - len(combo)) == 1:
                                options = [c for c in transitions_dict[call] if c in self.guards]
                            else:
                                options = [c for c in transitions_dict[call] if c in self.cuts]
                            call = draw_from_options(options)
                            combo.append(call)

                        yield combo

        elif self.mode_widget.widget.text == 'Pre-programmed':
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

            def generator_function():
                yield random.choice(patterns)
        else:
            raise ValueError(
                'Valid values are `Pre-programmed`, `Random`, and `Return to Guard`.'
            )

        return generator_function

    def schedule_calls(self, *_, leading_n=10):
        m, s = self.total_time_widget.widget.text.split(':')
        total_time = int(m) * 60 + int(s) + leading_n
        for row in self._create_ready(leading_n):
            Clock.schedule_once(
                partial(
                    self._update_screen2,
                    row
                ),
                row[0]
            )
        prev_row = [leading_n + 1]
        # (i, call_length, time_string, call_text, call_list, call_sound
        for row in self._create_buffer(leading_n):
            if row[0] > total_time:
                break
            base_i_prev = math.floor(prev_row[0])
            base_i = math.floor(row[0])
            for base_i in range(base_i_prev + 1, base_i + 1):
                time_string = clock_time_from_seconds(total_time - base_i)
                filler_row = (
                    base_i,
                    row[0] - base_i,
                    time_string,
                    prev_row[3],
                    prev_row[4],
                    None
                )
                Clock.schedule_once(
                    partial(
                        self._update_screen2,
                        filler_row
                    ),
                    filler_row[0]
                )

            Clock.schedule_once(
                partial(
                    self._update_screen2,
                    row
                ),
                row[0]
            )
            prev_row = row

        final_row = (
            row[0] + 1,
            0,
            self.total_time_widget.widget.text,
            'READY',
            '',
            None
        )
        Clock.schedule_once(
            partial(
                self._update_screen2,
                final_row
            ),
            final_row[0]
        )

    def _create_ready(self, leading_n=10):
        for i in range(leading_n + 1):
            if i < leading_n:
                row = (i, None, self.total_time_widget.widget.text, 'READY', str(leading_n - i), None)
            else:
                row = (i, None, self.total_time_widget.widget.text, 'BEGIN', '', None)

            yield row

    def _create_buffer(self, leading_n=10):

        call_wait = float(self.call_wait_widget.widget.text)
        combo_wait = float(self.combo_wait_widget.widget.text)
        m, s = self.total_time_widget.widget.text.split(':')
        total_time = int(m) * 60 + int(s)
        combo_expand = self.combo_expand_widget.widget.text == 'ON'
        combo_repeat = self.combo_repeat_widget.widget.text == 'ON'

        pattern_generator = self._create_pattern_generator()

        sounds = {
            s: SoundLoader.load(f'assets/sounds/{s}.wav')
            for s in (self.cuts + self.guards)
        }

        i = leading_n + 1
        for pat in pattern_generator():

            start = 2 if combo_expand else len(pat)
            for end in range(start, len(pat) + 1):
                for call in range(end):
                    call_text = pat[call]
                    call_list = ' '.join(pat[:call + 1])
                    call_sound = sounds[call_text]
                    call_length = call_sound.length + call_wait
                    if i == (leading_n + 1):
                        time_string = clock_time_from_seconds(math.floor(total_time - 1))
                    else:
                        time_string = clock_time_from_seconds(math.floor(total_time))
                    row = (
                        i,
                        call_length,
                        time_string,
                        call_text,
                        call_list,
                        call_sound
                    )
                    i += call_length
                    total_time -= call_length
                    yield row

                i += combo_wait
                total_time -= combo_wait

            if combo_repeat:
                end = len(pat)
                for call in range(end):
                    call_text = pat[call]
                    call_list = ' '.join(pat[:call + 1])
                    call_sound = sounds[call_text]
                    call_length = call_sound.length + call_wait
                    time_string = clock_time_from_seconds(math.floor(total_time))
                    row = (
                        i,
                        call_length,
                        time_string,
                        call_text,
                        call_list,
                        call_sound
                    )
                    i += call_length
                    total_time -= call_length
                    yield row

                i += combo_wait
                total_time -= combo_wait

    def _create_screen_1(self):

        container = MDGridLayout(cols=1, padding=dp(10), spacing=dp(10))
        kwargs = dict(
            store=self.settings,
            value_key='value',
            width_mult=100,
            cols=1
        )

        mode_box = MDGridLayout(
            cols=2,
            rows=1,
            spacing=[dp(5), dp(0)]
        )

        self.mode_widget = LabeledDropdown(
            label='Mode:',
            options=[
                'Pre-programmed',
                'Random',
                'Return to Guard'
            ],
            size_hint=(0.8, 1.0),
            pos_hint={'center_x': .4, 'center_y': 0.5},
            **kwargs
        )
        self.mode_widget.widget.bind(text=self.validate_values)
        mode_box.add_widget(self.mode_widget)
        kwargs['width_mult'] = 2

        self.pct_widget = LabeledDropdown(
            label='% cuts:',
            options=[f"{v / 100:.0%}" for v in range(0, 105, 5)],
            size_hint=(0.2, 1.0),
            pos_hint={'center_x': .9, 'center_y': 0.5},
            **kwargs
        )
        self.pct_widget.widget.bind(text=self.validate_values)
        mode_box.add_widget(self.pct_widget)

        container.add_widget(mode_box)

        self.total_time_widget = LabeledDropdown(
            label='Drill duration:',
            options=[
                str(h).zfill(2) + flag
                for h in range(1, 20)
                for flag in (':00', ':30')
            ][:-1],
            **kwargs
        )
        container.add_widget(self.total_time_widget)

        pause_box = MDGridLayout(cols=2, rows=1, spacing=[dp(5), dp(0)])

        self.call_wait_widget = LabeledDropdown(
            label='Seconds after call:',
            options=['0.0', '0.1', '0.5', '1.0'],
            **kwargs
        )

        pause_box.add_widget(self.call_wait_widget)

        self.combo_wait_widget = LabeledDropdown(
            label='Seconds after combo:',
            options=['0.1', '0.5', '1.0', '2.0'],
            **kwargs
        )
        pause_box.add_widget(self.combo_wait_widget)

        container.add_widget(pause_box)

        length_box = MDGridLayout(cols=2, rows=1, spacing=[dp(5), dp(0)])

        self.min_combo_length_widget = LabeledDropdown(
            label='Minimum combo:',
            options=[str(v) for v in range(2, 11)],
            **kwargs
        )
        self.min_combo_length_widget.widget.bind(text=self.validate_values)
        length_box.add_widget(self.min_combo_length_widget)

        self.max_combo_length_widget = LabeledDropdown(
            label='Maximum combo:',
            options=[str(v) for v in range(2, 11)],
            **kwargs
        )
        self.max_combo_length_widget.widget.bind(text=self.validate_values)
        length_box.add_widget(self.max_combo_length_widget)

        container.add_widget(length_box)

        kwargs['width_mult'] = 100
        self.combo_repeat_widget = LabeledDropdown(
            label='Repeat full combo at end:',
            options=['OFF', 'ON'],
            **kwargs
        )
        container.add_widget(self.combo_repeat_widget)

        self.combo_expand_widget = LabeledDropdown(
            label='Progressively expand combos:',
            options=['OFF', 'ON'],
            **kwargs
        )
        container.add_widget(self.combo_expand_widget)

        self.settings_tabs = MDTabs(anim_duration=0.5)
        self.settings_tabs.bind(on_tab_switch=self._switch_settings_tabs)

        for tab_label in (
                'General',
                'Weights',
                'Transitions',
        ):
            tab = Tab(title=tab_label)
            if tab_label == 'General':
                tab.add_widget(container)
            elif tab_label == 'Weights':
                container = MDBoxLayout(orientation='vertical')
                self.cut_box = DropdownTable(
                    items=self.cuts,
                    options=[str(x) for x in range(6)],
                    store=self.weights,
                    shape=(3, 3),
                    value_key='value',
                    create_table=False
                )
                self.cut_box.bind(calls=self.compile_weight_dict)
                self.guard_box = DropdownTable(
                    items=self.guards,
                    options=[str(x) for x in range(6)],
                    store=self.weights,
                    shape=(3, 3),
                    value_key='value',
                    create_table=False
                )
                self.guard_box.bind(calls=self.compile_weight_dict)
                container.add_widget(self.cut_box)
                container.add_widget(MDSeparator())
                container.add_widget(self.guard_box)
                tab.add_widget(container)
            elif tab_label == 'Transitions':
                container = MDBoxLayout(orientation='vertical')
                self.cut_transitions_box = DialogTable(
                    items=self.cuts,
                    options=self.cuts + self.guards,
                    store=self.transitions,
                    shape=(3, 3),
                    value_key='value',
                    create_table=False
                )

                self.guard_transitions_box = DialogTable(
                    items=self.guards,
                    options=self.cuts + self.guards,
                    store=self.transitions,
                    shape=(3, 3),
                    value_key='value',
                    create_table=False
                )
                container.add_widget(self.cut_transitions_box)
                container.add_widget(MDSeparator())
                container.add_widget(self.guard_transitions_box)
                tab.add_widget(container)

            self.settings_tabs.add_widget(tab)
        self._disable_tabs()
        return self.settings_tabs

    def _create_screen_2(self):
        container = MDFloatLayout()
        with container.canvas:
            Color(0, 0, 0, 0.75)

            Rectangle(
                pos=(0, 0),
                size=(Window.width, Window.height)
            )

        self.time_label = MDLabel(
            text=self.total_time_widget.widget.text,
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

    def _create_screen_3(self, *_):
        container = MDFloatLayout()
        self.about_tabs = MDTabs()
        self.about_tabs.bind(on_tab_switch=self._switch_about_tabs)
        container.add_widget(self.about_tabs)

        for tab_label in (
                'Swage',
                'Cuts and Guards',
                'Settings'
        ):
            tab = Tab(title=tab_label)
            if tab_label == 'Swage':
                self.scroll_container1 = ScrollScreen(
                    item_list=[
                        {
                            '_pattern': 'text',
                            'text': 'Swage',
                            'markup': True,
                            'font_style': 'H3',
                            'halign': 'left'
                        },
                        {
                            '_pattern': 'textfile',
                            'text': 'assets/texts/paragraph1.txt',
                            'font_style': 'Body1',
                            'halign': 'left',
                            'markup': True
                        }
                    ],
                    do_scroll_x=False
                )
                tab.add_widget(self.scroll_container1)

            elif tab_label == 'Cuts and Guards':
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

                self.scroll_container2 = ScrollScreen(
                    item_list=[
                        {
                            '_pattern': 'textfile',
                            'text': 'assets/texts/paragraph2a.txt',
                            'font_style': 'Body1',
                            'halign': 'left',
                            'markup': True
                        },
                        {
                            '_pattern': 'imagecard',
                            'image_list': image_files,
                            'image_path': 'assets/images/'
                        },
                        {
                            '_pattern': 'textfile',
                            'text': 'assets/texts/paragraph2b.txt',
                            'font_style': 'Body1',
                            'halign': 'left',
                            'markup': True
                        },
                        {
                            '_pattern': 'image',
                            'source': 'assets/images/cut_and_thrust_abbreviations.png'
                        },
                    ],
                    do_scroll_x=False
                )
                tab.add_widget(self.scroll_container2)

            elif tab_label == 'Settings':
                self.scroll_container3 = ScrollScreen(
                    item_list=[
                        {
                            '_pattern': 'textfile',
                            'text': 'assets/texts/paragraph3.txt',
                            'font_style': 'Body1',
                            'halign': 'left',
                            'markup': True
                        }
                    ],
                    do_scroll_x=False
                )
                tab.add_widget(self.scroll_container3)

            self.about_tabs.add_widget(tab)
        return container

    def _update_screen2(self, row, _):
        call_time, call_length, time_text, call_text, full_call_text, play_sound = row
        self.time_label.text = time_text
        self.call_label.text = call_text
        self.full_call_label.text = full_call_text

        if call_text == 'READY':
            self.call_diagram.pointer_position_code = None
            self.call_diagram.update_lines()
            self.call_pointer.pointer_position_code = None
            self.call_pointer.update_circle()
        elif play_sound:
            self.call_diagram.pointer_position_code = call_text
            self.call_diagram.update_lines()
            self.call_pointer.pointer_position_code = call_text
            self.call_pointer.update_circle()

            play_sound.play()

    def _switch_settings_tabs(self, tabs, tab, label, tab_text):

        self.current_settings_tab = tab_text

        if tab_text == 'Weights':
            if not self.cut_box.table_populated:
                Clock.schedule_once(lambda dt: self.cut_box.append_table(), 0.5)
            if not self.guard_box.table_populated:
                Clock.schedule_once(lambda dt: self.guard_box.append_table(), 0.5)

        if tab_text == 'Transitions':
            if not self.cut_transitions_box.table_populated:
                Clock.schedule_once(lambda dt: self.cut_transitions_box.append_table(), 0.5)
            if not self.guard_transitions_box.table_populated:
                Clock.schedule_once(lambda dt: self.guard_transitions_box.append_table(), 0.5)

    def _switch_about_tabs(self, tabs, tab, label, tab_text):

        self.cancel_all_events()
        self.current_about_tab = tab_text
        if tab_text == 'Swage':
            if not self.scroll_container1.screen_populated:
                Clock.schedule_once(lambda df: self.scroll_container1.fill_container(), 0.5)
        if tab_text == 'Cuts and Guards':
            if not self.scroll_container2.screen_populated:
                Clock.schedule_once(lambda df: self.scroll_container2.fill_container(), 0.5)
        if tab_text == 'Settings':
            if not self.scroll_container3.screen_populated:
                Clock.schedule_once(lambda df: self.scroll_container3.fill_container(), 0.5)

    def compile_weight_dict(self, *_):

        self.weight_dict = dict()
        cut_pct = float(self.settings.get("% cuts:")['value'].strip('%')) / 100
        for k, d in self.weights.find():
            v = int(d['value'])
            if k in self.cuts:
                self.weight_dict[k] = v * cut_pct
            elif k in self.guards:
                self.weight_dict[k] = v * (1.0 - cut_pct)

    def _disable_tabs(self):
        manual_options = ('Random', 'Return to Guard')
        flag = self.mode_widget.widget.text not in manual_options
        for tab in self.settings_tabs.get_slides():
            if tab.title != 'General':
                tab.tab_label.disabled_color = [0.0, 0.0, 0.0, 0.1]
                tab.tab_label.disabled = flag
                tab.disabled = flag

        if self.mode_widget.widget.text == 'Random':
            self.pct_widget.widget.disabled = False
        else:
            self.pct_widget.widget.disabled = True

    def validate_values(self, widget, text):

        if widget == self.min_combo_length_widget.widget:
            a = self.min_combo_length_widget.widget.text
            b = self.max_combo_length_widget.widget.text
            if int(a) > int(b):
                self.max_combo_length_widget.widget.set_item(a)

        if widget == self.max_combo_length_widget.widget:
            a = self.min_combo_length_widget.widget.text
            b = self.max_combo_length_widget.widget.text
            if int(b) < int(a):
                self.min_combo_length_widget.widget.set_item(b)

        if widget == self.mode_widget.widget:
            self._disable_tabs()

        if widget == self.pct_widget.widget:
            self.compile_weight_dict()

    def change_value(self, _, text):
        self.call_diagram.pointer_position_code = text
        self.call_diagram.update_lines()

    def cancel_all_events(self, *_):
        for event in Clock.get_events():
            event.cancel()
        self.time_label.text = self.total_time_widget.widget.text
        self.call_label.text = 'READY'
        self.full_call_label.text = ''
        self.call_diagram.pointer_position_code = None
        self.call_pointer.pointer_position_code = None
        self.call_diagram.update_lines()
        self.call_pointer.update_circle()


if __name__ == '__main__':

    # Window.size = (720 / 2, 1280 / 2)
    HistoricalFencingDrillsApp().run()
