C++17 - poprawki standardu
==========================

Zdefiniowana kolejność ewaluacji wyrażeń
----------------------------------------

Kolejność ewaluacji wyrażeń dla wielu operatorów w C++ była niezdefiniowana w standardzie. 
W efekcie przewidzenie wyniku wykonania operacji korzystającej z takich operatorów było w zasadzie niemożliwe.

Oto kilka przykładów:

.. code-block:: c++

    std::map<int, int> dict;
    dict[0] = dict.size(); // after statement: dict = { {0, 0} } or { { 0, 1} }


.. code-block:: c++

    std::string s = "but I have heard it works even if you don’t believe in it";
    s.replace(0, 4, "").replace(s.find("even"), 4, "only").replace(s.find(" don’t"), 6, "");
    assert(s == "I have heard it works only if you believe in it"); // it may fail

.. code-block:: c++

    std::cout << f() << g() << h();  // UB: undefined evaluation of order

    std::cout.operator<<(f()).operator<<(g()).operator<<(h());

Reguły ewaluacji wyrażeń w C++17
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

C++17 definiuje następujące reguły ewaluacji:

* Wyrażenia postfix są ewaluowane od lewej do prawej. Dotyczy to również wywołań funkcji i wyrażeń związanych z wyborem składowej klasy (struktury).
* Wyrażenia przypisania są ewaluowane od prawej do lewej.
* Operandy dla operatorów przesunięć są ewaluowane od lewej do prawej.

W rezultacie następujące wyrażenia są ewaluowane w kolejności **a**, potem **b**, potem **c** a następnie **d**:

* ``a.b``
* ``a->b``
* ``a->*b``
* ``a(b1, b2, b3)``
* ``b @= a``
* ``a[b]``
* ``a << b``
* ``a >> b``

Dodatkowo wprowadzono regułę, że kolejność ewaluacji wyrażeń zawierających przeciążone operatory jest określona tak jak w przypadku
odpowiednich operatorów wbudowanych, a nie przez reguły związane z wywołaniami funkcji.

W rezultacie wyrażenie: 

.. code-block:: c++

    s.replace(0, 4, "") // 1-st
     .replace(s.find("even"), 4, "only") // 2nd
     .replace(s.find(" don’t"), 6, ""); // 3rd

jest ewaluowane w określony sposób, ale kolejność ewaluacji argumentów wywołań metody ``replace()`` wciąż nie jest specyfikowana przez standard.

Inicjalizacja typów wyliczeniowych
----------------------------------

Dla typów wyliczeniowych z określonym typem całkowitym (*fixed underlying type*) standard C++17 dopuszcza
bezpośrednią inicjalizację listową (*direct list initialization*) wartością całkowitą. Dotyczy to zarówno klasycznych wyliczeń ``enum``, jak i
wprowadzonych w C++11 wyliczeń ``enum class``.

Dla klasycznych typów wyliczeniowych ``enum`` bez określonego typu całkowitego taka inicjalizacja wciąż jest traktowana jako błąd kompilacji.

.. code-block:: c++

    enum class Coffee { espresso, cappucino, dopio };

    Coffee c1 = 0; // ERROR (all versions)
    Coffee c2(0);  // ERROR (all versions)
    Coffee c3{0};  // OK since C++17


    enum class GuitarType : char { stratocaster, les_paul };

    GuitarType gt1 = 1; // ERROR (all versions)
    GuitarType gt2(1);  // ERROR (all versions)
    GuitarType gt3{1}; // OK since C++17


    enum EngineType { diesel, petrol, wankel };

    // EngineType e1 = 0; // ERROR (all versions)
    // EngineType e2(0); // ERROR (all versions)
    // EngineType e3{2}; // ERROR (all versions)


    enum MovieFormat : char { divx, mpeg };

    // MovieFormat mv1 = 1; // ERROR (all versions)
    // MovieFormat mv2(1); // ERROR (all versions)
    MovieFormat mv3{1}; // OK since C++17

Definiowanie nowych typów całkowitych za pomocą wyliczeń
--------------------------------------------------------

W C++17 można użyć typu wyliczeniowego do zdefiniowania nowego typu całkowitego niepodlegającego niejawnym konwersjom.

.. code-block:: c++

    enum length_t : size_t {}; // new distinct integral type with some restrictions

    length_t x; // OK
    length_t x1(9); // ERROR
    length_t x2{42}; // OK
    length_t x3{-19}; // ERROR (narrowing)
    length_t x4 = 665; // ERROR
    length_t x5 = length_t(665); // OK
    length_t x6 = static_cast<length_t>(665); // OK

    x = 42; // ERROR
    x = length_t(42); // OK
    x = x2; // OK

    if (x == x2) // OK
    {
        int a = x; // OK for enum but ERROR for enum class
        cout << x << endl; // OK for enum but ERROR for enum class
        cout << x + x << endl; // OK for enum but ERROR for enum class
        x2 = x + x; // ERROR        
    }


Inicjalizacja listowa i auto
----------------------------

W C++17 zmieniona została reguła dotycząca automatycznej detekcji typu w przypadku inicjalizacji bezpośredniej za pomocą inicjalizacji listowej.

W C++11/14:

.. code-block:: c++

    int x1(42); // direct initialization with C++98/03 syntax
    int x2{42}; // direct initialization with C++11
    int x3 = 665; // copy initialization

    auto a1(42); // direct initialization -> int
    auto a2{42}; // direct initialization -> initializer_list<int>
    auto a3{42, 665}; // direct initialization -> initializer_list<int>

    auto a4 = 42; // copy initialization -> int
    auto a5 = {42}; // copy initialization -> initializer_list<int>
    auto a6 = {42, 665}; // copy initialization -> initializer_list<int>

Po zmianie reguły w C++17:

.. code-block:: c++

    auto a1(42); // direct initialization -> int
    auto a2{42}; // direct initialization -> int (new rule!!!)
    auto a3{42, 665}; // ERROR

    auto a4 = 42; // copy initialization -> int
    auto a5 = {42}; // copy initialization -> initializer_list<int>
    auto a6 = {42, 665}; // copy initialization -> initializer_list<int>

Zalety inicjalizacji bezpośredniej z {}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* działa z każdym typem
  
  - również z typami wyliczeniowymi
  - również z agregatami posiadającymi klasy bazowe

* wykrywane są konwersje zawężające (inicjalizacja zmiennej ``int`` wartością typu ``float``)
* bezpośrednia inicjalizacja w połączeniu z mechanizmem ``auto`` działa prawidłowo od C++17

noexcept jako część typu funkcji
--------------------------------

System typów w C++17 uwzględnia specyfikację ``noexcept`` dla funkcji.

.. code-block:: c++

    void func1();
    void func2() noexcept;

    static_assert(is_same_v<decltype(func1), decltype(func2)>); // ERROR - different types

    void (*fp)() noexcept;

    fp = func2(); // OK
    fp = func1(); // ERROR since C++17

Zmiana ta może spowodować, że kod z C++14 może się nie skompilować w C++17:

.. code-block:: c++

    template <typename F>
    void call(F f1, F f2)
    {
        f1();
        f2();
    }

    call(func1, func2); // ERROR since C++17


Elementy usunięte ze standardu
------------------------------

* Trigrafy
* Operator ++ dla typu ``bool``
* Słowo kluczowe ``register``
* Specyfikacja rzucanych wyjątków z listą typów
  
  .. code-block:: c++

      void foo() throw(std::bad_alloc); // invalid since C++17
      void foo() throw(); // OK - but no stack unwinding guarantee
  