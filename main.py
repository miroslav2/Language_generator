import sys


def main():
    if "--cli" in sys.argv or "-c" in sys.argv:
        from ui.debug_launcher import DebugRunner

        DebugRunner().run()
    else:
        from ui.language_wizard import run_wizard

        run_wizard()


if __name__ == "__main__":
    main()