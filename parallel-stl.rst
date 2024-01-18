*************************
Algorytmy współbieżne STL
*************************

W C++17 istnieje możliwość współbieżnego wykonania algorytmów STL.
Bazą dla wprowadzenia współbieżności do STL był dokument *Parallel TS*.

Implementacja algorytmów współbieżnych w GCC 9 wykorzystuje bibliotekę *Thread Building Blocks* firmy Intel.

Szczegółowy opis instalacji biblioteki TBB dla potrzeb *Parallel STL* w GCC 9 znajduje się 
na `stronie <https://solarianprogrammer.com/2019/05/09/cpp-17-stl-parallel-algorithms-gcc-intel-tbb-linux-macos>`_.

Lista algorytmów współbieżnych
------------------------------

Większość algorytmów STL posiada w C++17 wersje współbieżne:

+---------------------+-------------------------+------------------------------+
| adjacent_difference | inplace_merge           | replace_copy                 |
+---------------------+-------------------------+------------------------------+
| adjacent_find       | is_heap                 | replace_copy_if              |
+---------------------+-------------------------+------------------------------+
| all_of              | is_heap_until           | replace_if                   |
+---------------------+-------------------------+------------------------------+
| any_of              | is_partitioned          | reverse                      |
+---------------------+-------------------------+------------------------------+
| copy                | is_sorted               | reverse_copy                 |
+---------------------+-------------------------+------------------------------+
| copy_if             | is_sorted               | rotate                       |
+---------------------+-------------------------+------------------------------+
| copy_n              | is_sorted_until         | rotate_copy                  |
+---------------------+-------------------------+------------------------------+
| count               | lexicographical_compare | search                       |
+---------------------+-------------------------+------------------------------+
| count_if            | max_element             | search_n                     |
+---------------------+-------------------------+------------------------------+
| equal               | merge                   | set_difference               |
+---------------------+-------------------------+------------------------------+
| **exclusive_scan**  | min_element             | set_intersection             |
+---------------------+-------------------------+------------------------------+
| fill                | minmax_element          | set_symmetric_difference     |
+---------------------+-------------------------+------------------------------+
| fill_n              | mismatch                | set_union                    |
+---------------------+-------------------------+------------------------------+
| find                | move                    | sort                         |
+---------------------+-------------------------+------------------------------+
| find_end            | none_of                 | stable_partition             |
+---------------------+-------------------------+------------------------------+
| find_first_of       | nth_element             | stable_sort                  |
+---------------------+-------------------------+------------------------------+
| find_if             | partial_sort            | swap_ranges                  |
+---------------------+-------------------------+------------------------------+
| find_if_not         | partial_sort_copy       | transform                    |
+---------------------+-------------------------+------------------------------+
| for_each            | partition               | **transform_exclusive_scan** |
+---------------------+-------------------------+------------------------------+
| **for_each_n**      | partition_copy          | **transform_inclusive_scan** |
+---------------------+-------------------------+------------------------------+
| generate            | **reduce**              | **transform_reduce**         |
+---------------------+-------------------------+------------------------------+
| generate_n          | remove                  | uninitialized_copy           |
+---------------------+-------------------------+------------------------------+
| includes            | remove_copy             | uninitialized_copy_n         |
+---------------------+-------------------------+------------------------------+
| **inclusive_scan**  | remove_copy_if          | uninitialized_fill           |
+---------------------+-------------------------+------------------------------+
| inner_product       | remove_if               | uninitialized_fill_n         |
+---------------------+-------------------------+------------------------------+
|                     | replace                 | unique                       |
+---------------------+-------------------------+------------------------------+
|                     |                         | unique_copy                  |
+---------------------+-------------------------+------------------------------+


Funkcje dostępu do danych
-------------------------

Algorytmy współbieżne korzystają z tzw. funkcji dostępu do danych (*element access functions*). Należą do nich:

* wszystkie operacje danej kategorii iteratora przekazanego przy wywołaniu algorytmu
* operacje wykonywane na elementach wymagane przez specyfikację algorytmu
* obiekty funkcyjne przekazane przez użytkownika oraz operacje na tych obiektach wymagane przez specyfikację

Na przykład algorytm ``sort()``:

* wykorzystuje operacje iteratora o dostępie swobodnym
* wywołuje funkcję ``swap()`` na elementach sekwencji
* wywołuje funktor ``Compare`` przekazany przez użytkownika

.. important:: Funkcje lub obiekty funkcyjne przekazane do algorytmu współbieżnego nie powinny 
               bezpośrednio lub pośrednio modyfikować wartości obiektów przekazanych do nich jako argumenty.


Wytyczne wykonania algorytmów współbieżnych
-------------------------------------------

Dla nowych wersji algorytmów standardowych przyjęto rozwiązanie polegające na tym, że żądanie wykonania algorytmu
we współbieżny lub sekwencyjny sposób jest realizowane poprzez przekazanie jako pierwszego argumentu wywołania funkcji
tzw. wytycznej wykonania (*execution policy*).

Standard definiuje trzy podstawowe typy wytycznych:

std::execution::sequenced_policy - obiekt ``std::execution::seq``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Jeden wątek (ten, w którym został wywołany algorytm) **wykonuje wszystkie zadania sekwencyjnie w pewnej kolejności, która nie jest ściśle zdefiniowana i może być z każdym wywołaniem inna**. 
  W szczególności, **nie ma gwarancji, że kolejność wykonywania operacji będzie taka sama jak w wersji algorytmu bez wytycznej**.

W poniższym przykładzie wektor ``v`` zostanie zapełniony liczbami z przedziału 1-1000, ale w nieokreślonej kolejności:

.. code-block:: c++

    std::vector<int> v(1000);
    int count = 0;
    std::for_each(std::execution::seq, v.begin(), v.end(),
                    [&](int& x){ x = ++count; }); // not a race because of std::execution::seq

- Tryb wykonania przydatny przy debugowaniu i w testach
- Brak współbieżności wykonania - nie ma konieczności synchronizacji dostępu do współdzielonych danych

.. code-block:: c++

    std::transform(std::execution::seq, data.begin(), data.end(), dest.begin(), 
                    [&log_file](auto x) { 
                        log_file << x; // concurrent access would be a race
                        return x * x;
                    }
    );


std::execution::parallel_policy - obiekt ``std::execution::par``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Wiele wątków może wykonywać współbieżnie zadania (multithreading)**
- **Zadania w obrębie swojego wątku roboczego są wykonywane sekwencyjnie w zadanej (lecz nieokreślonej) kolejności, bez przeplotu** (*not-interleaved*)
  => wszystkie zadania muszą być *thread safe*
- Istnieje możliwość użycia konstrukcji synchronizujących współbieżny dostęp do danych (np. ``std::mutex``, ``std::atomic<T>``)

Wcześniejsze przykłady wywołania algorytmu, przy zastosowaniu wytycznej ``std::execution::par`` doprowadziłyby do wyścigu. Aby
nie dopuścić do niezdefiniowanego zachowania programu (*UB*) musimy zsynchronizować dostęp do współdzielonych zasobów:

- stosując zmienną typu atomowego

  .. code-block:: c++

    std::vector<int> v(1000);
    std::atomic<int> count{};
    std::for_each(std::execution::par, v.begin(), v.end(),
                    [&](int& x){ x = ++count; }); // must be atomic when std::execution::par    

- stosując muteks

  .. code-block:: c++

    std::transform(std::execution::par, data.begin(), data.end(), dest.begin(), 
                    [&log_file](auto x) {
                        {
                            std::lock_guard lk{log_file_mutex};   
                            log_file << x; // now concurrent access is synchronized
                        }
                        return x * x;
                    }
    );


std::execution::parallel_unsequenced_policy - obiekt ``std::execution::par_unseq``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Zadania mogą być wykonywane z wykorzystaniem wielowątkowości** (*multithreading*) **i współbieżności wektorowej** (np. OpenMP)
- Zadania mogą być:
  
  - **wykonywane w różnej kolejności w różnych wątkach**
  - **przemieszane** (*interleaved*) w ramach konkretnego wątku (np. druga operacja zostanie
  - **transferowane między wątkami** (zadanie rozpoczęte w wątku nr 1, może kontynuować pracę w wątku nr 2 i zakończyć działanie w wątku nr 3)
    rozpoczęta zanim pierwsza zostanie ukończona). 

- W rezultacie:
  
  - wywołania operacji synchronizujących (np. ``mutex::lock()``) grożą zakleszczeniem
  - nie można używać dynamicznej alokacji i dealokacji pamięci
  - operacje (funkcje) wykonywane przez algorytm muszą operować tylko na zadanym elemencie kolekcji i nie mogą modyfikować jakiegokolwiek
    współdzielonego stanu pomiędzy wątkami lub elementami sekwencji

.. code-block:: c++

    int x = 0;
    std::mutex m;
    int a[] = {1,2};

    std::for_each(std::execution::par_unseq, std::begin(a), std::end(a), 
                [&](int) {
                    std::lock_guard lk(m); // Error: lock_guard constructor calls m.lock()
                    ++x;
                }
    );

    std::transform(std::execution::par_unseq, data.begin(), data.end(), dest.begin(), 
                    [&](auto x) { 
                        return x * x; // OK - no access to a shared state
                    }
    );

Wyjątki w algorytmach współbieżnych
-----------------------------------

Jeśli jakikolwiek wyjątek wydostanie się z algorytmu współbieżnego, wywołana zostanie funkcja ``terminate()``.

Nowe algorytmy współbieżne
--------------------------

std::reduce
~~~~~~~~~~~

.. cpp:function:: T reduce(ExecutionPolicy&& policy, FwdIt first, FwdIt last, T init)
                  std::iterator_traits<FwdIt>::value_type reduce(ExecutionPolicy&& policy, FwdIt first, FwdIt last)
                  T reduce(ExecutionPolicy&& policy, FwdIt first, FwdIt last, T init, BinaryOp binary_op)

Działa jak algorytm ``std::accumulate()``, ale aplikuje funktor ``binary_op`` w nieokreślonej kolejności. Domyślnym funktorem jest ``std::plus<>``.

* rezultat w przypadku przekazania funktora, który nie jest przechodni i komutatywny, jest nieokreślony
  
  - np: dodawanie zmiennych typu ``float``

.. code-block:: c++

    std::vector<int> v(1000665);
    std::iota(v.begin(), v.end(), 1);

    auto sum = std::reduce(std::execution::par_unseq, v.begin(), v.end(), 0LL);


std::transform_reduce
~~~~~~~~~~~~~~~~~~~~~

.. cpp:function:: T transform_reduce(ExecutionPolicy&& policy, FwdIt1 first1, FwdIt1 last1, FwdIt2 first2, T init)
                  T transform_reduce(ExecutionPolicy&& policy, FwdIt1 first1, FwdIt1 last1, FwdIt2 first2, T init, BinaryOp1 binary_op1, BinaryOp2 binary_op2)
                  T transform_reduce(ExecutionPolicy&& policy, FwdIt first, FwdIt last, T init, BinaryOp binary_op, UnaryOp unary_op)

Aplikuje transformację funktorem ``binary_op2()`` lub ``unary_op()``, a następnie redukuje wyniki transformacji
funktorem ``binary_op1``.

Domyślnymi funktorami są odpowiednio: ``std::multiplies<>`` i ``std::plus<>``.

Przykład policzenie słów w plikach z rozszerzeniem cpp.

.. code-block:: c++

    template <typename ExecutionPolicy>
    std::uintmax_t count_words(string_view text, ExecutionPolicy execution_policy)
    {
        if (text.empty())
            return 0;

        auto is_word_beginning = [](auto left, auto right) {
            return std::isspace(left) && !std::isspace(right);
        };

        std::uintmax_t wc = (!std::isspace(text.front()) ? 1 : 0);

        wc += std::transform_reduce(execution_policy,
            text.begin(),
            text.end() - 1,
            text.begin() + 1,
            std::size_t(0),
            std::plus<>(),
            is_word_beginning);

        return wc;
    }


std::exclusive_scan
~~~~~~~~~~~~~~~~~~~

.. cpp:function:: FwdIt2 exclusive_scan( ExecutionPolicy&& policy, FwdIt1 first, FwdIt1 last, FwdIt2 d_first, T init)
                  FwdIt2 exclusive_scan( ExecutionPolicy&& policy, FwdIt1 first, FwdIt1 last, FwdIt2 d_first, T init, BinaryOperation binary_op )

Oblicza sumę poprzedzającą używając funktora ``binary_op()`` (używając wartości początkowej ``init``) i 
zapisuje wyniki do sekwencji wskazywanej iteratorem ``d_first``.

Przedrostek *exlusive* oznacza, że i-ty element nie jest uwzględniany w i-tej sumie.

std::inclusive_scan
~~~~~~~~~~~~~~~~~~~

.. cpp:function:: FwdIt2 inclusive_scan( ExecutionPolicy&& policy, FwdIt1 first, FwdIt1 last, FwdIt2 d_first, T init)
.. cpp:function:: FwdIt2 inclusive_scan( ExecutionPolicy&& policy, FwdIt1 first, FwdIt1 last, FwdIt2 d_first, T init, BinaryOperation binary_op )

Oblicza sumę poprzedzającą używając funktora ``binary_op()`` (używając wartości początkowej ``init``) i 
zapisuje wyniki do sekwencji wskazywanej iteratorem ``d_first``.

Przedrostek *inclusive* oznacza, że i-ty element jest uwzględniany w i-tej sumie.


std::transform_inclusive_scan oraz transform_exclusive_scan
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Algorytmy będące połączeniem transformacji i i odpowiedniego algorytmu skanującego.
