Klasa std::any
==============

``std::any`` umożliwia:

* bezpieczne (typowane) mechanizmy przechowywania i odwoływania się do wartości dowolnych typów 
  
  - bezpiecznie typizowany odpowiednik ``void*``

* przechowywanie elementów heterogenicznych w kontenerach biblioteki standardowej
* przekazywanie wartości dowolnych typów pomiędzy warstwami, bez konieczności wyposażania warstw pośredniczących w jakąkolwiek wiedzę o tych typach

Klasa ``std::any`` służy do przechowywania i udostępniania wartości dowolnych typów, ale pod warunkiem znajomości tych typów, a więc z zachowaniem zalet i bezpieczeństwa typowania.

Typy przechowywane w ``std::any`` muszą spełniać następujące warunki:

* muszą umożliwiać kopiowanie - typy *move-only* nie są wspierane, choć klasa
* muszą umożliwiać przypisywanie (publiczny operator przypisania)
* nie mogą rzucać wyjątków z destruktora (to jest wymóg odnośnie wszystkich typów użytkownika w C++)

Interfejs klasy std::any
------------------------

.. cpp:function:: any()

    domyślny konstruktor, tworzący pusty egzemplarz obiektu klasy ``any`` 

.. cpp:function:: any(const any& other)
    
    konstruktor kopiujący

.. cpp:function:: any(any&& other)
    
    konstruktor przenoszący

.. cpp:function:: template <typename ValueType> \
                  any(ValueType&& value)

    szablonowa wersja konstruktora do tworzenia obiektu przechowywującego kopię argumentu typu ``ValueType`` 

.. cpp:function:: template <typename ValueType, class... Args> \
                  std::decay_t<ValueType>& emplace(Args&&... args)

    Zmienia przechowywany obiekt na nowy typu ``ValueType`` konstruowany z argumentów ``args``

.. cpp:function:: void swap(any& other)

    wymienia wartości przechowywane pomiędzy dwoma obiektami klasy ``any`` 

.. cpp:function:: any& operator=(const any& other)

    jeśli obiekt nie jest pusty, operator przypisania powoduje usunięcie przechowywanej wartości i przyjęcie kopii wartości przechowywanej w ``other``

.. cpp:function:: any& operator=(any&& other)

    przenosząca wersja operatora przypisania

.. cpp:function:: template <typename ValueType>  \
                  any& operator=(ValueType&& value)
    
    szablonowa wersja operatora przypisania

.. cpp:function:: bool has_value() const
    
    sygnalizuje stan egzemplarza ``any``, zwracając ``true``, jeśli egzemplarz przechowuje jakąkolwiek wartość

.. cpp:function:: const std::type_info& type() const

    opisuje typ przechowywanej wartości 

.. cpp:function:: void reset()

    jeśli obiekt nie jest pusty, przechowywany obiekt jest niszczony 



Funkcje zewnętrzne
~~~~~~~~~~~~~~~~~~

Dwie wersje funkcji szablonowej ``any_cast``:

.. cpp:function:: template<typename ValueType> \
                  ValueType any_cast(const any& operand)
        
    funkcja ``any_cast`` udostępnia wartość przechowywaną w obiekcie ``any``. 
    Argumentem wywołania jest obiekt ``any``, którego wartość ma zostać wyłuskana. Jeśli parametr szablonu funkcji ``ValueType`` nie odpowiada właściwemu typowi przechowywanego elementu rzucany jest wyjątek ``std::bad_any_cast``

.. cpp:function:: template<typename ValueType> \
                  ValueType* any_cast(any* operand)            

    przeciążona wersja ``any_cast``, przyjmująca wskaźniki obiektów i zwracająca typowane wskaźniki wartości przechowywanych w ``any``. Jeśli typ ``ValueType`` nie odpowiada typowi właściwemu typowi wartości przechowywanej, zwracany jest wskaźnik pusty (``nullptr``).

Stosowanie std::any
-------------------

.. code:: c++

    std::any a;

    a = std::string("Tekst...");
    a = 42;
    a = 3.1415;

    double pi = std::any_cast<double>(a); // OK

    std::string s = std::any_cast<std::string>(a); // rzuca wyjatek std::bad_any_cast 

    Gadget* g = std::any_cast<Gadget>(&a); // zwraca nullptr

    if (g)
    	g->do_stuff();
    else 
    	std::cout << "Niepoprawna konwersja dla obiektu any.\n"; 

Kontenery heterogeniczne z std::any
-----------------------------------

Klasa ``std::any`` umożliwia przechowywanie w kontenerach standardowych elementów różnych, niezwiązanych ze sobą typów.

.. code:: c++

    void print_any(const std::any& a)
    {
        // ...
    }

    std::vector<std::any> store_anything;

    store_anything.push_back(A());
    store_anything.push_back(B());
    store_anything.push_back(C());
    store_anything.push_back(Gadget{"ipad"});
    
    //...
   
    for(const auto& obj : store_anything)
        print_any(obj);


Obiekty typu std::any w algorytmach standardowych
-------------------------------------------------

Algorytmy standardowe mogą być wykonywane na heterogenicznych kontenerach zawierających obiekty typu ``any``.

.. code:: c++

    using namespace std;

    // predykat
    auto is_int = [](const std::any& a) { return typeid(int) == a.type(); };

    vector<std::any> a = { 1, 3.14, "text"s, 42, 44.4f, 665 };
    vector<std::any> b;

    copy_if(a.begin(), a.end(), back_inserter(b), is_int);