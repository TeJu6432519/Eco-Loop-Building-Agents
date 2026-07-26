from energyPlus.prepare_idf import prepare_idf
from energyPlus.run_simulation import run_simulation


def main():

    prepare_idf()

    run_simulation()


if __name__ == "__main__":
    main()