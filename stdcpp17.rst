Standard C++17
==============

C++17 to najnowszy opublikowany standard języka C++.

* Dokument standardu ISO:
  
  - ISO/IEC 14882:2017

* Darmowa wersja bliska wersji finalnej standardu:
  
  - `Working Draft, Standard for Programming Language C++ <https://wg21.link/n4659>`_

Kompilatory - C++17
-------------------

* gcc/g++ 7.1

  - wspiera wszystkie nowe elementy języka
  - implementuje kilka nowych klas z biblioteki standardowej
  - opcja kompilacji: ``-std=c++17``

* clang 5

  - wspiera wszystkie nowe elementy języka
  - opcja kompilacji: ``-std=c++0z`` lub ``-std=c++17``

* Visual Studio 2017

  - wersja kompilatora >= 19.10 (binarnie kompatybilny z VS2015)
  - opcja kompilacji: ``/std:c++latest`` lub ``/std:c++17``
  - `szczegóły implementacji C++17 w VS2017 <https://blogs.msdn.microsoft.com/vcblog/2017/12/19/c17-progress-in-vs-2017-15-5-and-15-6/>`_   


Stałe definiujące wersje
------------------------

Stała preprocesora ``__cplusplus`` definiuje, która wersja standardu jest dostępna w trakcie kompilacji. Wartości, jakie może przyjmować, to:

================= ===========
dla C++98 i C++03 ``199711L``
----------------- -----------
dla C++11         ``201103L``
----------------- -----------
dla C++14         ``201402L``
----------------- -----------
dla C++17         ``201703L``
================= ===========
