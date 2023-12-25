import asyncio
import websockets
from ball import Ball
from board import *
from multis import *
from settings import *
import ctypes, pygame, pymunk, random, sys
import threading

# Maintain resolution regardless of Windows scaling settings
ctypes.windll.user32.SetProcessDPIAware()

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE_STRING)
        self.clock = pygame.time.Clock()
        self.delta_time = 0
        self.space = pymunk.Space()
        self.space.gravity = (0, 1800)
        self.ball_group = pygame.sprite.Group()
        self.board = Board(self.space)
        self.balls_played = 0

    async def receive_commands(self, websocket, path):
        print("Connected successfully!")
        async for message in websocket:
            print(f"Received message: {message}")
            if message == "throw_ball":
                print("Throwing a ball...")
                random_x = WIDTH//2 + random.choice([random.randint(-20, -1), random.randint(1, 20)])
                self.ball = Ball((random_x, 20), self.space, self.board, self.delta_time)
                self.ball_group.add(self.ball)

    async def start_server(self):
        server = await websockets.serve(self.receive_commands, "localhost", 8765)
        print("Server started...")
        await server.wait_closed()

    def run(self):
        threading.Thread(target=self.start_server_thread, daemon=True).start()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill(BG_COLOR)
            self.delta_time = self.clock.tick(FPS) / 1000.0
            self.space.step(self.delta_time)
            self.board.update()
            self.ball_group.update()
            pygame.display.update()

    def start_server_thread(self):
        asyncio.run(self.start_server())

if __name__ == '__main__':
    game = Game()
    game.run()
