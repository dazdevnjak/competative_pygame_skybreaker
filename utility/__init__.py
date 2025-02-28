import pygame
import math

from entities.components import *

KEYBOARD_PLAYER_ONE_CONTROLS = [
    pygame.K_w,
    pygame.K_a,
    pygame.K_s,
    pygame.K_d,  # MoveVelocity
    pygame.K_g,
    pygame.K_h,  # AimVelocity
    pygame.K_SPACE,  # FireButton
    pygame.K_t,  # SkipButton
]
KEYBOARD_PLAYER_TWO_CONTROLS = [
    pygame.K_UP,
    pygame.K_LEFT,
    pygame.K_DOWN,
    pygame.K_RIGHT,  # MoveVelocity
    pygame.K_KP1,
    pygame.K_KP2,  # AimVelocity
    pygame.K_RCTRL,  # FireButton
    pygame.K_KP3,  # SkipButton
]
JOYSTICK_PLAYER_CONTROLS = [
    0,
    1,  # MoveVelocity
    2,
    3,  # AimVelocity
    [5, 10],  # FireButton
    1,  # SkipButton
]


class Executor:
    class ExecState:
        def __init__(self, time: float, method, condition=None) -> None:
            self.__method = method
            self.__condition = condition
            self.__time = time
            self.__timer = pygame.time.get_ticks()
            pass

        def reset_timer(self) -> None:
            self.__timer = pygame.time.get_ticks()

        def update(self, current) -> bool:
            if self.__condition is not None:
                return (current - self.__timer) >= self.__time and self.__condition()
            return (current - self.__timer) >= self.__time

        def invoke(self) -> None:
            self.__method()

    one_time_method = []
    repeat_method = []

    @staticmethod
    def init():
        for exec_state in Executor.one_time_method:
            exec_state.reset_timer()
        for exec_state in Executor.repeat_method:
            exec_state.reset_timer()
        pass

    @staticmethod
    def reset():
        Executor.one_time_method.clear()
        Executor.repeat_method.clear()
        pass

    @staticmethod
    def wait(time: float, method, condition=None):
        Executor.one_time_method.append(Executor.ExecState(time, method, condition))
        pass

    @staticmethod
    def repeat(time: float, method, condition=None):
        Executor.repeat_method.append(Executor.ExecState(time, method, condition))
        pass

    @staticmethod
    def remove(method):
        # TODO : Add removing repeat_method
        pass

    @staticmethod
    def update():
        current = pygame.time.get_ticks()
        for exec_state in Executor.one_time_method[:]:
            if exec_state.update(current):
                exec_state.invoke()
                Executor.one_time_method.remove(exec_state)

        for exec_state in Executor.repeat_method:
            if exec_state.update(current):
                exec_state.invoke()
                exec_state.reset_timer()
        pass


class GameState:
    previous_time: float = 0.0
    current_time: float = 0.0
    delta_time: float = 0.0

    player_one = None
    player_two = None

    enemy = None

    surface = None
    screen = None

    window_width = None
    window_height = None
    
    is_tutorial = False

    def __init__(self, _screen, _surface) -> None:
        self.surface = _surface
        self.screen = _screen
        pass

    def reset(self, time: tuple[float, float, float]) -> None:
        self.previous_time = time[0]
        self.current_time = time[1]
        self.delta_time = time[2]

        pass


class Input:
    __current_keys = None
    __previous_keys = None

    __joysticks = []
    __current_joystick_buttons = None
    __previous_joystick_buttons = None
    __joystick_axes = None

    @staticmethod
    def init():
        pygame.joystick.init()
        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            Input.__joysticks.append(joystick)

        Input.__current_joystick_buttons = [None] * len(Input.__joysticks)
        Input.__previous_joystick_buttons = [None] * len(Input.__joysticks)
        for i in range(len(Input.__joysticks)):
            Input.__current_joystick_buttons[i] = [False] * Input.__joysticks[
                i
            ].get_numbuttons()
            Input.__previous_joystick_buttons[i] = [False] * Input.__joysticks[
                i
            ].get_numbuttons()

        Input.__joystick_axes = [None] * len(Input.__joysticks)
        for i in range(len(Input.__joysticks)):
            Input.__joystick_axes[i] = [0.0] * Input.__joysticks[i].get_numaxes()
        pass

    @staticmethod
    def update():
        Input.__previous_keys = Input.__current_keys
        Input.__current_keys = pygame.key.get_pressed()

        for i, joystick in enumerate(Input.__joysticks):
            Input.__previous_joystick_buttons[i] = Input.__current_joystick_buttons[i][
                :
            ]

            Input.__current_joystick_buttons[i] = [
                joystick.get_button(j) for j in range(joystick.get_numbuttons())
            ]

            Input.__joystick_axes[i] = [
                joystick.get_axis(a) for a in range(joystick.get_numaxes())
            ]

    @staticmethod
    def is_key_pressed(key: int):
        return Input.__current_keys[key] and not Input.__previous_keys[key]

    @staticmethod
    def is_key_released(key: int):
        return not Input.__current_keys[key] and Input.__previous_keys[key]

    @staticmethod
    def is_key_hold(key: int):
        return Input.__current_keys[key]

    @staticmethod
    def is_joystick_connected(joystick_index):
        return 0 <= joystick_index < len(Input.__joysticks)

    @staticmethod
    def is_joystick_button_pressed(joystick_index, button):
        if 0 <= joystick_index < len(Input.__joysticks):
            return (
                Input.__current_joystick_buttons[joystick_index][button]
                and not Input.__previous_joystick_buttons[joystick_index][button]
            )
        return False

    @staticmethod
    def is_joystick_button_released(joystick_index, button):
        if 0 <= joystick_index < len(Input.__joysticks):
            return (
                not Input.__current_joystick_buttons[joystick_index][button]
                and Input.__previous_joystick_buttons[joystick_index][button]
            )
        return False

    @staticmethod
    def is_joystick_button_hold(joystick_index, button):
        if 0 <= joystick_index < len(Input.__joysticks):
            return Input.__current_joystick_buttons[joystick_index][button]
        return False

    @staticmethod
    def get_joystick_axis(joystick_index, axis):
        if 0 <= joystick_index < len(Input.__joysticks) and 0 <= axis < len(
            Input.__joystick_axes[joystick_index]
        ):
            return Input.__joystick_axes[joystick_index][axis]
        return 0.0


def get_velocity(controls, joystick_index):
    move_velocity = [0.0, 0.0]
    aim_velocity = 0

    if not Input.is_joystick_connected(joystick_index):
        if Input.is_key_hold(controls[0]):
            move_velocity[1] -= 1
        if Input.is_key_hold(controls[1]):
            move_velocity[0] -= 0.7
        if Input.is_key_hold(controls[2]):
            move_velocity[1] += 1
        if Input.is_key_hold(controls[3]):
            move_velocity[0] += 1

        if Input.is_key_hold(controls[4]):
            aim_velocity = -5
        if Input.is_key_hold(controls[5]):
            aim_velocity = 5
    else:
        move_velocity[0] = Input.get_joystick_axis(
            joystick_index, JOYSTICK_PLAYER_CONTROLS[0]
        )
        move_velocity[1] = Input.get_joystick_axis(
            joystick_index, JOYSTICK_PLAYER_CONTROLS[1]
        )

        x_axis = Input.get_joystick_axis(joystick_index, JOYSTICK_PLAYER_CONTROLS[2])
        y_axis = Input.get_joystick_axis(joystick_index, JOYSTICK_PLAYER_CONTROLS[3])
        angle_rad = math.atan2(-y_axis, x_axis)
        angle_deg = math.degrees(angle_rad)

        if x_axis > 0.2 or x_axis < -0.2 or y_axis > 0.2 or y_axis < -0.2:
            aim_velocity = -angle_deg

    return move_velocity, aim_velocity


class ControllableObject:
    position: list[int] = None
    size: tuple[int, int] = None

    speed: float = 0
    max_speed: float = 0

    acceleration: float = 0
    friction: float = 0

    velocity: list[int]

    health: int = 100

    is_player: bool
    lives_left: int

    def __init__(self, _position, is_player, lives_left, _size=(128, 72)) -> None:
        self.components: list[Component] = []

        self.is_player = is_player

        self.position = list(_position)
        self.size = _size
        self.lives_left = lives_left

        self.speed = 0.2
        self.max_speed = 2

        self.acceleration = 0.05
        self.friction = 0.02

        self.velocity = [0, 0]
        self.hitbox_rect = pygame.Rect(
            self.position[0] + self.size[0] / 4.0,
            self.position[1] + self.size[1] / 4.0,
            self.size[0] / 2.0,
            self.size[1] / 2.0,
        )

        self.add_component(AimIndicator)
        self.add_component(HealthBarUI)

        self.health = 100
        pass

    @staticmethod
    def create_instance(cls_type, *args, **kwargs):
        return cls_type(*args, **kwargs)

    def add_component(self, component_type: type):
        component = ControllableObject.create_instance(component_type)
        component.on_load(self)
        self.components.append(component)
        return component

    def get_component(self, component_type: type):
        for component in self.components:
            if isinstance(component, component_type):
                return component
        return None

    def remove_component(self, component_type: type) -> bool:
        for component in self.components:
            if isinstance(component, component_type):
                self.components.remove(component)
                return True
        return False

    def update(self, state):
        for component in self.components:
            component.on_update(state, self)

        for i in range(2):
            if self.velocity[i] > 0:
                self.velocity[i] = max(0, self.velocity[i] - self.friction)
            elif self.velocity[i] < 0:
                self.velocity[i] = min(0, self.velocity[i] + self.friction)

        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]

        self.hitbox_rect.x = self.position[0] + self.size[0] / 4.0
        self.hitbox_rect.y = self.position[1] + self.size[1] / 4.0
        pass

    def render(self, state):
        # Render Hitbox TODO : Skloni ovo kasnije
        # pygame.draw.rect(screen, (255, 0, 0, 64), self.hitbox_rect)
        for component in self.components:
            component.on_render(state, self)
        pass

    def move(self, dx, dy):
        if dx != 0:
            self.velocity[0] += dx * self.acceleration
            self.velocity[0] = max(
                -self.max_speed, min(self.velocity[0], self.max_speed)
            )
        if dy != 0:
            self.velocity[1] += dy * self.acceleration
            self.velocity[1] = max(
                -self.max_speed, min(self.velocity[1], self.max_speed)
            )
        pass

    def check_edges(self, width, height):
        offset_x, offset_y = 50, 30
        if self.position[0] + (self.size[0] / 2) + offset_x > width:
            self.position[0] = width - (self.size[0] / 2) - offset_x
        elif self.position[0] + (self.size[0] / 2) - offset_x < 0:
            self.position[0] = 0 - (self.size[0] / 2) + offset_x
        if self.position[1] + (self.size[1] / 2) + offset_y > height:
            self.position[1] = height - (self.size[1] / 2) - offset_y
        elif self.position[1] + (self.size[1] / 2) - offset_y < 0:
            self.position[1] = 0 - (self.size[1] / 2) + offset_y

    def check_other_player_edges(self, other_player):
        self_center = pygame.Vector2(
            self.position[0] + self.size[0] / 2, self.position[1] + self.size[1] / 2
        )
        other_center = pygame.Vector2(
            other_player.position[0] + other_player.size[0] / 2,
            other_player.position[1] + other_player.size[1] / 2,
        )
        distance = self_center.distance_to(other_center)
        self_radius = min(self.size) / 2
        other_radius = min(other_player.size) / 2
        min_distance = self_radius + other_radius
        if distance < min_distance:
            overlap = min_distance - distance
            if distance == 0:
                direction = pygame.Vector2(1, 0)
            else:
                direction = (self_center - other_center).normalize()
            self.position[0] += direction.x * (overlap / 2)
            self.position[1] += direction.y * (overlap / 2)
            other_player.position[0] -= direction.x * (overlap / 2)
            other_player.position[1] -= direction.y * (overlap / 2)

    def check_intersection(self, other: pygame.Rect) -> bool:
        if other is None:
            return False
        return self.hitbox_rect.colliderect(other)


class Button:
    BUTTON_HOVER_SOUND = "Button hover"

    def __init__(
        self,
        x,
        y,
        width,
        height,
        text="",
        font_size=30,
        font_color=(0, 0, 0),
        button_color=(209, 179, 128),
        stroke_color=(97, 78, 6), 
        hover_color=(94, 209, 255),
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_size = font_size
        self.font_color = font_color
        self.button_color = button_color
        self.stroke_color = stroke_color
        self.hover_color = hover_color
        self.is_hovered = False
        self.was_hovered = False

        self.font = pygame.font.SysFont('calibri', self.font_size)
        self.text_surface = self.font.render(self.text, False, self.font_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def draw(self, screen):
        if self.was_hovered != self.is_hovered:
            if self.is_hovered:
                self.on_hover()
            self.was_hovered = self.is_hovered

        if self.is_hovered:
            pygame.draw.rect(screen, self.stroke_color, pygame.Rect(self.rect.x - 2, self.rect.y - 2, self.rect.width + 4, self.rect.height + 4))
            pygame.draw.rect(screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen, self.stroke_color, pygame.Rect(self.rect.x - 2, self.rect.y - 2, self.rect.width + 4, self.rect.height + 4))
            pygame.draw.rect(screen, self.button_color, self.rect)
        screen.blit(self.text_surface, self.text_rect)

    def on_hover(self):
        SoundSystem.play_sound(Button.BUTTON_HOVER_SOUND)
        pass

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False


class SoundSystem:
    sounds = {}
    overlapping_sounds = {}
    background_music = None
    music_volume = 0.5
    sound_volume = 0.5

    @staticmethod
    def Init():
        pygame.mixer.init()
        SoundSystem.sounds = {}
        SoundSystem.overlapping_sounds = {}
        SoundSystem.background_music = None
        SoundSystem.music_volume = 0.5
        SoundSystem.sound_volume = 0.5
        pygame.mixer.set_num_channels(32)

    @staticmethod
    def load_sound(name, file_path):
        try:
            sound = pygame.mixer.Sound(file_path)
            sound.set_volume(SoundSystem.sound_volume)
            SoundSystem.sounds[name] = sound
        except pygame.error as e:
            print(f"Error loading sound '{file_path}': {e}")

    @staticmethod
    def load_all_sounds(data: dict[str, str]):
        SoundSystem.sounds.clear()
        SoundSystem.overlapping_sounds.clear()
        for name, path in data.items():
            SoundSystem.load_sound(name, path)

    @staticmethod
    def play_sound(name, loops=0):
        if name in SoundSystem.sounds:
            sound = SoundSystem.sounds[name]
            channel = pygame.mixer.find_channel()
            if channel is None:
                print("No available channels to play the sound.")
                return

            is_playing = False
            num_channels = pygame.mixer.get_num_channels()
            for i in range(num_channels):
                ch = pygame.mixer.Channel(i)
                if ch.get_sound() == sound and ch.get_busy():
                    is_playing = True
                    break

            if is_playing:
                channel.play(sound, loops=loops)
                if name not in SoundSystem.overlapping_sounds:
                    SoundSystem.overlapping_sounds[name] = []
                SoundSystem.overlapping_sounds[name].append(channel)
            else:
                channel.play(sound, loops=loops)
        else:
            print(f"Sound '{name}' not found!")

    @staticmethod
    def stop_sound(name):
        if name in SoundSystem.sounds:
            sound = SoundSystem.sounds[name]
            num_channels = pygame.mixer.get_num_channels()
            for i in range(num_channels):
                ch = pygame.mixer.Channel(i)
                if ch.get_sound() == sound:
                    ch.stop()

        if name in SoundSystem.overlapping_sounds:
            for channel in SoundSystem.overlapping_sounds[name]:
                channel.stop()
            SoundSystem.overlapping_sounds[name].clear()

    @staticmethod
    def set_sound_volume(volume):
        SoundSystem.sound_volume = max(0.0, min(1.0, volume))
        for sound in SoundSystem.sounds.values():
            sound.set_volume(SoundSystem.sound_volume)
        for sound_channels in SoundSystem.overlapping_sounds.values():
            for channel in sound_channels:
                channel.set_volume(SoundSystem.sound_volume)

    @staticmethod
    def set_background_volume(volume):
        SoundSystem.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(SoundSystem.music_volume)

    @staticmethod
    def load_background_music(path):
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(SoundSystem.music_volume)
            SoundSystem.background_music = path
        except pygame.error as e:
            print(f"Error loading background music '{path}': {e}")

    @staticmethod
    def play_background_music(loops=-1):
        try:
            if SoundSystem.background_music:
                pygame.mixer.music.play(loops=loops)
            else:
                print("No background music loaded!")
        except pygame.error as e:
            print(e)

    @staticmethod
    def stop_background_music():
        pygame.mixer.music.stop()

    @staticmethod
    def resume_background_music():
        pygame.mixer.music.unpause()

    @staticmethod
    def cleanup_overlapping_sounds():
        """Optional method to clean up finished overlapping sounds."""
        for name, channels in SoundSystem.overlapping_sounds.items():
            SoundSystem.overlapping_sounds[name] = [
                ch for ch in channels if ch.get_busy()
            ]
