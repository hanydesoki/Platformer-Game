from platformer_game import LevelSelection


def main() -> None:
    level_selection = LevelSelection(folderpath="Levels")

    level_selection.run()


if __name__ == "__main__":
    main()