Klasa std::variant
==================

Typ wariantowy w C++17:

* umożliwia bezpieczne (ze względu na typy) przechowanie wartości określonego typu, wybranego z listy typów definiujących zmienną wariantową
  
  - ``std::variant`` jest implementacją koncepcji bezpiecznej unii (*type-safe union*)

* umożliwia statyczny podgląd (wizytację) zmiennych wariantowych
* efektywnie składuje wartości z listy typów wariantowych na stosie
  
  - nie może dynamicznie alokować pamięci na stercie (istotna różnica w stosunku do ``std::any``)
* nie może przechowywać referencji, tablic oraz typu ``void``
* może zawierać duplikaty typów na liście
  
  - obsługa takiego przypadku jest realizowana poprzez indeksy (tak jak w ``std::tuple``)


Unie w C++ mogą przechowywać tylko typy POD:

.. code:: c++

    union 
    { 
        int i; double d; 
    } u;

    u.d = 3.14; 
    u.i = 3; // nadpisuje u.d (OK: u.d jest typem POD)


Są zatem bezużyteczne w programowaniu obiektowym:

.. code:: c++

    union 
    { 
        int i; 
        std::string s; // błąd kompilacji: std::string nie jest typem POD
    } u;


Alternatywne rozwiązania:

* użycie ``void*`` - jest  niebezpieczne typologicznie
* ``std::any`` 
  
  - rozwiązanie mało wydajne
  - dodanie nowego typu może spowodować błędy 


Stosowanie std::variant
-----------------------

Plik nagłówkowy: <variant>

Konstrukcja zmiennej wariantowej
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deklarując typ wariantowy ``std::variant`` trzeba podać zestaw typów, które będą mogły być reprezentowane w typie wariantowym.

.. code:: c++

    std::variant<int, string, double> my_variant1; // holds an int with a default value 0

    std::variant<int, string, double> my_variant2(3.14); // holds a double 3.14

    my_variant1 = 24;
    my_variant1 = 2.52;
    my_variant1 = "text"s;

Domyślny konstruktor typu wariantowego inicjuje zmienną domyślną wartością dla pierwszego typu
z listy.

Jeśli pierwszy typ z listy nie jest domyślnie konstruowalny, można użyć tagu - ``std::monostate``:

.. code-block:: c++

    struct S
    {
        S(int v) : value{v} 
        {}

        int value;
    };

    std::variant<S, int> v1; // ERROR - ill-formed
    std::variant<monostate, S, int> v2; // OK - now v2 must be assigned


Konstruktor typu wariantowego może przeprowadzać konwersje, co może dać zaskakujący efekt:

.. code-block:: c++

    variant<string, bool> x("abc"); // OK, but chooses bool


Przypisania wartości do zmiennej wariantowej
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Przypisanie nowej wartości dla zmiennej wariantowej możemy zrealizować na dwa sposoby:

.. cpp:function:: template <typename T> \
                  variant& operator=(T&& x)

   .. code-block:: c++  
   
       variant<int, string, double> v1;

       v1 = 42; // v1 holds int{42}
       v1 = "text"s; // v1 holds "text"s
       v1 = 3.14; // v1 holds double{3.14}


       variant<int, string, string> v2;
       v2 = "text"s; // ERROR

       variant<string, bool> v3;
       v3 = "ctext"; // v3 holds bool{true}

.. cpp:function:: template <typename T, typename... Args> \
                  T& emplace(Args&&... args)

    Tworzy nową wartość (*in-place*) w istniejącej zmiennej wariantowej. 
    Jest jedyną możliwością przypisania wartości dla duplikatów typu na liście.                 

.. code-block:: c++

    class Gadget
    {
        int id_;
        std::string name_;

        Gadget(int id, const std::string& name)
            : id_{id}, name_{name}
        {}

        //...
    };

    variant<int, Gadget, int> v;

    v.emplace<Gadget>(1, "ipad"); // creates Gadget{1, "ipad"} inside variant object
    v.emplace<0>(42); // sets the first int to 42
    v.emplace<2>(665); // sets the second int to 665

Dostęp do wartości przechowywanej w zmiennej wariantowej
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Bezpieczny dostęp do wartości przechowywanej w zmiennej wariantowej odbywa się przy pomocy funkcji ``std::get<T>(v)`` lub ``std::get<Index>(v)``.

Jeśli wywołanie ``get(v)`` okaże się nieskuteczne (zmienna wariantowa zawiera wartość typu różnego od argumentu szablonu funkcji ``get(v)``), zgłaszany jest wyjątek ``std::bad_variant_access``. 

Aby uniknąć zgłaszania niepowodzenia w postaci wyjątku, należy wywołać funkcję ``std::get_if(v)`` przekazując jako argument wskaźnik do zmiennej wariantowej. W razie niezgodności typów, zwrócony zostanie ``nullptr``.

.. code:: c++

    std::variant<int, std::string, double> my_variant{"text"s};

    std::string s1 = std::get<std::string>(my_variant);  // OK
    std::string s2 = std::get<1>(my_variant); // OK
    std::get<string>(v) += "!!!"; 

    int x = std::get<int>(my_variant); // ERROR - throws std::bad_variant_access
    
    if (std::string* ptr_str = std::get_if<std::string>(&my_variant); ptr_str != nullptr)
        cout << "Stored string: " << *ptr_str << endl;


Inne funkcje API dla klasy std::variant
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. cpp:function:: std::size_t std::variant::index() const

    Zwraca indeks (licząc od zera) typu z listy dla danego stanu zmiennej wariantowej.

    .. code-block:: c++
    
        std::variant<int, double> v = 3.14;
        assert(v.index() == 1);

.. cpp:function:: template <typename T> \
                  bool holds_alternative(const std::variant& v)

    Sprawdza, czy zmienna wariantowa przechowuje w danym momencie odpowiedni typ.

    .. code-block:: c++
    
        if (std::holds_alternative<double>(v))
            std::cout << "Holds double\n";

Problem pustego stanu
---------------------

Obiekt klasy ``std::variant`` może stać się pustym obiektem tylko w przypadku wystąpienia wyjątku w trakcie operacji przypisania nowej (lub domyślnej) wartości.

W takim przypadku:

* metoda ``valueless_by_exception()`` zwraca ``true``
* a wywołanie metody ``index()`` zwraca wartość ``std::variant_npos``

.. code-block:: c++

    struct S
    {
        operator int()
        {
            throw std::runtime_error("ERROR#13");
        }
    };

    std::variant<int, double> v{3.14};

    try
    {
        v.emplace<0>(S{}); // throws while being set
    }
    catch(...)
    {
        assert(v.valueless_by_exception() == true);
        assert(v.index() == std::variant_npos);
    }


Wizytowanie wariantów
---------------------

Rozwiązaniem problemu przeglądania wartości przechowywanych w zmiennych wariantowych jest zastosowanie wizytatora. Wizytatory są implementowane jako obiekty funkcyjne z operatorami wywołania funkcji przyjmującymi argumenty typów odpowiadających typom z zestawu wariantowego.

Wizytacja odbywa się za pośrednictwem funkcji ``std::visit(wizytator, zmienna-wariantowa)``. Jeżeli zmieni się zestaw typów w zmiennej wariantowej, która była wizytowana przez wizytatora i wizytator nie będzie w stanie obsłużyć nowo dodanego typu, to kompilator zgłosi błąd.

Klasa wizytatora
~~~~~~~~~~~~~~~~

Klasa wizytatora:

.. code:: c++

    class PrintVisitor
    {
    public:
        void operator()(int i) const 
        {
            cout << "int: " << i << "\n";
        }
        
        void operator()(string s) const 
        {
            cout << "string: " << s << "\n";
        }
    };

    std::variant<int, string> var("Test"s);

    PrintVisitor pv;
    std::visit(pv, var); // compile error if type is not supported by visitor

    var = 12;
    std::visit(PrintVisitor{}, var);


Wizytacja za pomocą lambd
~~~~~~~~~~~~~~~~~~~~~~~~~~

Do wizytacji można również wykorzystać lambdę generyczną:


.. code-block:: c++

    std::visit([](auto&& value) { std::cout << value << "\n" }, var);

Istnieje możliwość zbudowania wizytora w miejscu wizytacji (*in-place*). Do tego celu będziemy potrzebowali 
funkcji wariadycznej ``make_inline_visitor()``, której implementacja korzysta z *variadic templates*.
Funkcja ta pozwoli utworzyć obiekt funkcyjny składający się z przeciążonych operatorów wywołania funkcji, który zostanie wykorzystany do wizytacji zmiennej wariantowej.

.. code-block:: c++

    template <typename... Ts>
    struct Overloader : Ts...
    {
        using Ts::operator()...;
    };

    template <typename... Ts>
    auto make_inline_visitor(Ts&&...op)
    {
        return Overloader<Ts...>{op...};
    }


    variant<int, double, string> v = 42;

    auto local_visitor = 
        make_inline_visitor(
            [](int value) { return "int: "s + to_string(value); },
            [](double value) { return "double: "s + to_string(value); },
            [](const string s) { return "string: " + s; }
        );

    auto result = visit(local_visitor, v);
    assert(result == "int: 42"s);

    v = text;
    result = visit(local_visitor, v);
    assert(result == "string: text");