# imports
from asyncio import TimerHandle
import sys
import os
import pygame
from pygame.locals import *
from engine import TextView, ViewBase, Board, Color

_print_dim = False


class PygameView(ViewBase):
    """Renders a board in pygame."""

    COLOR_MAP = {
        Color.CLEAR: pygame.Color(255, 255, 255),
        Color.RED: pygame.Color(255, 0, 0),
        Color.BLUE: pygame.Color(0, 255, 0),
        Color.GREEN: pygame.Color(0, 0, 255),
        Color.YELLOW: pygame.Color(255, 255, 0),
        Color.MAGENTA: pygame.Color(255, 0, 255),
        Color.CYAN: pygame.Color(0, 255, 255),
        Color.ORANGE: pygame.Color(255, 140, 0),
        Color.BLACK: pygame.Color(0, 0, 0),
        #AQUATIC THEME
        Color.TIFFANY_BLUE: pygame.Color(0, 173, 169),
        Color.AQUAMARINE: pygame.Color(127, 255, 212),
        Color.HONOLULU_BLUE: pygame.Color(0, 113, 173),
        Color.JACARTA: pygame.Color(71, 40, 100),
        Color.PEARLY_PURPLE: pygame.Color(163, 95, 152),
        Color.LEMON_MERINGUE: pygame.Color(249, 229, 193),
        Color.NAPLES_YELLOW: pygame.Color(252, 218, 100),
        #FOREST THEME
        Color.DARK_LAVA: pygame.Color(69, 55, 48),
        Color.COYOTE_BROWN: pygame.Color(130, 94, 65),
        Color.CRAYOLAS_OUTER_SPACE: pygame.Color(44, 62, 57),
        Color.GRAY_ASPARAGUS: pygame.Color(65, 90, 69),
        Color.AXOLOTL: pygame.Color(108, 112, 88),
        Color.PHILIPPINE_GRAY: pygame.Color(152, 147, 139),
        Color.ARTICHOKE: pygame.Color(138, 166, 131),
        #Industrial
        Color.JAPANESE_INDIGO: pygame.Color(44, 63, 80),
        Color.CARMINE_PINK: pygame.Color(232, 76, 61),
        Color.BRIGHT_GRAY: pygame.Color(236, 240, 241),
        Color.TUFTS_BLUE: pygame.Color(50, 151, 219),
        Color.CRAYOLAS_GOLD: pygame.Color(227, 194, 132),
        Color.SEA_GREEN: pygame.Color(39, 160, 99),
        Color.ASH_GRAY: pygame.Color(186, 185, 181)
    }

    BOARD_BORDER_SIZE = 5
    SCORE_PADDING = 5
    BORDER_SIZE = 4
    BORDER_FADE = pygame.Color(50, 50, 50)

    def __init__(self, surf, fonts):
        ViewBase.__init__(self)
        self.surf = surf
        self.view_width = surf.get_width()
        self.view_height = surf.get_height()
        self.box_size = 10
        self.padding = (0, 0)
        self.go_font = fonts["game_over"]
        self.sc_font = fonts["score"]
        self.font_color = pygame.Color(200, 0, 0)
        self.score = None
        self.level = None

        self.end_msg = self.go_font.render("GAME OVER", True, self.font_color)

    # Public interface to views
    def set_size(self, cols, rows):
        ViewBase.set_size(self, cols, rows)
        self.calc_dimensions()

    def set_score(self, score):
        self.score = score

    def set_level(self, level):
        if self.level != level:
            pygame.event.post(pygame.event.Event(Tetris.LEVEL_UP, level=level))
        self.level = level

    def show(self):
        self.draw_board()
        self.show_score()
        self.draw_hold()
    
    def show_hold(self, hold_block, block_color):
        if hold_block != None:
            hold_color = self.COLOR_MAP[block_color]
            for dx in hold_block:
                pygame.draw.rect(self.surf, (20, 20, 20), Rect(45+25*dx[1], 160+25*dx[0], 25, 25))
                pygame.draw.rect(self.surf, hold_color, Rect(45+25*dx[1], 160+25*dx[0], 21, 21))

    def show_score(self):
        score_height = 0
        if self.score is not None:
            score_surf = self.sc_font.render(
                "{:06d}".format(self.score), True, self.font_color)
            self.surf.blit(
                score_surf, (self.BOARD_BORDER_SIZE, self.BOARD_BORDER_SIZE))
            score_height = score_surf.get_height()

        if self.level is not None:
            level_surf = self.sc_font.render(
                "LEVEL {:02d}".format(self.level), True, self.font_color)
            level_pos = (self.BOARD_BORDER_SIZE,
                         self.BOARD_BORDER_SIZE + score_height + self.SCORE_PADDING)
            self.surf.blit(level_surf, level_pos)
            
    def draw_hold(self):
        hold_font = pygame.font.SysFont('ni7seg', 40)
        hold_surf = hold_font.render("HOLD", True, (225, 225, 225))
        hold_pos = (30, 120)
        self.surf.blit(hold_surf, hold_pos)
        #pygame.draw.rect(self.surf, (225, 225, 225), Rect(20, 150, 120, 120), 2)            

    def show_game_over(self):
        r = self.end_msg.get_rect()
        self.surf.blit(self.end_msg, (300 - r.width // 2, 300 - r.height // 2))

    # Helper methods

    def get_score_size(self):
        (sw, sh) = self.sc_font.size("000000")
        (lw, lh) = self.sc_font.size("LEVEL 00")
        return (max(sw, lw) + self.BOARD_BORDER_SIZE, sh + lh + self.SCORE_PADDING)

    def calc_dimensions(self):
        horiz_size = (self.view_width -
                      (self.BOARD_BORDER_SIZE * 2)) // self.width
        vert_size = (self.view_height -
                     (self.BOARD_BORDER_SIZE * 2)) // self.height

        if vert_size > horiz_size:
            self.box_size = horiz_size
            self.padding = (self.get_score_size()[0] * 2,
                            (self.view_height
                                - self.BOARD_BORDER_SIZE
                                - (self.height * horiz_size)))
        else:
            self.box_size = vert_size
            left_padding = max(self.get_score_size()[0] * 2,
                               (self.view_width
                                - self.BOARD_BORDER_SIZE
                                - (self.width * vert_size)))
            self.padding = (left_padding, 0)

        global _print_dim
        if not _print_dim:
            print(self.width, self.height)
            print(self.view_width, self.view_height)
            print(horiz_size, vert_size)
            print(self.box_size)
            print(self.padding)
            _print_dim = True

    def draw_board(self):
        bg_color = self.COLOR_MAP[Color.BLACK]
        self.surf.fill(bg_color + self.BORDER_FADE)

        X_START = self.BOARD_BORDER_SIZE + (self.padding[1] // 2)
        Y_START = self.BOARD_BORDER_SIZE + (self.padding[0] // 2)

        x = X_START
        y = Y_START
        board_rect = (y, x, self.width * self.box_size,
                      self.height * self.box_size)
        pygame.draw.rect(self.surf, bg_color, board_rect)
        for col in self.rows:
            for item in col:
                self.draw_box(x, y, item)
                y += self.box_size
            x += self.box_size
            y = Y_START

    def draw_box(self, x, y, color):
        if color == Color.CLEAR:
            return

        pg_color = self.COLOR_MAP[color]
        bd_size = self.BORDER_SIZE
        bd_color = pg_color - self.BORDER_FADE

        outer_rect = (y, x, self.box_size, self.box_size)
        inner_rect = (y + bd_size, x + bd_size,
                      self.box_size - bd_size*2, self.box_size - bd_size*2)

        pygame.draw.rect(self.surf, bd_color, outer_rect)
        pygame.draw.rect(self.surf, pg_color, inner_rect)


class Tetris:
    DROP_EVENT = USEREVENT + 1
    LEVEL_UP = USEREVENT + 2
    IS_SURVIVAL_MODE = False
    IS_SPRINT_MODE = False
    
    

    def __init__(self, view_type):
        self.board = Board(10, 20)
        self.board.generate_piece()
        self.view_type = view_type
        self.game_over = False

        if view_type == TextView:
            def cls():
                os.system('cls')
            self.show_action = cls
            self.max_fps = 5
        else:
            self.show_action = None
            self.max_fps = 50

    def key_handler(self, key):
        if key == K_LEFT:
            self.board.move_piece(-1, 0)
        elif key == K_RIGHT:
            self.board.move_piece(1, 0)
        elif key == K_UP:
            self.board.rotate_piece()
        elif key == K_DOWN:
            self.board.move_piece(0, 1)
        elif key == K_a:
            self.board.rotate_piece(clockwise=False)
        elif key == K_s:
            self.board.rotate_piece()
        elif key == K_SPACE:
            self.board.full_drop_piece()
        elif key == pygame.K_p:
          self.pause()
        elif key == K_h:
            self.board.hold_piece()
            
    def pause(self):
        isPaused = True;
        while(isPaused):
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    if (event.key == K_p):
                     isPaused = False                             
        pygame.display.update()    

    def init(self):
        pygame.init()
        pygame.display.set_caption("Tuffy Tetris")
        pygame.font.init()
        self.surf = pygame.display.set_mode((600, 600))
        self.font = None

        if pygame.font.get_init():
            self.fonts = {}
            self.fonts["game_over"] = pygame.font.SysFont("ni7seg", 60)
            self.fonts["score"] = pygame.font.SysFont("ni7seg", 18)

        self.view = self.view_type(self.surf, self.fonts)

    def show_colors(self):
        self.init()

        print("Fonts:", pygame.font.get_fonts())
        n = len(Color.colors())
        self.view.set_size(n+1, 1)
        for i in range(n):
            self.view.render_tile(i + 1, 0, Color.colors()[i])
        self.view.show()
        self.view.show_hold(self.board.get_hold_piece(), self.board.get_hold_color())       

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

    def get_level_speed(self, level):
        SPEEDS = {
            1: 1000,
            2: 750,
            3: 500,
            4: 400,
            5: 300,
            6: 250,
            7: 200,
            8: 150,
            9: 125,
            10: 100,
            11: 90,
            12: 80,
            13: 75
        }

        if level > 13:
            return 75 - (5 * (level - 13))
        else:
            return SPEEDS[level]

    # Renders current frame
    def render_frame(self):
        self.board.render(self.view)

        if self.show_action is not None:
            self.show_action()
        self.view.show()
        self.view.show_hold(self.board.get_hold_piece(), self.board.get_hold_color())
        
        if self.game_over:
            self.view.show_game_over()

        pygame.display.update()


    def main_survival(self):
        self.init()
        self.clock = pygame.time.Clock()
        pygame.time.set_timer(self.DROP_EVENT, self.get_level_speed(1))

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    self.key_handler(event.key)
                elif event.type == self.DROP_EVENT:
                    self.board.drop_piece()
                elif event.type == self.LEVEL_UP:
                    pygame.time.set_timer(
                        self.DROP_EVENT, self.get_level_speed(event.level))

            if self.board.game_over and not self.game_over:
                self.game_over = True
                # Additions
                userName = self.getUserName()
                currentLeaderboard = self.board.survivaLeaderboard(userName)
                self.displayLeaderboard(currentLeaderboard)
                pygame.time.set_timer(self.DROP_EVENT, 0)
                return

            self.render_frame()
            self.clock.tick(self.max_fps)


    def main_sprint(self):
        self.init()
        clock = pygame.time.Clock()

        timer_font = pygame.font.SysFont('ni7seg', 30)
        counter = 60 
        text = timer_font.render("01:00", True, (255, 0, 0))
        
        timer_pos = (5,45)
        pygame.time.set_timer(self.DROP_EVENT, self.get_level_speed(1))

        while True:
            for event in pygame.event.get():  
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    self.key_handler(event.key)
                elif event.type == self.DROP_EVENT:
                    if counter > 0:
                        counter -= 1
                        text = timer_font.render("00:%02d" % counter, True, (255, 0, 0))
                    else:
                        self.game_over = True
                        pygame.time.set_timer(self.DROP_EVENT, 0)
                        return  

                    self.board.drop_piece()
                elif event.type == self.LEVEL_UP:
                    pygame.time.set_timer(
                        self.DROP_EVENT, self.get_level_speed(event.level))
            
            if self.board.game_over and not self.game_over:
                self.game_over = True
                # Additions
                userName = self.getUserName()
                currentLeaderboard = self.board.sprintLeaderboard(userName)
                self.displayLeaderboard(currentLeaderboard)
                pygame.time.set_timer(self.DROP_EVENT, 0)
                return  


            self.render_frame()                    
            self.surf.blit(text, timer_pos)
            pygame.display.flip()
            clock.tick(self.max_fps)


#Ask for username
    def getUserName(self):
        #load images
        background = pygame.image.load("assets/Background.png")
        textRext = pygame.image.load("assets/Options Rect.png")
        #Score text and rect
        scoreText = pygame.font.Font("assets/font.ttf", 16).render("Enter a username to save score", True, "#b68f40")
        scoreRect = scoreText.get_rect(center=(300, 100))

        #Update name accordingly
        name = ""
        font = pygame.font.Font(None, 50)
        while True:
            for evt in pygame.event.get():
                if evt.type == KEYDOWN:
                    if evt.unicode.isalpha():
                        name += evt.unicode
                    elif evt.key == K_BACKSPACE:
                        name = name[:-1]
                    elif evt.key == K_RETURN:
                        return name
                elif evt.type == QUIT:
                    return

            #Update surface
            self.surf.blit(background, (0, 0))
            self.surf.blit(scoreText, scoreRect)
            block = font.render(name, True, (255, 255, 255))
            rect = block.get_rect()
            rect.center = self.surf.get_rect().center
            self.surf.blit(textRext, (5, 250))
            self.surf.blit(block, rect)
            pygame.display.flip()

    def displayLeaderboard(self, myLeaderboard):
        # load images
        background = pygame.image.load("assets/Background.png")
        textRect = pygame.image.load("assets/Options Rect.png")
        highScoreText = pygame.font.Font("assets/font.ttf", 16).render("Highscores", True, "#b68f40")
        scoreRect = highScoreText.get_rect(center=(300, 50))
        #NEW
        quitText = pygame.font.Font("assets/font.ttf", 16).render("Press [ENTER] to return to Main Menu", True, "#ffffff")
        quitRect = quitText.get_rect(center=(300, 400))

        self.surf.blit(background, (0, 0))
        self.surf.blit(highScoreText, scoreRect)
        self.surf.blit(quitText, quitRect)
        leaderBoardSize = len(myLeaderboard)
        if(leaderBoardSize < 5):
            for i in range(leaderBoardSize):
                textRext = pygame.image.load("assets/Options Rect.png")
                currentScoreText = pygame.font.Font("assets/font.ttf", 16).render(
                    str(i + 1) + ". " + str(myLeaderboard[i][0]) + "  " + str(myLeaderboard[i][1]), True, "#ffffff")
                currentScoreRect = highScoreText.get_rect(center=(300, 100 + (50 * i)))
                self.surf.blit(currentScoreText, currentScoreRect)
        else:
            for i in range(5):
                textRext = pygame.image.load("assets/Options Rect.png")
                currentScoreText = pygame.font.Font("assets/font.ttf", 16).render(
                    str(i + 1) + ". " + str(myLeaderboard[i][0]) + "  " + str(myLeaderboard[i][1]), True, "#ffffff")
                currentScoreRect = highScoreText.get_rect(center=(300, 100 + (50 * i)))
                self.surf.blit(currentScoreText, currentScoreRect)
        pygame.display.flip()

        while True:
            for evt in pygame.event.get():
                if evt.type == KEYDOWN:
                    if evt.key == K_RETURN:
                        return
                elif evt.type == QUIT:
                    quit()


    # Main game loop
    def main(self):

        if self.IS_SURVIVAL_MODE == True:
            self.main_survival()
        elif self.IS_SPRINT_MODE == True:
            self.main_sprint()
        
        
