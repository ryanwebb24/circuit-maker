import pygame
from typing import Callable, Optional, Tuple


class Button:
    """A simple, reusable UI button for Pygame.

    Features:
    - Draws a rectangle with a label centered
    - Hover and pressed visual states
    - Click callback (left mouse button)
    - Enable/disable

    Usage:
        btn = Button((x,y,w,h), "Click me", on_click=callback)
        # in main loop:
        for event in pygame.event.get():
            btn.handle_event(event)
        btn.update(pygame.mouse.get_pos())
        btn.draw(screen)
    """

    def __init__(
        self,
        rect: Tuple[int, int, int, int],
        text: str,
        on_click: Optional[Callable] = None,
        font: Optional[pygame.font.Font] = None,
        font_size: int = 18,
        colors: Optional[dict] = None,
        border_color: Tuple[int, int, int] = (0, 0, 0),
        border_width: int = 2,
    ) -> None:
        if pygame.get_init() is False:
            pygame.init()

        self.rect = pygame.Rect(rect)
        self.text = text
        self.on_click = on_click
        self.enabled = True

        # State
        self.hover = False
        self.pressed = False

        # Font
        if font is None:
            self.font = pygame.font.SysFont(None, font_size)
        else:
            self.font = font

        # Colors
        default_colors = {
            "bg": (200, 200, 200),
            "hover": (180, 180, 180),
            "pressed": (150, 150, 150),
            "text": (0, 0, 0),
            "disabled": (140, 140, 140),
        }
        self.colors = default_colors
        if colors:
            self.colors.update(colors)

        self.border_color = border_color
        self.border_width = border_width

        # Pre-rendered text surface (updated in set_text)
        self._text_surf = None
        self._text_rect = None
        self._render_text()

    def _render_text(self) -> None:
        if not self.text:
            self._text_surf = None
            self._text_rect = None
            return
        color = self.colors["text"] if self.enabled else self.colors["disabled"]
        self._text_surf = self.font.render(self.text, True, color)
        self._text_rect = self._text_surf.get_rect(center=self.rect.center)

    def set_text(self, text: str) -> None:
        self.text = text
        self._render_text()

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled
        self._render_text()

    def set_callback(self, cb: Callable) -> None:
        self.on_click = cb

    def update(self, mouse_pos: Tuple[int, int]) -> None:
        """Update hover state using current mouse position."""
        if not self.enabled:
            self.hover = False
            self.pressed = False
            return
        self.hover = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle Pygame events. Call this from your main event loop."""
        if not self.enabled:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed and self.rect.collidepoint(event.pos):
                # Click completed
                if callable(self.on_click):
                    try:
                        self.on_click()
                    except Exception:
                        # Swallow exceptions from callbacks to avoid crashing the UI
                        pass
            self.pressed = False

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the button on the given surface."""
        # Background color depends on state
        if not self.enabled:
            bg = self.colors["disabled"]
        elif self.pressed:
            bg = self.colors["pressed"]
        elif self.hover:
            bg = self.colors["hover"]
        else:
            bg = self.colors["bg"]

        pygame.draw.rect(surface, bg, self.rect)
        if self.border_width > 0:
            pygame.draw.rect(surface, self.border_color, self.rect, self.border_width)

        if self._text_surf:
            # Update text rect in case the button moved
            self._text_rect = self._text_surf.get_rect(center=self.rect.center)
            surface.blit(self._text_surf, self._text_rect)


# Small helper to create a button centered at (cx,cy)
def create_button_centered(cx: int, cy: int, w: int, h: int, text: str, on_click: Optional[Callable] = None, **kwargs) -> Button:
    x = int(round(cx - w / 2.0))
    y = int(round(cy - h / 2.0))
    return Button((x, y, w, h), text, on_click=on_click, **kwargs)
