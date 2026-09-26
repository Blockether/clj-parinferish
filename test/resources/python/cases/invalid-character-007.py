
a1 = attach(str(fix), filename="roznica.png",
            label="Przed zapisem 1 wiersz · dziś 2 wiersze i nagłówek „2 documents · 25.6KB" · propozycja 1 wiersz z „v2 · your 3 comments · just now”")
a2 = attach(str(pick), filename="warianty.png",
            label="Trzy sposoby na ten sam wiersz: A znacznik v2 · B wątek pod wierszem · C druga linia + kropki (rekomendacja)")
print(json.dumps(a1)[:400]); print(json.dumps(a2)[:400])
