import pygame
import time

pygame.init()

# 화면 설정
screen_width = 600
screen_height = 400
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("스레딩 예제 (문제점)")

# 색깔
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
gray = (200, 200, 200)

# 폰트
font = pygame.font.SysFont(None, 50)

# 버튼 설정
button_rect = pygame.Rect(200, 150, 200, 100)
button_text = font.render("Process start", True, black)
text_rect = button_text.get_rect(center=button_rect.center)

# 메시지
message = ""
message_surf = None

def slow_task():
    """시간이 오래 걸리는 작업을 흉내 내는 함수"""
    global message, message_surf
    message = "느린 작업 시작..."
    message_surf = font.render(message, True, red)
    print(message)
    time.sleep(3) # 3초 동안 프로그램 멈춤
    message = "Process_Done!"
    message_surf = font.render(message, True, red)
    print(message)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                slow_task() # 함수 직접 호출

    screen.fill(white)
    pygame.draw.rect(screen, gray, button_rect)
    screen.blit(button_text, text_rect)

    if message_surf:
        screen.blit(message_surf, (50, 300))

    pygame.display.flip()

pygame.quit()