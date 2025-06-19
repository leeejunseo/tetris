import pygame
import random

# --- 초기 설정 ---
pygame.init()

# 화면 크기
SCREEN_WIDTH = 400  # 게임 화면 너비 (블록 10개 + 좌우 여백)
SCREEN_HEIGHT = 600 # 게임 화면 높이 (블록 20개 + 상하 여백)
PLAY_WIDTH = 300    # 실제 게임 플레이 영역 너비 (10 블록 * 30 픽셀)
PLAY_HEIGHT = 600   # 실제 게임 플레이 영역 높이 (20 블록 * 30 픽셀)
BLOCK_SIZE = 30

# 게임 화면의 좌상단 x, y 좌표 (플레이 영역을 화면 중앙에 배치하기 위함)
top_left_x = (SCREEN_WIDTH - PLAY_WIDTH) // 2
top_left_y = SCREEN_HEIGHT - PLAY_HEIGHT

# 색깔 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# 화면 생성
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("간단 테트리스")

# --- 테트리스 블록 모양 정의 ---
# 각 블록은 2차원 배열로 표현되며, 각 숫자는 블록의 일부임을 나타냅니다.
# 각 모양은 여러 회전 상태를 가질 수 있습니다. (여기서는 간단히 첫 번째 상태만 정의)
S_SHAPE = [['.....',
            '.....',
            '..00.',
            '.00..',
            '.....'],
           ['.....',
            '..0..',
            '..00.',
            '...0.',
            '.....']]

Z_SHAPE = [['.....',
            '.....',
            '.00..',
            '..00.',
            '.....'],
           ['.....',
            '..0..',
            '.00..',
            '.0...',
            '.....']]

I_SHAPE = [['..0..',
            '..0..',
            '..0..',
            '..0..',
            '.....'],
           ['.....',
            '0000.',
            '.....',
            '.....',
            '.....']]

O_SHAPE = [['.....',
            '.....',
            '.00..',
            '.00..',
            '.....']] # O 모양은 회전해도 동일

T_SHAPE = [['.....',
            '..0..',
            '.000.',
            '.....',
            '.....'],
           ['.....',
            '..0..',
            '..00.',
            '..0..',
            '.....'],
           ['.....',
            '.....',
            '.000.',
            '..0..',
            '.....'],
           ['.....',
            '..0..',
            '.00..',
            '..0..',
            '.....']]

J_SHAPE = [['.....',
            '.0...',
            '.000.',
            '.....',
            '.....'],
           ['.....',
            '..00.',
            '..0..',
            '..0..',
            '.....'],
           ['.....',
            '.....',
            '.000.',
            '...0.',
            '.....'],
           ['.....',
            '..0..',
            '..0..',
            '.00..',
            '.....']]

L_SHAPE = [['.....',
            '...0.',
            '.000.',
            '.....',
            '.....'],
           ['.....',
            '..0..',
            '..0..',
            '..00.',
            '.....'],
           ['.....',
            '.....',
            '.000.',
            '.0...',
            '.....'],
           ['.....',
            '.00..',
            '..0..',
            '..0..',
            '.....']]

# 블록 모양 리스트와 색깔 리스트
shapes = [S_SHAPE, Z_SHAPE, I_SHAPE, O_SHAPE, T_SHAPE, J_SHAPE, L_SHAPE]
shape_colors = [GREEN, RED, CYAN, YELLOW, MAGENTA, BLUE, ORANGE]

# --- 클래스 정의 ---
class Piece:
    def __init__(self, column, row, shape):
        self.x = column
        self.y = row
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)] # 모양에 따른 색깔 지정
        self.rotation = 0 # 현재 회전 상태

# --- 함수 정의 ---
def create_grid(locked_positions={}):
    """
    게임 보드(그리드)를 생성합니다.
    locked_positions: 이미 블록이 쌓여있는 위치와 색깔 정보 ( (x,y): (r,g,b) )
    그리드는 각 칸의 색깔 정보를 담는 2차원 리스트로 표현됩니다. (0은 빈 칸)
    """
    grid = [[BLACK for _ in range(10)] for _ in range(20)] # 10x20 그리드

    for r in range(len(grid)):
        for c in range(len(grid[r])):
            if (c, r) in locked_positions:
                color = locked_positions[(c, r)]
                grid[r][c] = color
    return grid

def convert_shape_format(piece):
    """
    Piece 객체의 현재 모양과 회전 상태에 따라,
    실제 그리드 좌표에 해당하는 블록 위치 리스트를 반환합니다.
    """
    positions = []
    shape_format = piece.shape[piece.rotation % len(piece.shape)] # 현재 회전 상태의 모양 가져오기

    # shape_format은 문자열 리스트. '0'이 블록을 의미
    for i, line in enumerate(shape_format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((piece.x + j, piece.y + i))

    # 모양 데이터의 좌상단 빈 공간을 제거하기 위한 오프셋 조정
    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4) # shape 정의 시 여백을 고려한 오프셋
    return positions

def valid_space(piece, grid):
    """
    현재 Piece가 이동하려는 위치가 유효한 공간인지 확인합니다.
    (그리드 경계 안 & 다른 블록과 겹치지 않는지)
    """
    # 모든 가능한 그리드 위치를 튜플로 만듭니다 (빈 공간만)
    accepted_positions = [[(j, i) for j in range(10) if grid[i][j] == BLACK] for i in range(20)]
    accepted_positions = [j for sub in accepted_positions for j in sub] # 1차원 리스트로 변환

    formatted_shape = convert_shape_format(piece)

    for pos in formatted_shape:
        if pos not in accepted_positions: # 유효한 빈 공간 리스트에 없으면
            if pos[1] > -1: # 화면 상단보다 위에 있는 경우는 아직 유효 (게임 시작 시)
                return False # 유효하지 않은 공간
    return True

def check_lost(positions):
    """
    새 블록이 생성될 때, 이미 쌓인 블록과 겹쳐서 게임오버인지 확인합니다.
    positions: (x,y) 좌표 리스트
    """
    for pos in positions:
        x, y = pos
        if y < 1: # 블록의 y좌표가 1보다 작으면 (화면 최상단에 겹침)
            return True
    return False

def get_shape():
    """새로운 블록(Piece 객체)을 랜덤하게 생성하여 반환합니다."""
    return Piece(5, 0, random.choice(shapes)) # 초기 x위치는 5 (중앙), y위치는 0 (최상단)

def draw_text_middle(text, size, color, surface):
    """화면 중앙에 텍스트를 그립니다."""
    font = pygame.font.SysFont('comicsansms', size, bold=True)
    label = font.render(text, 1, color)
    surface.blit(label, (SCREEN_WIDTH/2 - label.get_width()/2, SCREEN_HEIGHT/2 - label.get_height()/2))

def draw_grid_lines(surface, grid):
    """게임 보드에 그리드 선을 그립니다."""
    for i in range(len(grid)): # 가로선
        pygame.draw.line(surface, GRAY, (top_left_x, top_left_y + i * BLOCK_SIZE),
                         (top_left_x + PLAY_WIDTH, top_left_y + i * BLOCK_SIZE))
    for j in range(len(grid[0]) + 1): # 세로선
        pygame.draw.line(surface, GRAY, (top_left_x + j * BLOCK_SIZE, top_left_y),
                         (top_left_x + j * BLOCK_SIZE, top_left_y + PLAY_HEIGHT))


def clear_rows(grid, locked):
    """
    꽉 찬 가로줄을 찾아 제거하고, 위의 블록들을 아래로 내립니다.
    제거된 줄 수를 반환합니다.
    """
    increment = 0 # 제거된 줄 수
    for i in range(len(grid)-1, -1, -1): # 아래에서부터 위로 탐색
        row = grid[i]
        if BLACK not in row: # 줄에 빈 칸(BLACK)이 없으면 꽉 찬 줄
            increment += 1
            ind = i # 제거할 줄의 인덱스
            for j in range(len(row)):
                try:
                    del locked[(j, i)] # locked_positions에서 해당 줄의 블록 정보 삭제
                except:
                    continue
    # 꽉 찬 줄이 있다면, 그 위의 줄들을 아래로 내림
    if increment > 0:
        # sorted는 (x,y) 키를 y값 기준으로 정렬 (아래에서 위로)
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind: # 제거된 줄(ind)보다 위에 있는 블록이라면
                new_key = (x, y + increment) # 제거된 줄 수만큼 아래로 이동
                locked[new_key] = locked.pop(key)
    return increment

def draw_next_shape(piece, surface):
    """다음 나올 블록을 화면 우측에 표시합니다."""
    font = pygame.font.SysFont('comicsansms', 30)
    label = font.render('Next Shape', 1, WHITE)

    sx = top_left_x + PLAY_WIDTH + 10  # "Next Shape" 텍스트와 블록 표시 시작 x좌표
    sy = top_left_y + PLAY_HEIGHT/2 - 100 # y 좌표
    shape_format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(shape_format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, piece.color,
                                 (sx + j*BLOCK_SIZE - BLOCK_SIZE*1.5, sy + i*BLOCK_SIZE - BLOCK_SIZE*2, BLOCK_SIZE, BLOCK_SIZE), 0)

    surface.blit(label, (sx , sy - 40))

def draw_window(surface, grid, score=0, last_score=0):
    """게임 화면 전체를 그립니다."""
    surface.fill(BLACK) # 배경 검은색

    # 타이틀
    font = pygame.font.SysFont('comicsansms', 50)
    label = font.render('TETRIS', 1, WHITE)
    surface.blit(label, (top_left_x + PLAY_WIDTH / 2 - (label.get_width() / 2), 30))

    # 현재 점수 표시
    font = pygame.font.SysFont('comicsansms', 30)
    label = font.render('Score: ' + str(score), 1, WHITE)
    sx = top_left_x + PLAY_WIDTH + 10
    sy = top_left_y + PLAY_HEIGHT/2 - 150 # 다음 블록 표시 위치보다 약간 위
    surface.blit(label, (sx, sy + 160))

    # 최고 점수 (간단히 이전 게임 점수로 표시)
    label = font.render('Last Score: ' + str(last_score), 1, WHITE)
    surface.blit(label, (sx, sy + 200))


    # 그리드에 쌓인 블록들 그리기
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j],
                             (top_left_x + j*BLOCK_SIZE, top_left_y + i*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

    # 게임 플레이 영역 테두리 그리기
    pygame.draw.rect(surface, GRAY, (top_left_x, top_left_y, PLAY_WIDTH, PLAY_HEIGHT), 5)

    # 그리드 선 그리기 (선택 사항)
    draw_grid_lines(surface, grid)


def update_score(nscore):
    """점수 파일에서 최고 점수를 읽고, 현재 점수가 더 높으면 업데이트 (간단 버전)"""
    # 이 예제에서는 파일 저장을 생략하고, 마지막 점수만 추적합니다.
    # 실제 게임에서는 파일에 저장하는 것이 좋습니다.
    return nscore # 여기서는 그냥 현재 점수를 반환 (last_score 관리는 main_menu에서)


def main(win):
    """메인 게임 루프 함수"""
    locked_positions = {}  # (x,y): (r,g,b) 형태로 고정된 블록 정보 저장
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.30  # 블록이 한 칸 아래로 떨어지는 데 걸리는 시간 (초)
    level_time = 0
    score = 0
    last_score = 0 # 이전 게임 점수 (main_menu에서 관리)

    while run:
        grid = create_grid(locked_positions) # 매 프레임마다 그리드 상태 업데이트
        fall_time += clock.get_rawtime() # 이전 프레임 이후 경과 시간 (밀리초)
        level_time += clock.get_rawtime()
        clock.tick() # FPS 제한 (너무 빠르지 않게)

        # 일정 시간마다 블록 자동 하강
        if fall_time/1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not (valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1 # 원위치
                change_piece = True # 블록 고정 및 새 블록 준비

        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN: # 소프트 드롭
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP: # 회전
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape) # 원상 복구
                elif event.key == pygame.K_SPACE: # 하드 드롭 (구현은 생략, 소프트 드롭 반복으로 대체 가능)
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1
                    change_piece = True # 바로 고정


        # 현재 블록의 화면상 위치 계산
        shape_pos = convert_shape_format(current_piece)

        # 현재 블록을 그리드에 임시로 표시 (색깔 입히기)
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1: # 그리드 범위 안에 있을 때만
                grid[y][x] = current_piece.color

        # 블록이 바닥이나 다른 블록 위에 도달했을 때
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color # 블록을 고정된 위치에 저장
            current_piece = next_piece # 다음 블록을 현재 블록으로
            next_piece = get_shape()   # 새로운 다음 블록 생성
            change_piece = False
            cleared_rows_count = clear_rows(grid, locked_positions) # 줄 제거 처리
            score += cleared_rows_count * 10 # 간단한 점수 계산 (제거한 줄 수 * 10)

            # 난이도 조절 (예: 5줄 제거할 때마다 속도 증가)
            if cleared_rows_count > 0 and score > 0 and score % 50 == 0 : # 5줄 제거에 해당 (5 * 10점)
                if fall_speed > 0.15: # 최소 속도 제한
                    fall_speed -= 0.01


        # 화면 그리기
        draw_window(screen, grid, score, last_score)
        draw_next_shape(next_piece, screen)
        pygame.display.update()

        # 게임 오버 조건 확인
        if check_lost(locked_positions):
            draw_text_middle("YOU LOST!", 80, WHITE, screen)
            pygame.display.update()
            pygame.time.delay(2000) # 2초 대기 후
            run = False
            # last_score = update_score(score) # 점수 업데이트 로직 필요시

    return score # 게임 종료 시 현재 점수 반환


def main_menu(win):
    """게임 시작 전 메인 메뉴 화면"""
    run = True
    last_score = 0 # 파일에서 읽어오거나, 이전 게임의 점수를 저장할 변수
    while run:
        win.fill(BLACK)
        draw_text_middle('Press Any Key To Play', 50, WHITE, win)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                current_game_score = main(win) # 게임 시작
                if current_game_score > last_score: # 최고 점수 갱신 (간단)
                    last_score = current_game_score

    pygame.quit()


if __name__ == '__main__':
    main_menu(screen)