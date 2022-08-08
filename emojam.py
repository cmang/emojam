#!/usr/bin/env python3

from emojam import main

if __name__ == "__main__":
    try:
        main.main()
    except KeyboardInterrupt:
        print("\nCaught interrupt, exiting...")
        exit(0)
