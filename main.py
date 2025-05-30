import pygame

# Main game loop
def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    # Debug: Confirm initialization
    print("[DEBUG] Game initialized. Listening for Tab key...")
    
    running = True
    while running:
        # Debug: Confirm game loop is running
        print("[DEBUG] Game loop running", end='\r')
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                print(f"[DEBUG] Key pressed: {pygame.key.name(event.key)}")  # Debug all keys
                if event.key == pygame.K_TAB:
                    print("[DEBUG] Tab key detected!")
                    player_ui.toggle_ui()
        
        # Existing game logic below (unchanged)
        screen.fill((0, 0, 0))
        player_ui.render(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main() 