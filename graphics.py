from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, Line, Ellipse


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
