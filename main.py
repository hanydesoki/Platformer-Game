from platformer_game import Game, LevelEditor


def main(edit_mode: bool = False):
    if edit_mode:
        level_editor = LevelEditor(filepath="my_map.json")
        level_editor.run()
    else:
        game = Game()
        game.run()

if __name__ == "__main__":
    main(edit_mode=True)