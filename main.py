from driver import initialise_selenium
from otomoto.scripts import get_all_car_brands

def main():
    wd = initialise_selenium()
    car_brands = get_all_car_brands(wd)


if __name__ == "__main__":
    main()



# TODO you can make a class thath will parse and store web elements in a way that will 
# be easy to input into db 