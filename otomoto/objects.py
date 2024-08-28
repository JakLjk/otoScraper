class OFFER:
    def __repr__(self) -> str:
        pass

    def __init__(self, link) -> None:
        self.link:str = link
        self.data_dodania:str = None
        self.id:int = None
        self.tytul:str = None

        self.cena:float = None
        self.przebieg:int = None
        self.rodzaj_paliwa:str = None
        self.skrzynia_biegow:str = None
        self.typ_nadwozia:str = None
        self.pojemnosc_silnika:int = None
        self.moc_silnika:int = None

        # Offer coordinates
        self.x_coord:float = None
        self.y_coord:float = None
        self.coords_exact:bool = None
        
        self.opis:str = None

        # Seller info
        self.sprzedawca_nr_tel:int = None
        self.sprzedawca_imie:str = None
        self.sprzedawca_data_od_kiedy_na_otomoto:str = None

        # DETAILS
        self.details:dict = None

        # EQUIPMENT
        self.equipment:dict = None


    def check_data_integrity(self):
        pass