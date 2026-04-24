Klasa std::optional
===================

* Nagłówek: ``<optional>``

Obiekt typu ``std::optional`` opcjonalnie przechowuje wartość określonego typu - jest pusty lub posiada określoną wartość.
W rezultacie nie ma potrzeby korzystać ze specjalnych znaczników pustej wartości (np. NULL, -1, itp.)

Tag pomocniczy - std::nullopt
-----------------------------

Klasa ``std::optional`` wykorzystuje stałą ``std::nullopt`` typu ``std::nullopt_t`` jako specjalny znacznik oznaczający brak wartości dla obiektu.

.. code-block:: c++

    inline constexpr nullopt_t nullopt{ /*unspecified*/ };

Konstruktory
------------

Obiekt ``std::optional`` może zostać skonstruowany:

* w stanie be wartości:

  .. code-block:: c++

      std::optional<std::string> o1;

      std::optional<double> o2 = std::nullopt;       

* z określoną wartością
    
  .. code-block:: c++
    
      std::optional<std::string> o3 = "text";    

      std::optional o4{42}; // deduces optional<int>

* *in-place* na podstawie listy argumentów - bez konieczności tworzenia obiektu tymczasowego

  .. code-block:: c++
    
     std::optional<std::complex<double>> o5{std::in_place, 3.0, 4.0};      

     // initialize set with lambda as sorting criterion:
     auto sc = [] (int x, int y) {
         return std::abs(x) < std::abs(y);
     };
      
     std::optional<std::set<int, decltype(sc)>> o6{std::in_place, {4, 8, -7, -2, 0, 5}, sc};   

* przy pomocy funkcji pomocniczej ``std::make_optional()``

  .. code-block:: c++

     auto o7 = std::make_optional(3.0); // optional<double>


Sprawdzenie stanu
-----------------

Aby sprawdzić, czy obiekt opcjonalny przychowuje wartość możemy użyć:

* metody ``has_value()``
* przeciążonej funkcji ``operator bool``

.. code-block:: c++

    std::optional o{42};

    assert(o.has_value() == true);
    
    if (o)  // has value
    {
        //...
    }    
    
    if (!o) // is empty
    {
        //...
    }

Dostęp do przechowywanej wartości
---------------------------------

Unsafe
~~~~~~

Dostęp do przechowywanej wartości zapewniony jest poprzez przeciążenie operatorów dereferencji ``*`` oraz ``*->``:

.. code-block:: c++

    *opt_str = "other";
    assert(opt_str.value() == "other");
    assert(opt_str->length() == 5);

.. warning:: Użycie tych operatorów w sytuacji, gdy obiekt jest pusty (nie przechowuje wartości) skutkuje *undefined behavior*

Safe
~~~~

Bezpieczny dostęp do przechowywanej wartości może być zrealizowany poprzez metody:

.. cpp:function:: const T& value()

    zwraca wartość. Jeśli jej nie ma rzuca wyjątkiem ``std::bad_optional_access``

.. code-block:: c++

    std::optional<std::string> opt_str;

    try
    {
        string str = opt_str.value();
    }
    catch(const std::bad_optional_access& e)
    {
        //...
    }
    
.. cpp:function:: template <typename U> \
                  T value_or(U&& default_value)

    zwraca wartość lub jeśli jej nie ma, podaną jako argument wartość domyślną

.. code-block:: c++

    #include <optional>
    #include <iostream>
    #include <cstdlib>
    
    std::optional<const char*> maybe_getenv(const char* n)
    {
        if(const char* x = std::getenv(n))
            return x;
        else
            return {};
    }
    
    //...
    std::cout << maybe_getenv("MYPWD").value_or("(none)") << '\n';
    
Resetowanie stanu
~~~~~~~~~~~~~~~~~

Usunięcie wartości realizowane jest za pomocą metody ``reset()``.

Semantyka przenoszenia
----------------------

Klasa ``std::optional`` wspiera semantykę przenoszenia:

.. code-block:: c++

    std::optional<std::string> os;

    std::string text = "text";
    os = std::move(text); // OK - string object is moved to optional

    std::string destination = std::move(*os);

Ostatnia instrukcja w powyższym przykładzie pozostawia obiekt ``std::optional``
z wartością (``os.has_value() == true``), ale w nieokreślonym stanie.

Specjalne przypadki
-------------------

W przypadku zmiennych typu ``std::optional`` przechowywanie w nich wartości typu ``bool``
i wskaźników może mieć zaskakujące efekty.

std::optional<bool>
~~~~~~~~~~~~~~~~~~~

.. code-block:: c++

    std::optional<bool> o{false};

    if (!o) // yields false - o has value, which is false
    {
        //...
    }

    if (o == false) // yields true
    {
    }


std::optional<T*>
~~~~~~~~~~~~~~~~~

.. code-block:: c++

    std::optional<double*> o{nullptr}; 

    if (!o) // yields false - o has value
    {
        //...
    }

    if (o == nullptr) // yields true
    {
        //...
    }

Case Study
----------

Opcjonalne składowe klasy
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: c++

    class Person
    {
        std::string first_name_;
        std::optional<std::string> middle_name_;
        std::string last_name_;
    public:
        Person(std::string fn, std::optional<std::string> mn, std::string ln)
            : first_name_{std::move(fn)}, middle_name_{std::move(mn)}, last_name_{std::move(ln)} 
        {}

        std::string full_name() const
        {
            return first_name_ + " " + ( middle_name_ ? *middle_name_ + " " : "") + last_name_; 
        }
    };

    //...
    Person p1{"Jan", "Maria", "Kowalski"};
    assert(p1.full_name() == "Jan Maria Kowalski");

    Person p2{"Jan", std::nullopt, "Kowalski"};
    assert(p2.full_name() == "Jan Kowalski");