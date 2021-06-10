import random
import math
from functools import partial

from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.spinner import Spinner
from kivy.core.audio import SoundLoader

from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

from kivymd.uix.toolbar import MDToolbar
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDRoundFlatIconButton
from kivymd.uix.label import MDLabel


class HistoricalFencingDrillsApp(MDApp):

    def __init__(self, **kwargs):
        super(HistoricalFencingDrillsApp, self).__init__(**kwargs)
        self.total_time_widget = None
        self.call_wait_widget = None
        self.combo_wait_widget = None
        self.combo_repeat_widget = None
        self.combo_expand_widget = None

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
        toolbar = MDToolbar(
            title='Historical Fencing Drills',
            anchor_title='center'
        )
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
            icon='sword'
        )
        bottom_navigation_item3 = MDBottomNavigationItem(
            name='screen 3',
            text='Help',
            icon='book',
            on_tab_press=self.cancel_all_events,
            height=Window.height
        )
        parent.add_widget(toolbar)

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

    def schedule_calls(self, event):
        for row in self._create_buffer():
            Clock.schedule_once(
                partial(
                    self._update_screen2,
                    row
                ),
                row[0]
            )

    @staticmethod
    def _get_patterns():

        with open('assets/combos.txt', 'r') as f:
            patterns = [line.strip().split(' ') for line in f.readlines()]

        random.shuffle(patterns)

        return patterns

    def _update_screen2(self, row, nap):
        _, time_text, call_text, full_call_text, play_sound = row
        self.time_label.text = time_text
        self.call_label.text = call_text
        self.full_call_label.text = full_call_text

        if play_sound:
            play_sound.play()

    def _create_buffer(self):
        call_wait = convert_value(self.call_wait_widget.text)
        combo_wait = convert_value(self.combo_wait_widget.text)
        total_time = convert_value(self.total_time_widget.text)
        combo_expand = convert_value(self.combo_expand_widget.text)
        combo_repeat = convert_value(self.combo_repeat_widget.text)

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

                row = (i, f'Time: {self.total_time_widget.text}', str(10 - i), '', None)
                buffer.append(row)
                time_left -= 1
                i += 1
            elif i == 10:
                time_string = clock_time_from_seconds(round(time_left))
                row = (i, f'Time: {time_string}', 'BEGIN', '', None)
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
                        row = (i, f'Time: {time_string}', call_text, call_list, call_sound)
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
                        row = (i, f'Time: {time_string}', call_text, call_list, call_sound)
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
                new_row = (j, f'Time: {time_string}') + prev_row[2:-1] + (None, )
                buffer.append(new_row)
                j += 1
            prev_row = row

        buffer = sorted(buffer, key=lambda t: t[0])
        buffer.append((
            total_time + 11,
            f'Time: {self.total_time_widget.text}',
            'READY',
            '',
            None
        ))

        return buffer

    def _create_screen_1(self):

        container = MDGridLayout(
            cols=2
        )

        title = MDLabel(text='Round duration (minutes):', font_style='H5')
        self.total_time_widget = Spinner(
            text='03:00',
            values=[str(h).zfill(2) + ':00' for h in range(1, 20)],
            size_hint=(0.25, 0.2),
            pos_hint={'center_x': .0, 'center_y': .0}
        )
        container.add_widget(title)
        container.add_widget(self.total_time_widget)

        title = MDLabel(text='Pause between calls (seconds):', font_style='H5')
        self.call_wait_widget = Spinner(
            text='0.5',
            values=[str(x / 100) for x in range(5, 205, 5)],
            size_hint=(0.25, 0.2),
            pos_hint={'center_x': .0, 'center_y': .0}
        )
        container.add_widget(title)
        container.add_widget(self.call_wait_widget)

        title = MDLabel(text='Pause between combos (seconds):', font_style='H5')
        self.combo_wait_widget = Spinner(
            text='1.0',
            values=[str(x / 100) for x in range(5, 205, 5)],
            size_hint=(0.25, 0.2),
            pos_hint={'center_x': .0, 'center_y': .0}
        )
        container.add_widget(title)
        container.add_widget(self.combo_wait_widget)

        title = MDLabel(text='Repeat full combo at end:', font_style='H5')
        self.combo_repeat_widget = Spinner(
            text='1',
            values=[str(x) for x in range(11)],
            size_hint=(0.25, 0.2),
            pos_hint={'center_x': .0, 'center_y': .0}
        )
        container.add_widget(title)
        container.add_widget(self.combo_repeat_widget)

        title = MDLabel(text='Progressively expand combos:', font_style='H5')
        self.combo_expand_widget = Spinner(
            text='ON',
            values=['OFF', 'ON'],
            size_hint=(0.25, 0.2),
            pos_hint={'center_x': .0, 'center_y': .0}
        )
        container.add_widget(title)
        container.add_widget(self.combo_expand_widget)

        return container

    def _create_screen_2(self):
        container = MDBoxLayout(orientation='vertical')
        self.time_label = MDLabel(
            text=f'Time: {self.total_time_widget.text}',
            halign='center',
            font_style='H2'
        )
        self.call_label = MDLabel(
            text='Ready',
            halign='center',
            font_style='H1'
        )
        self.full_call_label = MDLabel(
            text='',
            halign='center',
            font_style='H3'
        )

        start_button = MDRoundFlatIconButton(
            text='Begin',
            icon='play',
            size_hint=(None, None),
            pos_hint={'center_x': .5, 'center_y': .5},
            on_press=self.schedule_calls
        )

        container.add_widget(self.time_label)
        container.add_widget(self.call_label)
        container.add_widget(self.full_call_label)
        container.add_widget(start_button)
        container.add_widget(MDLabel(text='', height=50))

        return container

    @staticmethod
    def _create_screen_3():

        container = MDGridLayout(cols=1, spacing=10, size_hint_y=None, height=4000)

        paragraph1 = MDLabel(
            text=(
                "\n"
                "In the 1560s, Joachim Meyer created a manuscript "
                "for one of his private students, providing instruction "
                "in longsword, dussack, and side sword. It had much in "
                "common with a Meyer's 1570 publication, Gründtliche "
                "Beschreibung der Kunst des Fechtens. Although the later "
                "publication was more extensive, the early manuscript "
                "contained several cutting diagrams that can serve as useful drills."
                "\n"
            ),
            halign='left',
            font_style='Body1',
            size_hint_y=None,
            height=300
        )

        image1 = Image(
            source='assets/images/meyer_ms.jpg',
            size_hint_y=None,
            height=600
        )

        paragraph2 = MDLabel(
            text=(
                "\n"
                "This app adapts those cutting diagrams to provide audio "
                "callouts of cut and thrust combinations to serve for individual "
                "training. The app assumes a simplified system of eight cuts and "
                "9 thrusts. The cuts are illustrated here, witih the cut begining "
                "at the position of its respective number and continuing along the "
                "line that extends from that number."
                "\n"
            ),
            halign='left',
            font_style='Body1',
            size_hint_y=None,
            height=300
        )

        image2 = Image(
            source='assets/images/Cut patterns.png',
            size_hint_y=None,
            height=600
        )

        paragraph3 = MDLabel(
            text=(
                "\n"
                "The thrusts are illustrated here. In most cases, they "
                "are called out by the same number as their corresponding "
                "cut, with the word 'thrust' afterwards. The once exception "
                "is the '9', which is a thrust to the center of the body."
                "\n"
            ),
            halign='left',
            font_style='Body1',
            size_hint_y=None,
            height=300
        )

        image3 = Image(
            source='assets/images/Thrust patterns.png',
            size_hint_y=None,
            height=600
        )

        paragraph4 = MDLabel(
            text=(
                "\n\n\n\n\n\n"
                "The app provides multiple ways to adjust the training program:\n\n"
                "   \u2022 [b]Round duration (minutes):[/b] the amount of time "
                "you want to train for.\n\n"
                "   \u2022 [b]Pause between calls (seconds):[/b] the number of seconds "
                "to wait calling out the next cut or thrust.\n\n"
                "   \u2022 [b]Pause between combos (seconds):[/b] the number of seconds "
                "to wait after a combination of multiple cuts and/or thrusts have been called out.\n\n"
                "   \u2022 [b]Progressively expand combos:[/b] if ON, the app will "
                " start by calling out hte first two moves of the combo, then expand to "
                " three, then four, and so on, until the full combo is recited.\n\n"
                "   \u2022 [b]Repeat full combo at end:[/b] the number of times to repeat "
                "the combo before moving on to the next one. If progressive expansion is on, "
                "then the repetition will only apply to the full combo, not each progressive subset.\n\n"
            ),
            markup=True,
            halign='left',
            font_style='Body1',
            size_hint_y=None,
            height=600
        )

        container.add_widget(paragraph1)
        container.add_widget(image1)
        container.add_widget(paragraph2)
        container.add_widget(image2)
        container.add_widget(paragraph3)
        container.add_widget(image3)
        container.add_widget(paragraph4)

        scroll_container = ScrollView(
            size_hint=(1, None),
            size=(Window.width, Window.height - 250)
        )
        scroll_container.add_widget(container)

        return scroll_container

    def cancel_all_events(self, event):
        for event in Clock.get_events():
            event.cancel()
        self.time_label.text = 'Time: 00:00'
        self.call_label.text = 'Ready'
        self.full_call_label.text = ''


def convert_value(v):
    if ':' in v:
        m, s = v.split(':')
        return int(m) * 60 + int(s)
    elif '.' in v:
        return float(v)
    elif v.isnumeric():
        return int(v)
    else:
        return True if (v == 'ON') else False


def clock_time_from_seconds(seconds):
    m, s = divmod(seconds, 60)
    return f'{m:02d}:{s:02d}'


if __name__ == '__main__':
    HistoricalFencingDrillsApp().run()
