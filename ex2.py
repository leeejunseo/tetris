import pygame
import time
import threading # 스레딩 모듈 가져오기

pygame.init()

# 화면 설정
screen_width = 600
screen_height = 400
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Thread_Example")

# 색깔
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
gray = (200, 200, 200)

# 폰트
font = pygame.font.SysFont(None, 50)

# 버튼 설정
button_rect = pygame.Rect(200, 150, 200, 100)
button_text = font.render("Process Start", True, black)
text_rect = button_text.get_rect(center=button_rect.center)

# 메시지 (스레드 간 안전한 공유를 위해 Lock 사용 고려 가능)
message = ""
message_color = black
message_surf = None
# 스레드에서 UI 요소를 직접 업데이트하는 것은 주의해야 합니다.
# 이 예제에서는 간단하게 전역 변수를 사용하지만, 복잡한 경우 Queue 등을 사용하는 것이 좋습니다.

def update_message(text, color):
    """메시지 업데이트 함수 (메인 스레드에서 호출되도록 관리 필요)"""
    global message, message_color, message_surf
    message = text
    message_color = color
    # Pygame의 폰트 렌더링은 메인 스레드에서 하는 것이 안전합니다.
    # 여기서는 간단히 하지만, 실제로는 이 부분을 메인 루프에서 처리하도록 이벤트나 플래그를 사용할 수 있습니다.
    message_surf = font.render(message, True, message_color)


def slow_task_threaded():
    """시간이 오래 걸리는 작업을 별도의 스레드에서 실행"""
    # 주의: 스레드에서 Pygame의 그래픽 관련 함수를 직접 호출하는 것은 일반적으로 안전하지 않습니다.
    #       UI 업데이트는 메인 스레드로 전달하여 처리하는 것이 좋습니다.
    #       이 예제에서는 메시지 내용만 바꾸고, 실제 렌더링은 메인 루프에서 합니다.
    print("스레드: 느린 작업 시작...")
    # 메인 스레드에 메시지 업데이트 요청 (예시)
    # 실제로는 pygame.event.post 등을 사용하여 메인 스레드로 이벤트를 보내는 것이 더 좋습니다.
    # 여기서는 직접 전역 변수를 수정하지만, 복잡한 애플리케이션에서는 동기화 문제가 발생할 수 있습니다.
    global message, message_color
    message = "Processing..."
    message_color = red
    # 실제 렌더링은 메인 루프에서 하므로, 여기서는 텍스트만 준비
    time.sleep(3)
    message = "Process_Done!"
    message_color = green
    print("스레드: 작업 완료!")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                # 스레드를 생성하고 시작합니다.
                # target에는 스레드에서 실행할 함수를 지정합니다.
                task_thread = threading.Thread(target=slow_task_threaded)
                task_thread.start() # 스레드 시작

    # 메시지 서피스를 매 프레임마다 현재 메시지 내용으로 다시 렌더링
    # 이렇게 하면 스레드가 message 변수를 변경했을 때 화면에 반영됩니다.
    if message:
        message_surf = font.render(message, True, message_color)

    screen.fill(white)
    pygame.draw.rect(screen, gray, button_rect)
    screen.blit(button_text, text_rect)

    if message_surf:
        screen.blit(message_surf, (50, 300))

    pygame.display.flip()

pygame.quit()