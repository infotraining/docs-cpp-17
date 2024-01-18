Nowe elementy biblioteki standardowej
=====================================

Nowe algorytmy STL
------------------

std::clamp
~~~~~~~~~~

* | ``template<class T>``
  | ``constexpr const T& clamp( const T& v, const T& lo, const T& hi )``

* | ``template<class T, class Compare>``
  | ``constexpr const T& clamp( const T& v, const T& lo, const T& hi, Compare comp )``

Ogranicza wartość do odpowiednich przedziałów. Odpowiednik: ``std::min(std::max(val, lo), hi)``

.. code-block:: c++

    auto c1 = std::clamped(42, 10, 90);  // c1 = 42;
    auto c2 = std::clamped(7, 10, 90); // c2 = 10;
    auto c3 = std::clamped(99, 10, 90); // c3 = 90

std::sample
~~~~~~~~~~~

* | ``template<class PopulationIt, class SampleIt, class Distance, class UniformRandomBitGenerator>``
  | ``SampleIt sample(PopulationIt first, PopulationIt last, SampleIt out, Distance n, UniformRandomBitGenerator&& g)``

Ekstrakcja próbki statystycznej z sekwencji określonej iteratorami ``[first; last)``.
Próbka ``n`` elementów jest zapisywana do sekwencji wskazywanej przez iterator wyjściowy ``out``. Elementy są wybierane
za pomocą generatora liczb pseudolosowych ``g``.

.. code-block:: c++

    std::string in = "abcdefgh", out;
    std::sample(in.begin(), in.end(), std::back_inserter(out),
                5, std::mt19937{std::random_device{}()});

    // out can be: cdefg

std::search - opcje wyszukiwania
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

C++17 oferuje nowe (szybsze) opcje wyszukiwania podciągów wykorzystywane w 
algorytmie ``std::search()``.

* | ``template<class ForwardIt, class BinaryPredicate = std::equal_to<>>``
  | ``class default_searcher;``

  Standardowa (taka jak przed C++17) implementacja opcji wyszukiwania.

* | ``template<class RandomIt1,``
  |     ``class Hash = std::hash<typename std::iterator_traits<RandomIt1>::value_type>,``
  |     ``class BinaryPredicate = std::equal_to<>`` 
  | ``> class boyer_moore_searcher;``

  Implementacja algorytmu wyszukiwania *Boyer-Moore*

* | ``template<class RandomIt1,``
  |     ``class Hash = std::hash<typename std::iterator_traits<RandomIt1>::value_type>,``
  |     ``class BinaryPredicate = std::equal_to<>`` 
  | ``> class boyer_moore_horspool_searcher;``

  Implementacja algorytmu *Boyer-Moore-Horspool*

Przykład użycia nowych algorytmów wyszukiwania:

.. code-block:: c++

    std::string in = "Lorem ipsum dolor sit amet, consectetur adipiscing elit,"
                     " sed do eiusmod tempor incididunt ut labore et dolore magna aliqua";
    
    std::string needle = "pisci";
    


    std::default_searcher searcher{needle.begin(), needle.end()}; // default search

    std::boyer_moore_searcher searcher{needle.begin(), needle.end()}; // faster search

    std::boyer_moore_horspool_searcher searcher{needle.begin(), needle.end()};

    
    if(auto it = std::search(in.begin(), in.end(), searcher); it != in.end())
    {
        std::cout << "The string " << needle << " found at offset "
                  << it - in.begin() << '\n';
    }
    else
        std::cout << "The string " << needle << " not found\n";

Poprawki dla kontenerów standardowych
-------------------------------------

Mniejsze poprawki w API kontenerów
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* nowa operacja ``try_emplace()`` dla map i map z haszowaniem

* operacje ``emplace_back()`` i ``emplace_front()``
  
  - zwracają referencję do wstawionego elementu
  - modyfikacja dla ``vector``, ``list``, ``forward_list``, ``stack``, ``queue``

* operacja ``data()`` dla stringów bez modyfikatora ``const``

* ``std::vector``, ``std::list`` i ``std::forward_list`` wspierają niekompletne typy

Transfer węzłów dla zbiorów i map
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

C++17 rozszerza API zbiorów i map (z haszowaniem) o możliwość przepinania węzłów
pomiędzy kontenerami.

* lepsza wydajność niż ``erase()`` i ``insert()`` - żadne z elementów przechowywanych w kontenerze nie są kopiowane lub przesuwane
* aby przepiąć węzeł tylko typy klucza/wartości (oraz alokatora) muszą być zgodne ze sobą

  - kryteria porównań kluczy, funkcje haszujące mogą być różne
  - dozwolone jest przepinanie z kontenera nie zezwalającego na duplikaty do kontenera z duplikatami kluczy: np. ``set <-> multiset``

Typ węzła - node_type
*********************

Zdefiniowany jest typ węzła ``container::node_type``

- szczegółowa implementacja nie jest specyfikowana
- składowa ``value()`` zwraca wartość dla zbiorów
- składowe ``key()`` oraz ``mapped()`` są dostępne dla map
- wspierana jest semantyka przenoszenia (np. typy *move-only*)

Nowe operacje w interfejsie kontenerów
**************************************

.. cpp:member:: node_type set::extract(const_iterator pos)
                node_type set::extract(const_iterator pos)
                node_type set::extract(const key_type& key)

    Dokonuje ekstrakcji węzła wskazanego iteratorem ``pos`` lub zawierającego klucz równoważny ``key``. Zwraca uchwyt do węzła.
    Unieważniane są tylko iteratory wskazujące na usuwany element. Referencje i wskaźniki do ekstrahowanego elementu pozostają prawidłowe.

.. cpp:member:: insert_return_type set::insert(node_type&& nh)
                iterator set::insert(const_iterator hint, node_type&& nh)

    Wstawia do kontenera element, którego właścicielem jest węzeł ``nh``. Jeśli ``nh`` jest pustym węzłem, to nie jest wykonana żadna akcja.

.. cpp:member:: void set::merge(set& source)
                void set::merge(multiset& source)

    Próbuje dokonać ekstrakcji węzłów w kontenerze ``source`` i przepiąć je (*splice*) do kontenera ``*this`` używając
    komparatora z kontenera ``*this``. Jeśli w kontenerze ``*this`` znajduje się już element równoważny, to nie jest on poddawany
    ekstrakcji i zostaje w kontenerze ``source``.

Przykład przepięcia węzłów między kontenerami asocjacyjnymi:

.. code-block:: c++

    std::map<int, std::string> src{{1, "one"}, {2, "two"}, {3, "three"}};
    std::map<int, std::string> dst{{3, "THREE"}};

    auto pos_src = src.find(1);
    dst.insert(src.extract(pos_src)); // splice using iterator
    
    dst.insert(src.extract(2)); // splice using key value

    auto result = dst.insert(src.extract(3));

    // result.position == next(next(dst.begin()))
    // result.inserted == false
    // result.node.key() == 3
    // result.node.mapped() == "three"

    // instead the last statement
    auto [pos, success, node] = dst.insert(src.extract(2)); // splice using key value

    // pos == next(next(dst.begin()))
    // success == false
    // node.key() == 3
    // node.mapped() == "three"

Nowe funkcje pomocnicze
-----------------------

std::size(obj), std::empty(obj), std::data(obj)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* jednolite API dla tablic statycznych, kontenerów i list inicjalizacyjnych

  - nagłówek: ``<iterator>``

.. code-block:: c++

  template <typename T>
  void check(const T& t)
  {
      std::cout << "size: " << std::size(t) << '\n';
      std::cout << "empty: " << boolalpha << std::empty(t) << '\n';
      std::cout << "data: " << std::data(t) << '\n'; // prints address
  }

  //...

  int arr[10] = { 1, 2, 3, 4, 5 };
  check(arr);

  vector<int> vec = { 1, 2, 3, 4, 5 };
  check(vec);

  auto il = { 1, 2, 3, 4, 5 };
  check(il);

std::as_const(obj)
~~~~~~~~~~~~~~~~~~

Funkcja tworzy stały widok dla przekazanego jako argument obiektu. Przydatne narzędzie przy wywoływaniu przeciążonych funkcji.
Pozwala na uniknięcie rzutowań przy pomocy operatora ``const_cast<>``

- nagłówek ``<utility>``

.. code-block:: c++

    std::string mutable_string= "Hello World!";
    const std::string &const_view= std::as_const(mutable_string);

    void process_text(std::string&); // 1
    void process_text(const std::string&); // 2

    process_string(std::as_const(mutable_string)); // calls 2nd version

Funkcję ``as_const()`` można wykorzystać przy przechwytywaniu referencji w wyrażeniach lambda:

.. code-block:: c++

    std::vector<int> vec = { 1, 2, 3, 4, 5 };

    auto printer = [coll& = std::as_const(vec)] { 
        for(const auto& item : coll)
            std::cout << item << " ";
        std::cout << '\n';
    };

Wielowątkowość w C++17
----------------------

Muteksy współdzielone
~~~~~~~~~~~~~~~~~~~~~

W celu implementacji blokad współdzielonych (*Read/Write Locks*):

* w C++14 wprowadzono

  - ``std::shared_timed_mutex``
  - ``std::shared_lock<>``

* C++17 dodaje

  - ``std::shared_mutex``

.. code-block:: c++

    std::shared_mutex smtx;

    //...

    {
        std::shared_lock slk{smtx}; // calls smtx.lock_shared()

        // reading from a shared resource
    } // smtx.unlock_shared() called


std::scoped_lock<>
~~~~~~~~~~~~~~~~~~

Klasa ``std::scoped_lock<>`` jest wariadyczną wersją ``std::lock_guard<>``.
Posiada wbudowaną ochronę przed zakleszczeniem (*deadlock*):

Pozyskiwanie wielu muteksów przed C++17:

.. code-block:: c++

    void transfer(BankAccount& from, BankAccount& to, double amount)
    {
        std::lock(from.mtx_, to.mtx_);
        std::lock_guard<std::mutex> lk_from{from.mtx_, std::adopt_lock};
        std::lock_guard<std::mutex> lk_to{to.mtx_, std::adopt_lock};
        
        from.balance_ -= amount;
        to.balance_ += amount;
    }

To samo w C++17:

.. code-block:: c++

    void transfer(BankAccount& from, BankAccount& to, double amount)
    {
        std::scoped_lock lk{from.mtx_, to.mtx_};
        from.balance_ -= amount;
        to.balance_ += amount;
    }

std::atomic<T>::is_always_lock_free
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Stała ``constexpr`` dla typów atomowych informująca, że implementacja atomowości dla typu ``T`` jest zawsze *lock-free*.


Informacje o wielkości linii cache'a L1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``inline constexpr std::size_t hardware_destructive_interference_size = /*implementation-defined*/;``
 
  Zwraca minimalną wartość offsetu pomiędzy dwoma obiektami, która pomaga uniknąć problemu *false-sharing*.

  .. code-block:: c++

      struct Counters
      {
          alignas(std::hardware_destructive_interference_size) std::atomic<int> counter1;
          alignas(std::hardware_destructive_interference_size) std::atomic<int> counter2;
      };
  

* ``inline constexpr std::size_t hardware_constructive_interference_size = /*implementation-defined*/;``

  Zwraca maksymalny rozmiar ciągłego fragmentu pamięci na którym wystąpi *false-sharing* 

  .. code-block:: c++

      struct KeepTogether 
      {
          atomic<int> counter;
          int data;
      };

      struct LargeData 
      {
          // Other data members...
          alignas(sizeof(KeepTogether)) KeepTogether pack;
          // Other data members...
      };
    
      static_assert(sizeof(KeepTogether) <= std::hardware_constructive_interference_size);

std::shared_ptr<T[]>
--------------------

Od C++17 można bezpiecznie tworzyć ``shared_ptr`` dla tablicy dynamicznej:

.. code-block:: c++

    std::shared_ptr<int[]> shrd_tab(new int[10]);

* Brak ``make_shared()`` dla tablic dynamicznych.
