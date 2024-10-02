from dataclasses import dataclass, fields

@dataclass
class OFFER:
    def __repr__(self) -> str:
        repr_str =  (f"<class: OFFER>\n"
                f"Link: {self.link}\n"
                f"Tytuł: {self.tytul}\n"
                f"Data Dodania: {self.data_dodania}\n"
                f"Sprzedajacy Imie: {self.sprzedawca_imie}\n"
                f"Ilosc Szczegółów: {len(self.szczegoly)}\n"
                f"Ilosc Wyposazenia: {len(self.wyposazenie)}\n"
                f"Koordynaty: LAT: {self.latitude} LONG: {self.longitude}\n"
                )
        missing_fields = self.no_data_for_fields()
        if missing_fields:
            repr_str += f"Brakujące pola: {', '.join(missing_fields)}"
        else:
            repr_str += "Brakujące pola: Brak"

        return repr_str
    link:str 
    id_w_linku:str = None
    data_dodania:str = None
    id_oferty:int = None
    tytul:str = None

    cena:float = None
    przebieg:int = None
    rodzaj_paliwa:str = None
    skrzynia_biegow:str = None
    typ_nadwozia:str = None
    pojemnosc_silnika:int = None
    moc_silnika:int = None

    opis:str = None

    # DETAILS
    szczegoly:dict = None

    # EQUIPMENT
    wyposazenie:list = None

    # Seller info
    sprzedawca_nr_tel:int = None
    sprzedawca_imie:str = None
    sprzedawca_rodzaj:str = None
    sprzedawca_data_od_kiedy_na_otomoto:str = None

    # Offer coordinates
    latitude:float = None
    longitude:float = None
    coords_exact:bool = None
        
    def no_data_for_fields(self) -> list:
        return [field.name for field in fields(self) if getattr(self, field.name) is None]


    def check_data_integrity(self):
        pass

    @property
    def offer_info_dict(self) -> dict:
        pass