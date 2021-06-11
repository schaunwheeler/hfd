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
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, Line, Ellipse

from kivymd.uix.toolbar import MDToolbar
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel


class CircleWidget(Widget):
    def __init__(self, **kwargs):
        super(CircleWidget, self).__init__(**kwargs)

        self.pointer_position_code = '9'

        with self.canvas:
            Color(240, 255, 0, 1)
            self.circle = Ellipse(
                pos=self.center,
                size=(self.width * 0.05, self.height * 0.05)
            )

        self.bind(pos=self.update_circle, size=self.update_circle)

    def calculate_coordinates(self, code=None):
        center_x, center_y = self.center
        x = self.width / 2
        y = self.height / 2
        part_x = x * 0.66
        part_y = y * 0.66

        offset = min(self.width * 0.05, self.height * 0.05)

        if self.pointer_position_code is None:
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
        elif self.pointer_position_code == '1t':
            return center_x + part_x - offset, center_y + part_y - offset
        elif self.pointer_position_code == '2t':
            return center_x - part_x - offset, center_y + part_y - offset
        elif self.pointer_position_code == '3t':
            return center_x + part_x - offset, center_y - part_y - offset
        elif self.pointer_position_code == '4t':
            return center_x - part_x - offset, center_y - part_y - offset
        elif self.pointer_position_code == '5t':
            return center_x + part_x - offset, center_y - offset
        elif self.pointer_position_code == '6t':
            return center_x - part_x - offset, center_y - offset
        elif self.pointer_position_code == '7t':
            return center_x - offset, center_y + part_y - offset
        elif self.pointer_position_code == '8t':
            return center_x - offset, center_y - part_y - offset

    def update_circle(self, *args):
        offset = min(self.width * 0.05, self.height * 0.05)
        self.circle.pos = self.calculate_coordinates(code=self.pointer_position_code)

        if self.pointer_position_code is None:
            self.circle.size = (0, 0)
        else:
            self.circle.size = (offset * 2, offset * 2)


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

        self.bind(pos=self.update_rect, size=self.update_rect)
        self.bind(pos=self.update_lines, size=self.update_lines)

    def update_rect(self, *args):
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

    def update_lines(self, *args):
        self.line_1_4_color.rgba = (1, 1, 1, 0.9)
        self.line_2_3_color.rgba = (1, 1, 1, 0.9)
        self.line_5_6_color.rgba = (1, 1, 1, 0.9)
        self.line_7_8_color.rgba = (1, 1, 1, 0.9)

        self.line_1_4.width = 2
        self.line_2_3.width = 2
        self.line_5_6.width = 2
        self.line_7_8.width = 2

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
        else:
            pass


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
            icon='sword',
            on_tab_press=self.schedule_calls
        )
        bottom_navigation_item3 = MDBottomNavigationItem(
            name='screen 3',
            text='Help',
            icon='book',
            on_tab_press=self.cancel_all_events,
            on_tab_release=self.set_dims
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

    def _update_circle(self, value, nap):
        self.call_pointer.pointer_position_code = value
        self.call_pointer.update_circle()

    def _update_screen2(self, row, nap):
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
            self.total_time_widget.text,
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
            size_hint=(1, None),
            size=(Window.width, Window.height - 250)
        )

        self.container = MDGridLayout(
            cols=1, spacing=30,
            size_hint_y=None, size_hint_x=None,
            height=4200, width=Window.width
        )
        self.container.bind(minimum_height=self.container.setter('height'))

        self.paragraph1 = MDLabel(
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
            size_hint_x=None,
            width=self.container.width
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

        self.paragraph2 = MDLabel(
            text=(
                "This app adapts those cutting diagrams to provide audio "
                "callouts of cut and thrust combinations to serve for individual "
                "training. The app assumes a simplified system of eight cuts and "
                "9 thrusts. The cuts are illustrated here, witih the cut begining "
                "at the position of its respective number and continuing along the "
                "line that extends from that number. This differs from the user "
                "interface, where the yellow dot marks where the cut should end."
            ),
            halign='center',
            font_style='Body1',
            size_hint_y=None,
            size_hint_x=None,
            width=self.container.width
        )

        self.image2 = Image(
            source='assets/images/Cut patterns.png',
            allow_stretch=True,
            keep_ratio=True,
            size_hint_y=None,
            size_hint_x=None,
            width=self.container.width,
            height=self.container.width
        )

        self.paragraph3 = MDLabel(
            text=(
                "The thrusts are illustrated here. In most cases, they "
                "are called out by the same number as their corresponding "
                "cut, with the word 'thrust' afterwards. The once exception "
                "is the '9', which is a thrust to the center of the body."
            ),
            halign='center',
            font_style='Body1',
            size_hint_y=None,
            size_hint_x=None,
            width=self.container.width
        )

        self.image3 = Image(
            source='assets/images/Thrust patterns.png',
            allow_stretch=True,
            keep_ratio=True,
            size_hint_y=None,
            size_hint_x=None,
            width=self.container.width,
            height=self.container.width
        )

        self.paragraph4 = MDLabel(
            text=(
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
            halign='center',
            font_style='Body1',
            size_hint_y=None,
            size_hint_x=None,
            width=self.container.width
        )

        self.container.add_widget(self.paragraph1)
        self.container.add_widget(self.image1)
        self.container.add_widget(self.paragraph2)
        self.container.add_widget(self.image2)
        self.container.add_widget(self.paragraph3)
        self.container.add_widget(self.image3)
        self.container.add_widget(self.paragraph4)

        self.scroll_container.add_widget(self.container)
        Window.bind(width=self.set_dims, height=self.set_dims)

        return self.scroll_container

    def set_dims(self, *args):
        width = self.scroll_container.width
        adjusted_width = width #  * 0.66
        self.image1.width = adjusted_width
        self.image1.height = adjusted_width / self.image1.image_ratio
        self.image2.width = adjusted_width
        self.image2.height = adjusted_width / self.image2.image_ratio
        self.image3.width = adjusted_width
        self.image3.height = adjusted_width / self.image3.image_ratio
        self.paragraph1.width = width
        self.paragraph2.width = width
        self.paragraph3.width = width
        self.paragraph4.width = width
        self.paragraph1.height = self.paragraph1.texture_size[1]
        self.paragraph2.height = self.paragraph2.texture_size[1]
        self.paragraph3.height = self.paragraph3.texture_size[1]
        self.paragraph4.height = self.paragraph4.texture_size[1]
        new_height = self.image1.height + self.image2.height + self.image3.height
        new_height += (
                self.paragraph1.height + self.paragraph2.height +
                self.paragraph3.height + self.paragraph4.height
        )

        self.container.height = new_height + 100
        self.container.width = width

    def cancel_all_events(self, *args):
        for event in Clock.get_events():
            event.cancel()
        self.time_label.text = self.total_time_widget.text
        self.call_label.text = 'READY'
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