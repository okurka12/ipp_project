# Analyzátor kódu `parse.py`

Tento dokument představuje podrobnou dokumentaci k&nbsp;syntaktickému analyzátoru
`parse.py`, vyvinutému jako součást projektu do předmětu IPP - Principy
programovacích jazyků a&nbsp;objektově orientovaného programování.

## Zvolené programovací paradigma a&nbsp;použité knihovny

Necelých 600 řádků této implementace `parse.py` je napsána asi z&nbsp;poloviny
procedurálně a&nbsp;z&nbsp;poloviny objektově. Výhoda použití objektů
v&nbsp;této úloze spočívá zejména v zapouzdření dat do logických celků.

Podařilo se dobře využít výhod objektově orientovaného
programování, ale zároveň příliš nekomplikovat úlohu složitým objektovým
návrhem.

Konstruktory těchto objektů také poskytují mírnou abstrakci různých
sémantických a&nbsp;lexikálních kontrol, což vedlo k&nbsp;čistějšímu
procedurálnímu kódu, který tyto objekty vytvářel.

Pro některé lexikální kontroly, které nebylo možné dostatečně jednoduše
implementovat pomocí vestavěných funkcí, byla importována knihovna pro
regulární výrazy (modul `re`).

## Postup analyzování

Procedurální kód zpracovával vstupní program řádek po řádku. Každý řádek
byl rozdělen na jednotlivé lexémy (`.split()`) a&nbsp;pro každý řádek byl
vytvořen objek třídy `Instruction`.

Tímto se vytvořilo pole objektů třídy `Instruction`. Odkaz na toto pole se pak
předal funkci `generate_xml_tree`, které z&nbsp;pole vytvořila strom objektů
třídy `Element`. Tento strom se pak jedním voláním `print_xml` proměnil
ve výstupní XML reprezentaci.

## Tvorba XML

XML se v&nbsp;programu generuje rekurzivně z&nbsp;objektů třídy `Element`,
které tvoří strom, kde každý uzel má 0&nbsp;až n&nbsp;potomků následovně:
- uzel vypíše svoji otevírací značku včetně atributů
- jeden po druhém spustí generování XML pro každého ze svých potomků
- uzel vypíše svůj vnitřní obsah (použita funkce `xml_safe`)
- uzel vypíše svoji zavárací značku

Tento postup byl zvolen, protože je dostatečně jednoduchý a&nbsp;eliminuje
starosti se sháněním správné verze správné knihovny. Navíc nebylo třeba se učit
používat knihovnu.

## Třídy

Můj prográm obsahuje třídy `Element`, `Instruction` a&nbsp;`Operand`.

![Diagram tříd](./img/class_diagram.svg)

### Třída `Element`

Objekty třídy `Element` obsahují název značky, odkaz na vyhledávací tabulku
svých atributů, pole odkazů na své potomky a&nbsp;svůj vnitřní obsah.

Kromě metod nastavujících tyto položky je dostupná metoda `print_xml`, která
rekurzivně vytiskne danou instanci, jak je popsáno výše.

### Třída `Instruction`

Objekty třídy `Instruction` obsahují svůj operační kód a&nbsp;odkaz na pole
jejich argumentů, které je tvořeno objekty třídy `Operand`

### Třída `Operand`

Objekty třídy `Operand` obsahují svůj typ (label, type, var, int, bool, string,
nil) a&nbsp;jejich hodnotu (tato hodnota bude obsah XML elementu `argn`).

Konstruktor pro objekty třídy `Operand` má jako parametr `exp`, tedy očekávaný
typ pro daný lexém. Podle toho se například konstruktor rozhodne, jestli
argument `"int"` bude typu *type* nebo *label*. Pokud má argument pro daný
očekávaný typ neplatný formát, konstrukce selže a&nbsp;program je násilně
ukončen.

---

Vít Pavlík (`xpavli0a`), 6. 3. 2024
