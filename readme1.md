# Analyzátor kódu `parse.py`

## Zvolené programovací paradigma a užití knihoven

Necelých 600 řádků mojí implementace `parse.py` je napsána asi z poloviny
procedurálně a z poloviny objektově. Výhodu použití objektů v této uloze vidím
zejména zapouzdření dat do logických celků.

Konstruktory těchto objektů také poskytují mírnou abstrakci různých
sémantických a lexikálních kontrol, což vedlo k čistějšímu procedurálnímu kódu,
který tyto objekty vytvářel.

Pro některé lexikální kontroly, které nebylo možné dostatečně jednoduše
implementovat pomocí vestavěných funkcí, jsem importoval knihovnu pro regulární
výrazy (modul `re`).

## Postup analyzování

Procedurální kód zpracovával vstupní program řádek po řádku. Každý řádek
byl rozdělen na jednotlivé lexémy (`.split()`) a pro každý řádek byl vytvořen
objek třídy `Instruction`.

Tímto se vytvořilo pole objektů třídy `Instruction`. Odkaz na toto pole se pak
předal funkci `generate_xml_tree`, které z pole vytvořila strom objektů třídy
`Element`. Toto pole se pak jedním voláním `print_xml` proměnilo
ve výstupní XML reprezentaci.

## Tvorba XML

XML se v mém programu generuje rekurzivně z objektů třídy `Element`, které
tvoří strom, kde každý uzel má 0 až n potomků následovně:
- uzel vypíše svoji otevírací značku včetně atributů
- jeden po druhém spustí generování XML pro každého ze svých potomků
- uzel vypíše svůj vnitřní obsah (použita funkce `xml_safe`)
- uzel vypíše svoji zavárací značku

Tento postup jsem zvolil protože je dostatečně jednoduchý a eliminuje
starosti se sháněním správné verze správné knihovny. Navíc nebylo třeba učit se
používat knihovnu.

## Třídy

Můj prográm má třídy `Element`, `Instruction` a `Operand`.

![Diagram tříd](./img/class_diagram.svg)

### Třída `Element`

Objekty třídy `Element` obsahují název značky, odkaz na vyhledávací tabulku
svých atributů, pole odkazů na své potomky a svůj vnitřní obsah.

Kromě metod nastavujících tyto položky je dostupná metoda `print_xml`, která
rekurzivně vytiskne danou instanci, jak je popsáno výše.

### Třída `Instruction`

Objekty třídy `Instruction` obsahují svůj operační kód a odkaz na pole
jejich argumentů, které je tvořeno objekty třídy `Operand`

### Třída `Operand`

Objekty třídy `Operand` obsahují svůj typ (label, type, var, int, bool, string,
nil) a jejich hodnotu (tato hodnota bude obsah XML elementu `argn`).

Konstruktor pro objekty třídy `Operand` má jako parametr `exp`, tedy očekávaný
typ pro daný lexém. Podle toho se například konstruktor rozhodne, jestli
argument `"int"` bude typu *type* nebo *label*. Pokud má argument pro daný
očekávaný typ neplatný formát, konstrukce selže a program je násilně ukončen.

---

Vít Pavlík (`xpavli0a`), 18. 2. 2024
