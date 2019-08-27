class TableColors(object):
    """Colors"""
    try:
        from colored import fg, bg, attr

        TEXT_COLOR_WHITE = fg('white')
        TEXT_COLOR_YELLOW = fg(226)
        TEXT_COLOR_RED = fg(196)
        TEXT_COLOR_GREEN = fg(119)
        TEXT_COLOR_BLUE = fg(27)
        BG_COLOR_ROW = bg(244)
        BG_RESET = attr('reset')  # docs say bg(0) should do this but it doesn't work right
        BOLD = attr('bold')
        RESET = attr('reset')
    except ImportError:
        try:
            from colorama import Fore, Back, Style

            TEXT_COLOR_WHITE = Fore.WHITE
            TEXT_COLOR_YELLOW = Fore.LIGHTYELLOW_EX
            TEXT_COLOR_RED = Fore.LIGHTRED_EX
            TEXT_COLOR_GREEN = Fore.LIGHTGREEN_EX
            TEXT_COLOR_BLUE = Fore.LIGHTBLUE_EX
            BG_COLOR_ROW = Back.LIGHTBLACK_EX
            BG_RESET = Back.RESET
            BOLD = Style.BRIGHT
            RESET = Style.NORMAL + Fore.RESET + Back.RESET
        except ImportError:
            TEXT_COLOR_WHITE = ''
            TEXT_COLOR_YELLOW = ''
            TEXT_COLOR_RED = ''
            TEXT_COLOR_GREEN = ''
            TEXT_COLOR_BLUE = ''
            BG_COLOR_ROW = ''
            BG_RESET = ''
            BOLD = ''
            RESET = ''

    @classmethod
    def set_color_library(cls, library_name: str) -> None:
        """Manually override the color library being used."""
        if library_name == 'colored':
            from colored import fg, bg, attr

            cls.TEXT_COLOR_WHITE = fg('white')
            cls.TEXT_COLOR_YELLOW = fg(226)
            cls.TEXT_COLOR_RED = fg(196)
            cls.TEXT_COLOR_GREEN = fg(119)
            cls.TEXT_COLOR_BLUE = fg(27)
            cls.BG_COLOR_ROW = bg(244)
            cls.BG_RESET = attr('reset')  # docs say bg(0) should do this but it doesn't work right
            cls.BOLD = attr('bold')
            cls.RESET = attr('reset')
        elif library_name == 'colorama':
            from colorama import Fore, Back, Style

            cls.TEXT_COLOR_WHITE = Fore.WHITE
            cls.TEXT_COLOR_YELLOW = Fore.LIGHTYELLOW_EX
            cls.TEXT_COLOR_RED = Fore.LIGHTRED_EX
            cls.TEXT_COLOR_GREEN = Fore.LIGHTGREEN_EX
            cls.TEXT_COLOR_BLUE = Fore.LIGHTBLUE_EX
            cls.BG_COLOR_ROW = Back.LIGHTBLACK_EX
            cls.BG_RESET = Back.RESET
            cls.BOLD = Style.BRIGHT
            cls.RESET = Style.NORMAL + Fore.RESET + Back.RESET
        else:
            cls.TEXT_COLOR_WHITE = ''
            cls.TEXT_COLOR_YELLOW = ''
            cls.TEXT_COLOR_RED = ''
            cls.TEXT_COLOR_GREEN = ''
            cls.TEXT_COLOR_BLUE = ''
            cls.BG_COLOR_ROW = ''
            cls.BG_RESET = ''
            cls.BOLD = ''
            cls.RESET = ''
