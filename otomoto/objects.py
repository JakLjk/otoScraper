from dataclasses import dataclass

@dataclass
class OFFER:
    def __repr__(self) -> str:
        return

    link:str 
    data_dodania:str
    id:int
    tytul:str

    cena:float 
    przebieg:int
    rodzaj_paliwa:str
    skrzynia_biegow:str
    typ_nadwozia:str
    pojemnosc_silnika:int 
    moc_silnika:int

    opis:str

    # DETAILS
    szczegoly:dict

    # EQUIPMENT
    wyposazenie:list

    # Seller info
    sprzedawca_nr_tel:int = None
    sprzedawca_imie:str = None
    sprzedawca_rodzaj:str = None
    sprzedawca_data_od_kiedy_na_otomoto:str = None

    # Offer coordinates
    x_coord:float = None
    y_coord:float = None
    coords_exact:bool = None
        

    def check_data_integrity(self):
        # check like if offer id is int with 10 chars
        pass

    @property
    def offer_info_dict(self) -> dict:
        pass