Nowe elementy języka
====================

Structured bindings
-------------------

W C++17 można zdefiniować i jednocześnie zainicjować wiele zmiennych przy pomocy tzw. *structured binding*.

Typy zmiennych są dedukowane za pomocą mechanizmu ``auto``.


Typy wiązań
~~~~~~~~~~~

Do realizacji wiązania mogą być użyte:

1. Wszystkie elementy tablicy

   .. code-block:: c++
    
      auto foo() -> int(&)[2];

      auto [first, second] = foo();

2. Wszystkie elementy krotki lub obiektu kompatybilnego typu (np. std::pair, std::array)
   
   * std::tuple
   
     .. code-block:: c++
  
        std::tuple<int, std::string, double> tpl(1, "text"s, 2.3);
        
        auto [first, second, third] = tpl;

        std::cout << first << " " << second << " " << third << '\n';

   * std::pair

     .. code-block:: c++

        std::set<int> unique_numbers = get_numbers();

        if (auto [pos, is_inserted] = unique_numbers.insert(1), is_inserted)
            std::cout << (*pos) << " has been inserted\n";        

   * std::array

     .. code-block:: c++

        std::array<int, 4> get_data();

        auto [i, j, k, l] = get_data();

        auto [i, j, k] = get_data(); // ERROR - number of items doesn't fit

   Takie wiązanie jest realizowane tylko jeśli ``std::tuple_size<E>`` jest typem 
   kompletnym (``E`` jest typem krotki lub kompatybilnego obiektu)


3. Wszystkie niestatyczne składowe obiektu klasy/struktury/unii
   
   - wszystkie składowe muszą być publiczne i być bezpośrednio zdefiniowane w klasie/strukturze wiązanego obiektu lub
     w jego klasie bazowej
   - anonimowe unie nie są dozwolone

   .. code-block:: c++

        struct Data
        {
            int n;
            char c;
            double d;
        };

        //...

        Data data1 { 1, 'A', 3.14 };

        auto [member1, member2, member3] = data1;

        std::cout << member1 << " " << member2 << " " << member3 << '\n';

Jeśli liczba zmiennych umieszczonych w nawiasach ``[]`` nie zgadza się z liczbą 
składowych obiektu zwróconego, kompilator zgłasza błąd.

Mechanizm wiązania *structured binding*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Mechanizm działania wiązania *structured binding* wykorzystuje nową (anonimową) zmienną, a nowe identyfikatory wprowadzone w wiązaniu
odwołują się do pól tej anonimowej zmiennej.

Kod wiązania:

.. code-block:: c++

    struct Timestamp
    {
        int hours, minutes, seconds;
    };

    Timestamp timestamp{12, 0, 30};

    auto [h, m, s] = timestamp;

Odpowiada koncepcyjnie:

.. code-block:: c++

    auto e = timestamp;
    auto& h = e.hours;
    auto& m = e.minutes;
    auto& s = e.seconds;

Obiekt ``e`` istnieje tak długo jak istnieją zdefiniowane do niego wiązania.

Kwalifikatory dla wiązań
~~~~~~~~~~~~~~~~~~~~~~~~

Deklaracje *structured bindings* mogą być dekorowane kwalifikatorami w postaci referencji, modyfikatorów ``const`` oraz ``volatile``, ``alignas``, 
przy czym dekoracja taka dotyczy całego anonimowego obiektu:

.. code-block:: c++

    int a[] = { 42, 13 };

    auto [x, y] = a;

    auto& [rx, ry] = a; // rx and ry refer to the elements in a

    const auto [v, w] = a; // v and w have type const int, initialized by the elements of a

    alignas(128) auto[id, pi] = std::tuple(1, 3.14); // id and pi refers to implicit entity, which is 128-byte aligned

    auto& [id, name] = std::make_tuple(1, "John"s); // ERROR - cannot bind auto& to rvalue std::tuple
    
    auto&& [id, name] = std::make_tuple(1, "John"s); // OK


Semantyka przenoszenia
~~~~~~~~~~~~~~~~~~~~~~

Aby przenieść obiekt do anonimowej zmiennej należy użyć następującej konstrukcji:

.. code-block:: c++

    auto [h, m, s] = std::move(ts);

W przypadku, kiedy użyjemy specyfikatora ``auto&&``, obiekt ``ts`` wciąż, przechowuje dane, ponieważ obiekt tymczasowy jest 
referencją do r-value:

.. code-block:: c++

    Timestamp ts{12, 40, 0};
    
    auto&& [h, m, s] = std::move(ts); // entity is a r-value ref to ts


Praktyczne wykorzystanie *structured bindings*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. *Structured bindings* umożliwiają wygodną iterację po mapach w C++17:

   .. code-block:: c++

       std::map<std::string, double> data = { { "pi"s, 3.14 }, { "e"s, 2.71 } };

       for (const auto& [key, value] : data)
           std::cout << key << " - " << value << "\n";

2. Inicjalizacja wielu wartości na raz w instrukcji ``for``:

   .. code-block:: c++

       std::vector vec = { 1, 2, 3 };

       for (auto[i, it] = std::tuple{ 0, begin(vec) } ; i < size(vec); ++i, ++it)
       {
           cout << i << " - " << *it << "\n";
       }

Instrukcje if oraz switch z sekcją inicjującą
---------------------------------------------

W C++17 wprowadzono dodatkową składnię dla instrukcji ``if`` oraz ``switch`` umożliwiającą zgrupowanie instrukcji inicjującej oraz sprawdzającej warunek.

Nowa (dodatkowa) składnia:

.. code-block:: c++

    if (init; condition) 
    {}

    switch(init; condition)
    {}

W efekcie kod, który w C++98 wyglądał tak:

.. code-block:: c++

    Status status = g.status();

    if (status == Status::bad)
    {
        std::cerr << "Gadget is broken(status=" << static_cast<int>(status) << std::endl;        
    }

możemy zastąpić bardziej zwięzłym kodem:

.. code-block:: c++

    if (Status status = g.status(); status == Status::bad)
    {
        std::cerr << "Gadget is broken(status=" << static_cast<int>(status) << std::endl;        
    }

Przykład wykorzystania nowej wersji instrukcji ``if`` w pracy z muteksami:

.. code-block:: c++

    if (std::lock_guard<std::mutex> lk{mtx}; !q.empty())
    {
        std::cout << q.front() << std::endl;
    }

Instrukcja ``switch`` z nową składnią:

.. code-block:: c++

    switch (Gadget g{2}; auto s = g.status())
    {
    case Status::on:
        cout << "Gadget is on" << endl;
        break;
    case Status::off:
        cout << "Gadget is off" << endl;
        break;
    case Status::bad:
        cout << "Gadget is broken" << endl;
        break;
    }

Obiekty tymczasowe w sekcji inicjującej
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Obiekt tymczasowy utworzony na potrzeby inicjalizacji istnieje tylko w obrębie sekcji
inicjującej (tak jak w pętli ``for``).

Przykład z *bugiem*:

.. code-block:: c++

    if (std::lock_guard<std::mutex>(mtx); !q.empty()) // ERROR - locks ends before ;
    {
        std::cout << q.front() << std::endl;
    }

Poprawiony kod:

.. code-block:: c++

    if (std::lock_guard<std::mutex> _(mtx); !q.empty()) // OK - lock has name
    {
        std::cout << q.front() << std::endl;
    }

lub

.. code-block:: c++

    if (std::lock_guard lk(mtx); !q.empty())
    {
        std::cout << q.front() << std::endl;
    }

Structured bindings i if z sekcją inicjującą
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instrukcja ``if`` z sekcją inicjującą może być połączona z przypisaniem wielu wartości do zmiennych za pomocą *structured bindings*:

.. code-block:: c++

    map<int, string> dictionary;

    if (auto [pos, is_inserted] = dictionary.insert(pair(42, "fourty two"s); !is_inserted)
    {
        const auto& [key, value] = *pos;

        cout << key << " is already in a dictionary" << endl;
    }

constexpr if
------------

C++17 wprowadza do standardu C++ nową postać instrukcji warunkowej ``if``, która działa na etapie kompilacji - tzw. ``constexpr if``.

Działanie ``constexpr if`` polega na wyborze podczas kompilacji bloku instrukcji ``then``/``else`` w zależności od warunku, który jest wyrażeniem ``constexpr``.

Składnia:

.. code-block:: c++

  if constexpr(condition)
  {
     // ...
  }
  else
  {
     // ...
  }

``constexpr if`` umożliwia znaczne uproszczenie kodu szablonowego, który bardzo często w C++11 był mocno skomplikowany.

Przykład w C++11:

.. code-block:: c++

    template<class T>
    auto compute(T x) -> enable_if_t<supportsAPI<T>::value, int>
    {
        return optimized_computation(x);
    }

    template<class T>
    auto compute(T x) -> enable_if_t<!supportsAPI<T>::value, int>
    {
        return generic_computation(x);
    }

Powyższy kod może być dużo prościej wyrażony w C++17 za pomocą ``constexpr if``:

.. code-block:: c++

    template<class T>
    auto compute(T x) 
    {
        if constexpr(supportsAPI<T>::value)
        {
            return optimized_computation(x);
        }
        else
        {
            return generic_computation(x);
        }
    }

Discarded statements
~~~~~~~~~~~~~~~~~~~~

Kod (grupa instrukcji), który jest ominięty przy kompilacji (tzw. *discarded statement*), nie jest instancjonowany, ale musi być poprawny składniowo.
Mechanizm *constexpr if* zasadniczo odpowiada pierwszemu etapowi przetwarzania szablonów przez kompilator (faza definicji).

.. code-block:: c++
 
    template <typename T>
    void foo(T obj);

    void f_with_discarded_statements()
    {
        if constexpr(std::numeric_limits<char>::is_signed) 
        {
            foo(42);
            static_assert(std::numeric_limits<char>::is_signed, "char is unsigned"); // always fails if char is unsigned
        }   
        else
        {
            undeclared(42);  // always error if undeclared() not declared
            static_assert(!std::numeric_limits<char>::is_signed, "char is signed"); // always fails if char is signed
        }
    }

Powyższy kod nigdy się nie skompiluje.

Mechanizm kompilacji szablonów
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Faza pierwsza:
   
   - wykrywane są błędy składniowe
   - użycie nieznanych typów, funkcji, itp. generuje błąd kompilacji
   - sprawdzane są statyczne asercje

2. Faza druga:
 
   - kod zależny od parametru szablonu jest podwójnie sprawdzany

.. code-block:: c++

    template <typename T>
    void foo(T t)
    {
        undeclared();
        undeclared(t);

        static_assert(sizeof(int) > 4, "small int"); // 1st phase error if sizeof(int) <= 4
        static_assert(sizeof(T) > 4, "small T"); // 2nd phase error if sizeof(T) <= 4
        static_assert(false, "Error"); // always fails when template is compiled (even if not called)
    }


Zmienne inline
--------------

W C++17 statyczne zmienne oznaczone jako ``inline`` są uznawane jako definicja takiej zmiennej w programie.

* gwarantowana jest jednokrotna definicja zmiennej nawet wtedy, gdy nagłówek z definicją jest włączany w wielu jednostkach translacji
* nie musimy tworzyć pliku *cpp* tylko na potrzeby definicji zmiennych globalnych/statycznych

* Plik ``gadget.hpp``

.. code-block:: c++

    class Gadget
    {
    public:
        static size_t count() 
        {
            return counter_;
        }
    private:
        Gadget() 
        {
            ++counter_;
        }

        Gadget(const Gadget&) = delete;
        Gadget& operator=(const Gadget&) = delete;

        ~Gadget()
        {
            --counter_;
        }

        static inline size_t counter_ = 0;
        static inline std::string class_id = "Gadget";
    };

* Plik ``a.cpp``

.. code-block:: c++

    #include "gadget.hpp"
    #include <iostream>

    int main()
    {
        std::cout << "No of gadgets: " << Gadget::count() << std::endl;
    }
    
* Plik ``b.cpp``

.. code-block:: c++

    #include "gadget.hpp"

    void bootstrap(GadgetFactory& gf)
    {
        gf.register(Gadget::class_id, &make_unique<Gadget>);
    }

Zmienne statyczne ``inline`` mogą być:

* inicjalizowane przed funkcją ``main()`` lub przed pierwszym użyciem
* mogą być ``thread_local``
* modyfikator ``constexpr`` implikuje, że zmienna statyczna jest ``inline``

Przykład (plik ``monitor.hpp``):

.. code-block:: c++

    class Monitor
    {
    public:
        Monitor() { /* ... */ };

        void log(const std::string& msg);
    };

    inline thread_local Monitor global_monitor;

Agregaty w C++17
----------------

C++17 rozszerza definicję agregatu:

* Agregaty w C++17 mogą posiadać klasy bazowe, po których dziedziczą publicznie
* Inicjalizacja jest możliwa za pomocą zagnieżdżonych klamr ``{}``
* Biblioteka standardowa dostarcza nową cechę (*trait*) - ``is_aggregate<T>``

.. code-block:: c++

    struct Base1 
    { 
        int b1;
        int b2 = 42; 
    };
    
    struct Base2 
    {
        Base2() 
        {
            b3 = 42;
        }
        
        int b3;
    };

    struct Derived : Base1, Base2 
    {
        int d;
    };
    
    Derived d1{{1, 2}, {}, 4}; // d1.b1 = 1,  d1.b2 = 2, d1.b3 = 42, d1.d = 4
    Derived d2{{}, {}, 4}; // d2.b1 = 0, d2.b2 = 42, d2.b3 = 42, d2.d = 4


* Klasy bazowe oraz składowe agregatów nie muszą być w C++17 agregatami (znaczne obniżenie wymagań)

.. code-block:: c++

    template <typename T>
    struct Aggregate : std::string, std::complex<T> 
    {
        std::string data;
    };

    Aggregate<double> agg1{ {"aggregate"}, {4.5, 6.7}, "test" };

Definicja agregatu w C++17
~~~~~~~~~~~~~~~~~~~~~~~~~~

C++17 definiuje agregat jako:

* tablicę

* lub klasę(``class``, ``struct``, lub ``union``), która:

  – nie posiada konstruktorów ``explicit`` lub zdefiniowanych przez użytkownika
  
  – nie posiada konstruktorów odziedziczonych deklaracją ``using``
  
  – nie posiada prywatnych lub chronionych niestatycznych danych składowych
  
  – nie posiada wirtualnych funkcji składowych 
  
  – nie posiada wirtualnych, prywatnych lub chronionych klas bazowych

Dodatkowo, inicjalizacja agregatu, nie może wykorzystywać prywatnych lub chronionych konstruktorów klasy bazowej.


Return Value Optimization & Copy Elision
----------------------------------------

* W C++17 wymagane jest, aby inicjalizacja zmiennych z wartości tymczasowych (*prvalue*) wykorzystywała
  mechanizm *copy elision*.

* W rezultacie istnienie konstruktorów kopiujących lub przenoszących dla klasy nie jest
  wymagane jeśli chcemy:
  
  * zwrócić tymczasowy obiekt z funkcji
  * przekazać obiekt tymczasowy jako argument wywołania funkcji

Przykład:

.. code-block:: c++

    class CopyMoveDisabled
    {
    public:
        int value;
        CopyMoveDisabled(int value) : value{value} {}
        CopyMoveDisabled(const CopyMoveDisabled&) = delete;
        CopyMoveDisabled(CopyMoveDisabled&&) = delete;
    };

* *Copy elision* dla zwracanych wartości:

.. code-block:: c++

    CopyMoveDisabled copy_elided()
    {
        return CopyMoveDisabled{42};
    }

    CopyMoveDisabled cmd = copy_elided(); // OK since C++17

* *Copy elision* dla argumentów funkcji:

.. code-block:: c++

    void copy_elided(CopyMoveDisabled arg)
    {
        cout << "arg: " << arg.value << endl;
    }

    copy_elided(CopyMoveDisabled{665}); // OK since C++17

.. note:: Wciąż **nie jest wymagana** optymalizacja kopiowań dla NRVO (gdy zwracane są lokalne obiekty)

Kategorie wartości w C++17
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. image:: images/expression-categories-cpp-17.svg
   :align: center

W C++17 każde wyrażenie należy do jednej z kategorii:

* **glvalue** - *generalized lvalue*

* **lvalue** - lokalizowalna wartość
  
  - zmienna, pole obiektu, funkcja, zwrócona referencja do lvalue
  - może stać po lewej stronie operatora przypisania (jeśli nie jest stałą)

* **rvalue** - *generalized rvalue*

* **prvalue** - wykonuje inicjalizację

  - literały, ``this``, lambda, zwrócona z funkcji wartość, efekt wywołania konstruktora
  - nie powoduje powstania obiektu tymczasowego

* **xvalue** - *eXpiring value*

  - zwrócona referencja do rvalue (np. efekt wywołania ``std::move()``)

Materializacja do obiektu tymczasowego
**************************************
  
Konwersja **prvalue-to-xvalue**:

- przy wiązaniu do referencji
- przy próbie dostępu do składowej
- przy konwersji do klasy bazowej

.. code-block:: c++

    MyClass create()
    {
        return MyClass(); // returns prvalue (no temporary object yet)
    }

    MyClass x = create(); // uses prvalue for initialization

    void call_v(MyClass obj); // accepts any value category
    void call_r(const MyClass& obj); // requires glvalue
    void call_m(MyClass&& obj); // requires xvalue (may be materialized from prvalue)

    call_v(create()); // passes prvalue and uses it for initialization of obj
    call_r(create()); // passes prvalue (materialized as xvalue) 
    call_m(create()); // passes prvalue(materialized as xvalue)

Atrybuty
--------

Standard C++17 wprowadza kilka nowych atrybutów, które umożliwiają lepszą kontrolę nad
interpretacją kodu przez kompilator:

* atrybut ``[[ nodiscard ]]``

  - wymusza zgłoszenie ostrzeżenia w przypadku, gdy zwracana wartość nie jest użyta

  .. code-block:: c++
  
      template <typename F, typename... Args>
      [[nodiscard]] future<decltype(F())> async(F&& f, Args&&...);

* atrybut ``[[ maybe_unused ]]``

  - dezaktywuje ostrzeżenia o nieużywanej zmiennej, jeśli taka jest intencja programisty

    .. code-block:: c++

        [[maybe_unused]] int x = foo();

* atrybut ``[[ fallthrough ]]``

  - używany w instrukcji ``switch``, gdy wybrana etykieta ``case`` zawiera instrukcje, ale nie kończy się
    instrukcją ``break``
  - musi poprzedzać inną etykietę  ``case`` (jeśli nie, kod jest *illformed*)

  .. code-block:: c++

      void f(int n)
      {
          switch (n) {
            case 1:
            case 2:
                step1();
                [[fallthrough]];
            case 3: // no warning on fallthrough
                step2();
            case 4: // compiler may warn on fallthrough
                step3();
                [[fallthrough]]; // ill­formed, not before a case label
        }
      }

* atrybut ``[[ deprecated ]]`` może być stosowany dla przestrzeni nazw oraz wyliczeń:

  .. code-block:: c++

     enum Coffee {
        espresso = 1,
        americano [[deprecated]] = espresso
     };
  
     namespace [[deprecated]] LegacyCode
     {
        // ...
     }

* deklaracja ``using`` dla atrybutów

  .. code-block:: c++

       [[using CC: opt(1), debug]] // same as [[CC::opt(1), CC::debug]]
       [[using CC: CC::opt(1)]] // error: cannot combine using and scoped attribute

Zagnieżdżone przestrzenie nazw
------------------------------

Dozwolona jest nowa składnia przy zagnieżdżaniu przestrzeni nazw.

* Zamiast:

  .. code-block:: c++

      namespace A {
          namespace B {
              namespace C {
                  // ...
              }
          }
      }

* można napisać:

  .. code-block:: c++

     namespace A::B::C {
         // ...
     }

Statyczne asercje bez komunikatów o błędach
-------------------------------------------

Od C++17 ``static_assert()`` nie wymaga przekazania komunikatu o błędzie. Jeśli asercja nie jest zaliczona, 
wyświetlany jest komunikat domyślny.

.. code-block:: c++

    static_assert(sizeof(int) >= 4, "integers are to small");  // OK since C++11
    static_assert(sizeof(int) >= 4); // OK since C++17

Lambdy w C++17
--------------

Przechwytywanie this
~~~~~~~~~~~~~~~~~~~~

Można użyć trzech opcji, aby przechwycić wskaźnik ``this`` w funkcjach składowych:

.. code-block:: c++

    class Gadget
    {
        std::string name_;
    public:
       void do_sth()
       {
           execute([] { std::cout << name_ << std::endl; }); // ERROR - this is not captured
           execute([&] { std::cout << name_ << std::endl; }); // OK - this captured implicitly by &
           execute([=] { std::cout << name_ << std::endl; }); // OK - this captured implicitly by =
           execute([this] { std::cout << name_ << std::endl; }); // OK - this captured explicitly
       }
    };

Od C++17 przy pomocy ``*this`` możemy przechwycić kopię obiektu:

.. code-block:: c++

    execute([*this] { std::cout << name_ << std::endl; }) / OK since C++17 - local copy of *this

Lambdy constexpr
~~~~~~~~~~~~~~~~

Od C++17 wyrażenia lambda są traktowane domyślnie jako wyrażenia ``constexpr`` (jeśli jest to możliwe).
Można explicite zastosować również słowo kluczowe ``constexpr`` w definicji lambdy.

.. code-block:: c++

    auto squared = [](auto x) { return x * x; } // implicitly consexpr

    std::array<int, squared(8)> arr1; // OK - array<int, 64>

    auto squared = [](auto x) constexpr { // OK - since C++17
        return x * x;
    };

Jeśli w definicji wyrażenia lambda nie są spełnione wymagania dla wyrażeń ``constexpr``, to kompilator:

- domyślnie przyjmie, że definicja lambdy nie jest ``constexpr``

  .. code-block:: c++

      auto is_even = [](int x) { 
          static size_t counter = 0;
          counter++;
          //...
          return x % 2 == 0;
      }; // OK - but not constexpr
  
- lub w przypadku jawnej deklaracji ``constexpr`` zgłosi błąd kompilacji

  .. code-block:: c++

      auto is_even = [](int x) constexpr { 
          static size_t counter = 0;
          counter++;
          //...
          return x % 2 == 0;
      }; // ERROR - lambda expression is not constexpr


Literały
--------

Literały UTF-8
~~~~~~~~~~~~~~

* Prefix ``u8`` dla znaku umożliwia zdefiniowanie znaku w kodowaniu UTF-8
  
  - typ ``char``
  - literał może mieć tylko jeden znak (np. ASCII)
  - wartość jest równa kodowi znaku UTF-8 wg normy ISO 10646

.. code-block:: c++

    auto c = u8'a'; // char 'a'

Literały szesnastkowe
~~~~~~~~~~~~~~~~~~~~~

* Prefix ``0x`` definiuje literały szesnastkowe również dla typów zmiennoprzecinkowych (tak jak w C99)
  
  - mantysa jest podawana szesnastkowo
  - eksponenta jest podawana w notacji dziesiętnej (zmiennoprzecinkowej) i jest potęgą 2

.. code-block:: c++

    auto hex1 = 0xA; // int: 10
    auto hex2 = 0x1p4; // double: 1 * 2^4 = 16
    auto hex3 = 0x1.4p+2; // double: 5
    auto hex4 = 0xC.68p+2; // double: 49.625