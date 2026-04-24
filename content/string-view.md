# Klasa std::string_view

* Nagłówek: `<string_view>`

* Lekki uchwyt dla sekwencji znaków (*read-only*)

  - czas życia danych (bufora znaków) nie jest kontrolowany przez obiekt typu `string_view`

  ```{code-block} cpp
  string_view good("text literal"); // OK - internal pointer points to static array
  string_view bad("string literal"s); // BAD - internal pointer is a dangling pointer
  ```

  - brak wsparcia dla alokatorów - nie są potrzebne
  - przekazywanie przez wartość jest efektywne
  - typowa implementacja: wskaźnik na stały znak (`const char*`) i rozmiar

* Zdefiniowane są również odpowiedniki dla innych typów znakowych niż `char`:

  - `std::wstring_view` - dla typu `wchar_t`
  - `std::u16string_view` - dla typu `char16_t`
  - `std::u32string_view` - dla typu `char32_t`

* Literał: `sv`

  - zdefiniowany w nagłówku `<literals>`
  - zdefiniowany jako `constexpr`

  ```{code-block} cpp
  auto txt = "text"sv;
  ```

* Obiekt `string_view` zapewnia podobną funkcjonalność jak `std::string`:

  - `operator[]`
  - `at()`
  - `data()`
  - `size()`
  - `length()`
  - `find()`
  - `find_first_of()`
  - `find_last_of()`

* Zapewnia operatory porównania i wyliczania skrótu (`std::hash<std::string_view>`)

## Różnice między string_view a string

* Wartość po konstrukcji domyślnej dla wewnętrznego wskaźnika to `nullptr`

  - `string::data` nie może zwrócić `nullptr`

  ```{code-block} cpp
  string_view txt;

  assert(txt.data() == nullptr);
  assert(txt.size() == 0);
  ```

* Typ `string_view` nie ma gwarancji, że bufor znaków jest zakończony zerem (*null terminated string*)

  ```{code-block} cpp
  char txt[3] = { 't', 'x', 't' };

  string_view txt_v(txt, sizeof(txt)); // this view is not null terminated
  ```

```{warning}
Dla `string_view` zawsze należy sprawdzić rozmiar operacją `size()` zanim użyty zostanie `operator[]` lub wywołana zostanie metoda `data()`
```

## Konwersje string `<->` string_view

* Konwersja `string -> string_view` jest szybka

  - dozwolona niejawna konwersja przy pomocy `std::string::operator string_view()`

* Konwersja `string_view -> string` jest kosztowna

  - wymagana jawna konwersja - `explicit std::string::string(string_view sv)`

## Użycie string_view w API funkcji

* Obiekty `string_view` przekazywane jako argumenty wywołania funkcji powinny być przekazywane przez wartość.

```{code-block} cpp
void foo_s(const string& s);
void foo_sv(string_view sv);

foo_s("text"); // computes length, allocates memory, copies characters
foo_sv("text"); // computes only length
```

* `string_view` powinno być stosowane zamiast `string` jeśli:

  - API nie wymaga, aby tekst był zakończony zerem

    - nie można przekazywać `string_view` do funkcji języka C

  - odbiorca respektuje czas życia obiektu
  - dostęp do danych przy pomocy metody `data()` uwzględnia potencjalny pusty wskaźnik (`nullptr`)

* Należy unikać zwracania `string_view`, chyba że jest to świadomy wybór programisty

  - zwrócenie `string_view` może być niebezpieczne - należy pamiętać o tym, że `string_view` jest **non-owning view**

  ```{code-block} cpp
  string_view start_from_word(string_view text, string_view word)
  {
        return text.substr(text.find(word));
  }
  ```

  Jeśli wywołamy funkcję `start_from_word()` w następujący sposób:

  ```{code-block} cpp
  auto text = "one two three"s;

  auto sv = start_from_word(text + " four", "two");
  ```

  Dostaniemy instancję `string_view` z wiszącym wskaźnikiem odnoszącym się do nieaktualnej już tablicy znaków, która 
  została zwolniona w momencie wyjścia z funkcji.

* Dostarczanie obydwu wersji funkcji jako przeciążeń może powodować dwuznaczności:

  ```{code-block} cpp
  void foo(const string& s);

  void foo(string_view sv);

  foo("ambigous"); // ERROR - ambigous call
  ```