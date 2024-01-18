Fold expressions w C++17
========================

Wyrażenia *fold* w językach funkcjonalnych
------------------------------------------

Koncept *redukcji* jest jednym z podstawowych pojęć w językach
funkcjonalnych.

**Fold** w językach funkcjonalnych to rodzina funkcji wyższego rzędu
zwana również **reduce**, **accumulate**, **compress** lub **inject**.
Funkcje **fold** przetwarzają rekursywnie uporządkowane kolekcje danych
(listy) w celu zbudowania końcowego wyniku przy pomocy funkcji
(operatora) łączącej elementy.

Dwie najbardziej popularne funkcje z tej rodziny to fold (fold left) i
foldr (fold right).

Przykład:

Redukcja listy [1, 2, 3, 4, 5] z użyciem operatora (+):

-  użycie funkcji ``fold`` - redukcja od lewej do prawej

--------------

.. code:: haskell

    fold (+) 0 [1..5]

.. code:: console

    (((((0 + 1) + 2) + 3) + 4) + 5)

-  użycie funkcji ``foldr`` - redukcja od prawej do lewej

--------------

.. code:: haskell

    foldr (+) 0 [1..5]

.. code:: console

    (1 + (2 + (3 + (4 + (5 + 0)))))

Redukcja w C++98 - std::accumulate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

W C++ redukcja jest obecna poprzez implementację algorytmu
``std::accumulate``.

.. code:: c++

    #include <vector>
    #include <numeric>
    #include <string>
    
    using namespace std::string_literals;
    
    std::vector<int> vec = {1, 2, 3, 4, 5};
    
    std::accumulate(std::begin(vec), std::end(vec), "0"s, 
                       [](const std::string& reduction, int item) { 
                           return "("s + reduction +  " + "s + std::to_string(item) + ")"s; });




.. parsed-literal::

    (((((0 + 1) + 2) + 3) + 4) + 5)




Variadic templates
------------------

C++11 wprowadziło *variadic templates* jako jeden z podstawowych
mechanizmów zaawansowanego programowania z wykorzystaniem szablonów.

*Variadic templates* umożliwiają między innymi implementację funkcji
akceptujących dowolną liczbę parametrów z zachowaniem bezpieczeństwa
typów.

Implementacja redukcji z wykorzystaniem *variadic templates* często
wykorzystuje idiom *Head-Tail*, który polega na rekursywnym wywołaniu
funkcji z częścią parametrów. Rekurencja jest przerywana przez
implementację funkcji albo przez specjalizację szablonu klasy dla
końcowego przypadku.

.. code:: c++

    namespace Cpp11 
    {
        auto sum()
        {
            return 0;
        }
        
        template <typename Head, typename... Tail>
        auto sum(Head head, Tail... tail)
        {
            return head + sum(tail...);
        }
    }


.. code:: c++

    Cpp11::sum(1, 2, 3, 4, 5);


.. parsed-literal::

    (int) 15


Fold expressions w C++17
------------------------

Wyrażenia typu *fold* umożliwiają uproszczenie rekurencyjnych
implementacji dla zmiennej liczby argumentów szablonu.

Przykład z wariadyczną funkcją ``sum(1, 2, 3, 4, 5)`` z wykorzystaniem
*fold expressions* może być w C++17 zaimplementowany następująco:

.. code:: c++

    template <typename... Args>
    auto sum(Args&&... args)
    {
        return (... + args);
    }


.. code:: c++

    sum(1, 2, 3, 4, 5);


.. parsed-literal::

    (int) 15


Składnia wyrażeń fold
~~~~~~~~~~~~~~~~~~~~~

Niech :math:`e = e_1, e_2, \dotso, e_n` będzie wyrażeniem, które
zawiera nierozpakowany *parameter pack* i :math:`\otimes` jest
*operatorem fold*, wówczas **wyrażenie fold** ma postać:

-  Unary **left fold**

   :math:`(\dotso\; \otimes\; e)`

który jest rozwijany do postaci
:math:`(((e_1 \otimes e_2) \dotso ) \otimes e_n)`

-  Unary **right fold**

   :math:`(e\; \otimes\; \dotso)`

który jest rozwijany do postaci
:math:`(e_1 \otimes ( \dotso (e_{n-1} \otimes e_n)))`

Jeśli dodamy argument nie będący paczką parametrów do operatora ``...``,
dostaniemy dwuargumentową wersję **wyrażenia fold**. W zależności od
tego po której stronie operatora ``...`` dodamy dodatkowy argument
otrzymamy:

-  Binary **left fold**

   :math:`(a \otimes\; \dotso\; \otimes\; e)`

który jest rozwijany do postaci
:math:`(((a \otimes e_1) \dotso ) \otimes e_n)`

-  Binary **right fold**

   :math:`(e\; \otimes\; \dotso\; \otimes\; a)`

który jest rozwijany do postaci
:math:`(e_1 \otimes ( \dotso (e_n \otimes a)))`

Operatorem :math:`\otimes` może być jeden z poniższych operatorów C++:

.. code:: cpp

    +  -  *  /  %  ^  &  |  ~  =  <  >  <<  >>
    +=  -=  *=  /=  %=  ^=  &=  |=  <<=  >>=
    ==  !=  <=  >=  &&  ||  ,  .*  ->*

Elementy identycznościowe
~~~~~~~~~~~~~~~~~~~~~~~~~

Operacja fold dla pustej paczki parametrów (*parameter pack*) jest
ewaluowana do określonej wartości zależnej od rodzaju zastosowanego
operatora. Zbiór operatorów i ich rozwinięć dla pustej listy parametrów
prezentuje tabela:

+--------------------+--------------------------------------------------+
| Operator           | Wartość zwracana jako element identycznościowy   |
+====================+==================================================+
| :math:`\&\&`       | true                                             |
+--------------------+--------------------------------------------------+
| :math:`\mid\mid`   | false                                            |
+--------------------+--------------------------------------------------+
| :math:`,`          | void()                                           |
+--------------------+--------------------------------------------------+

Jeśli operacja fold jest ewaluowana dla pustej paczki parametrów dla
innego operatora, program jest nieprawidłowo skonstruowany
(*ill-formed*).

Przykłady zastosowań wyrażeń fold w C++17
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

all_true(Args...)
*****************

Wariadyczna funkcja przyjmująca dowolną liczbę argumentów konwertowalnych do wartości logicznych i zwracająca ich iloczyn logiczny
(``operator &&``):

.. code:: c++

    template <typename... Args>
    bool all_true(Args... args)
    {
        return (... && args);
    }

.. code:: c++

    bool result = all_true(true, true, false, true);
    assert(result == false);

    assert(all_true(1, 1, 1));

    assert(all_true() == true);


print(Args...)
**************

Funkcja ``print()`` wypisująca przekazane argumenty. Implementacja
wykorzystuje wyrażenie *binary left fold* dla operatora ``<<``:

.. code:: c++

    #include <iostream>
    
    template <typename... Args>
    void print(Args&&... args)
    {
        (std::cout << ... << args) << "\n";
    }

.. code:: c++

    print(1, 2, 3, 4);


.. parsed-literal::

    1234


Wyliczanie wartości skrótu (*hash*) dla krotki
**********************************************

.. code-block:: c++

    template <typename... Args>
    size_t hash_value(const Args&... value)
    {
        size_t seed = 0;
        (boost::hash_combine(seed, value), ...); // fold-expression
        return seed;
    }

    template <typename Tpl, size_t... Is>
    auto hash_for_tuple_impl(const Tpl& t, std::index_sequence<Is...>)
    {
        return hash_value(std::get<Is>(t)...);
    }

    template <typename... Ts>
    auto hash_for_tuple(const std::tuple<Ts...>& tpl)
    {
        using Indexes = std::make_index_sequence<sizeof...(Ts)>;
        return hash_for_tuple_impl(tpl, Indexes{});
    }

    struct Person
    {
        string first_name;
        string last_name;
        uint8_t age;

        auto tied() const
        {
            return tie(first_name, last_name, age);
        }

        bool operator==(const Person& other) const
        {
            return tied() == other.tied();
        }
    };

    struct HashPerson
    {
        size_t operator()(const Person& p) const
        {               
            return hash_for_tuple(p.tied());
        }
    };
    

Iteracja po elementach różnych typów
************************************

.. code:: c++

    #include <iostream>
    
    struct Window {
        void show() { std::cout << "showing Window\n"; }
    };
    
    struct Widget {
        void show() { std::cout << "showing Widget\n"; }
    };
    
    struct Toolbar {
        void show(){ std::cout << "showing Toolbar\n"; }
    };



.. code:: c++

    Window wnd;
    Widget widget;
    Toolbar toolbar;
    
    #define fw(...) ::std::forward<decltype(__VA_ARGS__)>(__VA_ARGS__)
    
    auto printer = [](auto&&... args) { (fw(args).show(), ...); };
    
    printer(wnd, widget, toolbar);


.. parsed-literal::

    showing Window
    showing Widget
    showing Toolbar


foreach(Args...)
****************

Implementacja wariadycznej wersji algorytmu ``foreach()`` z
wykorzystaniem funkcji ``std::invoke()``:

.. code:: c++

    #include <iostream>
    
    template <typename F, typename... Args>
    auto invoke(F&& f, Args&&... args)
    {
        return std::forward<F>(f)(std::forward<Args>(args)...);
    }
    
    struct Printer
    {
        template <typename T>
        void operator()(T&& arg) const { std::cout << arg; }
    };


.. code:: c++

    #include <string>    
    
    using namespace std::literals;
    
    auto foreach = [](auto&& fun, auto&&... args) {
        (..., invoke(fun, std::forward<decltype(args)>(args));
    };
    
    foreach(Printer{}, 1, " - one; ", 3.14, " - pi;"s);


.. parsed-literal::

    1 - one; 3.14 - pi


count(Args...) oraz count_if(Args...)
*************************************

Implementacja wariadycznych wersji algorytmów ``count()`` oraz
``count_if()`` działających na listach typów:

.. code:: c++

    #include <type_traits>
    #include <iostream>
    
    // count the times a predicate Predicate is satisfied in a typelist Lst
    template <template<class> class Predicate, class... Lst>
    constexpr size_t count_if = (Predicate<Lst>::value + ...); 
    
    // count the occurences of a type V in a typelist L
    template <class V, class... Lst>
    constexpr size_t count = (std::is_same<V, Lst>::value + ...); 


.. code:: c++

    static_assert(count_if<std::is_integral, float, unsigned, int, double, long> == 3);
    static_assert(count<float, unsigned, int, double, long, float> == 1);


