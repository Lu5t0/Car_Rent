

# Sistem de Închirieri Mașini (Car Rental System)

Un sistem complet de gestionare a închirierilor de mașini, destinat utilizatorilor și superuserilor. Permite utilizatorilor să vizualizeze și să caute mașini, să închirieze și să returneze vehicule, iar superuserilor să adauge sau să elimine mașini, producători și imagini, precum și să gestioneze utilizatorii și rezervările.

---

## Funcționalități principale

- **Get all cars**: Vizualizează toate mașinile disponibile.
- **Search by car model**: Caută mașini după model.
- **Get all manufacturers**: Obține lista tuturor producătorilor.
- **Search by manufacturer name**: Caută producători după nume.
- **Top rented cars**: Afișează cele mai închiriate mașini.
- **My rentals**: Vizualizează închirierile proprii ale utilizatorului.
- **Rent car**: Închiriază o mașină.
- **Return car**: Returnează o mașină închiriată.
- **Reset password**: Resetează parola utilizatorului.
- **Logout**: Deconectează utilizatorul.

## Funcții pentru superuser

- **Add car / Delete car**: Adaugă sau șterge mașini.
- **Add manufacturer / Delete manufacturer**: Adaugă sau șterge producători.
- **Add car image / Delete car image**: Gestionează imaginile mașinilor.

---

## Cerințe

- Python 3.8 sau mai recent
- pip (gestionarea pachetelor Python)

---

## Instalare
Instalarea dependențelor
pip install -r requirements.txt

### Crearea fișierului `.env` pentru configurarea bazei de date

In directorul `Car_Rent/my_rent_car_project/my_rent_car_project`, creează un fișier numit `.env` și completează-l cu datele de conectare ale bazei tale de date:

**Exemplu:**

DB_NAME=nume_baza_de_date  
DB_USER=username  
DB_PASSWORD=parola  
DB_HOST=localhost  
DB_PORT=3306

---


După aceea, rulează următoarele comenzi pentru a crea și aplica migrațiile:

```bash
python manage.py makemigrations
python manage.py migrate
```
Pentru a putea accesa panoul de administrare , creează un superuser in terminalul python:

```bash
python manage.py createsuperuser
```
### Asigură-te că ești în directorul `Car_Rent/my_rent_car_project`

Dacă nu ești deja în acest director, rulează următoarea comandă pentru a te deplasa:

```bash
cd Car_Rent/my_rent_car_project
```
### Pornește serverul pentru a testa aplicația

Rulează următoarea comandă:

```bash
python manage.py runserver
```

### Apoi, accesează aplicația la adresa: localhost:8000
