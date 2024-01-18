Szablony w C++17
================

Dedukcja argumentów szablonu dla klas (CTAD)
--------------------------------------------

C++17 wprowadza mechanizm dedukcji argumentów szablonu klasy (*Class Template Argument Deduction*). 
Typy parametrów szablonu klasy mogą być dedukowane na podstawie argumentów przekazanych do konstruktora tworzonego obiektu.
Wcześniej mechanizm dedukcji typu był dostępny tylko dla szablonów funkcji i deklaracji ``auto``.

Dla klasy szablonowej:

.. code-block:: c++

    template <typename T1, typename T2>
    struct ValuePair
    {
        T1 fst;
        T2 snd;

        ValuePair(T1 f, T2 s) : fst{f}, snd{s}
        {
        }
    };

Mechanizm dedukcji typów argumentów klasy szablonowej umożliwia prostsze tworzenie instancji. Zamiast jawnie specyfikować 
argumenty szablonu, możemy kompilatorowi zlecić dedukcję na podstawie wywołania konstruktora klasy:

.. code-block:: c++

    ValuePair<int, double> vp1(1, 3.14); // OK - all versions of standard

    ValuePair vp2(1, 3.14); // OK in C++17 - deduces ValuePair<int, double>
    ValuePair vp3{1, 3.14); // OK in C++17 - deduced ValuePair<int, double>

    auto vp4 = ValuePair(1, "text"); // OK in C++17 - deduces ValuePair<int, const char*>
    auto vp5 = ValuePair{3.14, "pi"s); // OK in C++17 - deduces ValuePair<int, std::string>

.. warning:: Nie można częściowo dedukować argumentów szablonu klasy. 
   Należy wyspecyfikować lub wydedukować wszystkie parametry z wyjątkiem parametrów domyślnych.

.. code-block:: c++

    ValuePair vp6; // ERROR - T1 & T2 are undefined - deduction fails
    ValuePair<int> vp7{1, 3.14}; // ERROR - partial deduction is not allowed

Inny przykład dedukcji typu argumentów dla szablony klasy:

.. code-block:: c++

    template <typename T1 = int, typename T2 = T1>
    struct Generic
    {
        T1 fst;
        T2 snd;

        explicit Generic(T1 f = T1{}, T2 s = T2{}) : fst{f}, snd{s}
        {}
    };

    Generic<int, double> g0{1, 3.14}; // no deduction

    Generic g1{1, 3.14};
    static_assert(is_same_v<decltype(g1), Generic<int, double>>);

    Generic<double> g2{3.14, 1}; // no deduction
    static_assert(is_same_v<decltype(g2), Generic<double, double>>);

    Generic g3{3.14};
    static_assert(is_same_v<decltype(g3), Generic<double, double>>);

    Generic<> g4; // no deduction
    static_assert(is_same_v<decltype(g4), Generic<int, int>>);

    Generic g5{}; 
    static_assert(is_same_v<decltype(g5), Generic<int, int>>);

Stosowanie mechanizmu dedukcji argumentów szablonu klasy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Stosując mechanizm dedukcji argumentów szablonu klasy możemy zrezygnować ze stosowania 
funkcji pomocniczych definiowanych jako szablony funkcji. Zamiast tworzyć parę przy pomocy:

.. code-block:: c++

    auto p1 = std::make_pair(1, 3.14);
    auto p2 = std::pair<int, std::string>(1, "one");

Możemy napisać:

.. code-block:: c++

    using namespace std::string_literals;

    std::pair p1{1, 3.14};
    std::pair p2{1, "one"s};

Inny praktyczny przykład dedukcji argumentów szablonu klasy:

.. code-block:: c++

    std::timed_mutex mtx_one;
    std::shared_mutex mtx_two;

    std::scoped_lock lk{mtx_one, mtx_two}; // deduces std::scoped_lock<std::timed_mutex, std::shared_mutex>

Specjalny przypadek dedukcji argumentów klasy szablonowej
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Jeżeli kod służący do dedukcji argumentów szablonu klasy może być zinterpretowany
jako przypadek inicjalizacji poprzez kopię, to kompilator preferuje taką interpretację.

Rozważmy następujący przypadek dedukcji:

.. code-block:: c++

    std::vector v{1, 2, 3}; // vector<int>
    std::vector data1{v, v}; // vector<vector<int>>

Lecz w przypadku, gdy składnia inicjalizacji obiektu pasuje do wywołania konstruktora kopiującego, 
wtedy działa specjalna reguła dedukcji argumentu szablonu klasy:

.. code-block:: c++

    std::vector data2{v}; // vector<int>!

.. note:: W powyższym kodzie dedukcja argumentów szablonu ``vector`` zależy od ilości argumentów przekazanych do konstruktora!

Podpowiedzi dedukcyjne (*deduction guides*)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

C++17 umożliwia tworzenie podpowiedzi dla kompilatora, jak powinny być dedukowane typy parametrów szablonu klasy na podstawie wywołania odpowiedniego konstruktora.

Daje to możliwość poprawy/modyfikacji domyślnego procesu dedukcji.

Dla szablonu:

.. code-block:: c++

    template <typename T>
    class S
    {
    private:
        T value;
    public:
        S(T v) : value(v)
        {}
    };

Podpowiedź dedukcyjna musi zostać umieszczona w tym samym zakresie (przestrzeni nazw) i może mieć postać:

.. code-block:: c++

    template <typename T> S(T) -> S<T>; // deduction guide

    S x{12}; // OK -> S<int> x{12};
    S y(12); // OK -> S<int> y(12);
    auto z = S{12}; // OK -> auto z = S<int>{12};
    S s1(1), s2{2}; // OK -> S<int> s1(1), s2{2};
    S s3(42), s4{3.14}; // ERROR

gdzie:

* ``S<T>`` to tzw. typ zalecany (*guided type*)
* nazwa podpowiedzi dedukcyjnej musi być niekwalifikowaną nazwą klasy szablonowej zadeklarowanej wcześniej w tym samym zakresie
* typ zalecany podpowiedzi musi odwoływać się do identyfikatora szablonu (*template-id*), do którego odnosi się podpowiedź

W deklaracji ``S x{12};`` specyfikator ``S`` jest nazywany symbolem zastępczym dla klasy (*placeholder class type*).
W przypadku użycia symbolu zastępczego dla klasy, nazwa zmiennej musi zostać podana jako następny element składni.
W rezultacie poniższa deklaracja jest błędem składniowym:

.. code-block:: c++

    S* p = &x; // ERROR - syntax not permitted

Dany szablon klasy może mieć wiele konstruktorów oraz wiele podpowiedzi dedukcyjnych:

.. code-block:: c++

    template <typename T>
    struct Data
    {
        T value;

        using type1 = T;

        Data(const T& v)
            : value(v)
        {
        }

        template <typename ItemType>
        Data(initializer_list<ItemType> il)
            : value(il)
        {
        }
    };

    template <typename T>
    Data(T)->Data<T>;

    template <typename T>
    Data(initializer_list<T>)->Data<vector<T>>;

    Data(const char*) -> Data<std::string>;

    //...

    Data d1("hello"); // OK -> Data<string>

    const int tab[10] = {1, 2, 3, 4};
    Data d2(tab); // OK -> Data<const int*>

    Data d3 = 3; // OK -> Data<int>

    Data d4{1, 2, 3, 4}; // OK -> Data<vector<int>>

    Data d5 = {1, 2, 3, 4}; // OK -> Data<vector<int>>

    Data d6 = {1}; // OK -> Data<vector<int>>

    Data d7(d6); // OK - copy by default rule -> Data<vector<int>>

    Data d8{d6, d7}; // OK -> Data<vector<Data<vector<int>>>>


Podpowiedzi dedukcyjne nie są szablonami funkcji - służą jedynie dedukowaniu argumentów szablonu i nie są wywoływane. 
W rezultacie nie ma znaczenia czy argumenty w deklaracjach dedukcyjnych są przekazywane przez referencję, czy nie.

.. code-block:: c++

    template <typename T> 
    struct X
    {
        //...
    };

    template <typename T>
    struct Y
    {
        Y(const X<T>&);
        Y(X<T>&&);
    };

    template <typename T> Y(X<T>) -> Y<T>; // deduction guide without references

W powyższym przykładzie podpowiedź dedukcyjna nie odpowiada dokładnie sygnaturom konstruktorów przeciążonych. Nie ma to znaczenia, ponieważ jedynym celem podpowiedzi jest umożliwienie dedukcji typu, który jest parametrem szablonu. Dopasowanie wywołania przeciążonego konstruktora odbywa się później.

Podpowiedzi dedukcyjne vs. Konstruktory
***************************************

Podpowiedzi dedukcyjne rywalizują z konstruktorami klasy. Mechanizm dedukcji wykorzystuje konstruktor lub podpowiedź, która 
ma najwyższy priorytet zgodnie z regułami przeciążania funkcji. Jeśli konstruktor i podpowiedź pasują jednakowo dobrze, kompilator preferuje podpowiedź dedukcyjną.

Dla szablonu klasy:

.. code-block:: c++

    template <typename T>
    struct Thing
    {
        Thing(const T&) 
        {
        }
    };

    Thing(int) -> Thing<long>;

Przy wywołaniu:

.. code-block:: c++

    Thing t1{42}; // T deduced as long

preferowana jest podpowiedź dedukcyjna. 

Ale, gdy w wywołaniu konstruktora użyjemy typu ``char``:

.. code-block:: c++

    Thing t2{'a'}; // deduced as char

preferowany do dedukcji argumentu szablonu jest konstruktor (ponieważ nie jest wymagana konwersja typu).


Ponieważ przekazanie argumentu przez wartość, jest dopasowywane równie dobrze co przekazanie argumentu
przez referencję oraz biorąc pod uwagę fakt, że podpowiedź dedukcyjna jest preferowana przy równie dobrym dopasowaniu, 
najczęściej wystarczy w sygnaturze podpowiedzi przekazać parametry przez wartość.


Niejawne podpowiedzi dedukcyjne
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ponieważ często podpowiedź dedukcyjna jest potrzebna dla każdego konstruktora klasy, standard C++17
wprowadza mechanizm **niejawnych podpowiedzi dedukcyjnych** (*implicit deduction guides*).
Działa on w następujący sposób:

* Lista parametrów szablonu dla podpowiedzi zawiera listę parametrów z szablonu klasy
  - w przypadku szablonowego konstruktora klasy kolejnym elementem jest lista parametrów szablonu konstruktora klasy

* Parametry "funkcyjne" podpowiedzi są kopiowane z konstruktora lub konstruktora szablonowego

* Zalecany typ w podpowiedzi jest nazwą szablonu z argumentami, które są parametrami szablonu wziętymi 
  z klasy szablonowej

Dla klasy szablonowej rozważanej powyżej:

.. code-block:: c++

    template <typename T>
    class S
    {
    private:
        T value;
    public:
        S(T v) : value(v)
        {}
    };

niejawna podpowiedź dedukcyjna będzie wyglądać następująco:

.. code-block:: c++

    template <typename T> S(T) -> S<T>; // implicit deduction guide

W rezultacie programista nie musi implementować jej jawnie.

Agregaty a dedukcja argumentów
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Jeśli szablon klasy jest agregatem, to mechanizm automatycznej dedukcji argumentów szablonu wymaga napisania jawnej podpowiedzi dedukcyjnej.

Bez podpowiedzi dedukcyjnej dedukcja dla agregatów nie działa:

.. code-block:: c++

    template <typename T>
    struct Aggregate1
    {
        T value;
    };

    Aggregate1 agg1{8}; // ERROR
    Aggregate1 agg2{"eight"}; // ERROR
    Aggregate1 agg3 = 3.14; // ERROR


Gdy napiszemy dla agregatu podpowiedź, to możemy zacząć korzystać z mechanizmu dedukcji:

.. code-block:: c++

    template <typename T>
    struct Aggregate2
    {
        T value;
    };

    template <typename T>
    Aggregate2(T) -> Aggregate2<T>;

    Aggregate2 agg1{8}; // OK -> Aggregate2<int>
    Aggregate2 agg2{"eight"}; // OK -> Aggregate2<const char*>
    Aggregate2 agg3 = { 3.14 }; // OK -> Aggregate2<double>

Podpowiedzi dedukcyjne w bibliotece standardowej
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dla wielu klas szablonowych z biblioteki standardowej dodano podpowiedzi dedukcyjne w celu ułatwienia tworzenia instancji tych klas.

std::pair<T>
************

Dla pary STL dodana w standardzie podpowiedź to:

.. code-block:: c++

    template<class T1, class T2>
    pair(T1, T2) -> pair<T1, T2>;

    pair p1(1, 3.14); // -> pair<int, double>

    pair p2{3.14f, "text"s}; // -> pair<float, string>

    pair p3{3.14f, "text"}; // -> pair<float, const char*>

    int tab[3] = { 1, 2, 3 };
    pair p4{1, tab}; // -> pair<int, int*>

std::tuple<T...>
****************

Szablon ``std::tuple`` jest traktowany podobnie jak ``std::pair``:

.. code-block:: c++

    template<class... UTypes>
    tuple(UTypes...) -> tuple<UTypes...>;

    template<class T1, class T2>
    tuple(pair<T1, T2>) -> tuple<T1, T2>;

    //... other deduction guides working with allocators

    int x = 10;
    const int& cref_x = x;

    tuple t1{x, &x, cref_x, "hello", "world"s}; // -> tuple<int, int*, int, const char*, string>

std::optional<T>
****************

Klasa ``std::optional`` jest traktowana podobnie do pary i krotki.

.. code-block:: c++

    template<class T> optional(T) -> optional<T>;

    optional o1(3); // -> optional<int>
    optional o2 = o1; // -> optional<int>


Inteligentne wskaźniki
**********************

Dedukcja dla argumentów konstruktora będących wskaźnikami jest zablokowana:

.. code-block:: c++

    int* ptr = new int{5};
    unique_ptr uptr{ip}; // ERROR - ill-formed (due to array type clash)

Wspierana jest dedukcja przy konwersjach:

* z ``weak_ptr``/``unique_ptr`` do ``shared_ptr``:

  .. code-block:: c++

      template <class T> shared_ptr(weak_ptr<T>) ->  shared_ptr<T>;
      template <class T, class D> shared_ptr(unique_ptr<T, D>) ->  shared_ptr<T>;

* z ``shared_ptr`` do ``weak_ptr``

  .. code-block:: c++

      template<class T> weak_ptr(shared_ptr<T>) -> weak_ptr<T>;
  
.. code-block:: c++

    unique_ptr<int> uptr = make_unique<int>(3);

    shared_ptr sptr = move(uptr); -> shared_ptr<int>
        
    weak_ptr wptr = sptr; // -> weak_prt<int>

    shared_ptr sptr2{wptr}; // -> shared_ptr<int>

std::function
*************

Dozwolone jest dedukowanie sygnatur funkcji dla ``std::function``:

.. code-block:: c++

    int add(int x, int y)
    {
        return x + y;
    }

    function f1 = &add;
    assert(f1(4, 5) == 9);

    function f2 = [](const string& txt) { cout << txt << " from lambda!" << endl; };
    f2("Hello");


Kontenery i sekwencje
*********************

Dla kontenerów standardowych dozwolona jest dedukcja typu kontenera dla konstruktora akceptującego parę iteratorów:

.. code-block:: c++

    vector<int> vec{ 1, 2, 3 };
    list lst(vec.begin(), vec.end()); // -> list<int>


Dla ``std::array`` dozwolona jest dedukcja z sekwencji:

.. code-block:: c++

    std::array arr1 { 1, 2, 3 }; // -> std::array<int, 3>


Deklaracje using w *variadic templates*
---------------------------------------

W C++17 dodano możliwość wygodniejszego użycia deklaracji ``using`` w przypadku
rozpakowywania paczki parametrów (*parameter pack expansion*) w szablonie wariadycznym.

.. code-block:: c++

    #include <string>
    #include <unordered_set>

    class Customer
    {
        std::string name_;
    public:
        Customer(const std::string& name) : name_{name}
        {}

        std::string name() const
        {
            return name_;
        }
    };

    struct CustomerEq
    {
        bool operator()(const Customer& c1, const Customer& c2) const
        {
            return c1.name() == c2.name();
        }
    };

    struct CustomerHash
    {
        bool operator()(const Customer& c) const
        {
            return std::hash<std::string>{}(c.name());
        }
    };

    // overloader
    template <typename... Ts>
    struct Overloader : Ts...
    {
        using Ts::operator()...; // since C++17
    };

    using CustomerComparer = Overloader<CustomerEq, CustomerHash>;

    unordered_set<Customer, CustomerComparer, CustomerComparer> collection;

Parametry szablonu nie będące typami ze specyfikatorem ``auto``
---------------------------------------------------------------

C++17 wprowadza możliwość zadeklarowania parametru szablonu nie będącego typem jako ``auto`` lub ``decltype(auto)``.
W rezultacie typ stałej jest automatycznie dedukowany wg odpowiedniego mechanizmu.

.. code-block:: c++


    template <auto N>
    struct S
    {
        //...
    };

    S<42> s1; // -> N in S is int
    S<'a'> s2; // -> N in S is char
    S<3.14> s3; // ERROR - template parametr type still cannot be double

    // partial specialization
    template <int N> struct S<N>
    {
    };

    // list of heterogenous constant template arguments
    template <auto... CS> struct ValueList { };


    // list of homogenous constant template arguments
    template <auto C, decltype(C)... CS> struct ValueList { };

Przykład szablonu z parametrem specyfikowanym jako ``decltype(auto)``:

.. code-block:: c++

    template <decltype(auto) N>
    struct S
    {
        S()
        {
            cout << "N has value: " << N << endl;
            cout << "type of N is int&: " << is_same_v<decltype(N), int&> << endl;
        }

        void print()
        {
            cout << "N has value: " << N << endl;
        }
    };

    constexpr auto x = 665;
    int y{};

    S<x> s0; // N is int
    S<(y)> s1; // N is int& => prints: 'N has value 0'

    y = 77;
    S<(y)> s2; // N is int& => prints: 'N has value 77'
    
    y = 88;
    s1.print(); // prints: 'N has value 88'
    s2.print(); // prints: 'N has value 88'


Variable templates ze specyfikatorem auto
-----------------------------------------

.. code-block:: c++

    // variable.hpp

    #include <array>

    template <typename T, auto N> std::array<T, N> FixedArray; // OK - since C++17
    template <auto N> constexpr decltype(N) value = N; // OK - since C++17

    // in test1.cpp

    #include "variable.hpp"

    void print();

    int main()
    {
        FixedArray<double, 100u>[0] = 17;
        FixedArray<int, 10>[0] = 42;

        print();

        std::cout << value<'c'> << "\n";
    }

    // in test2.cpp

    #include "variable.hpp"

    void print()
    {
        std::cout << FixedArray<double, 100u>[0] << std::endl;
        
        for(auto i = 0u; i < FixedArray<int, 10>.size(); ++i)
        {
            cout << FixedArray<int, 10>[i] << std::endl;
        }
    }