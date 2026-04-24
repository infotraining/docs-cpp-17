*********************
Biblioteka Filesystem
*********************

C++17 dodaje do standardu bibliotekę umożliwiającą cross-platformową obsługę systemu plików.
Specyfikacja standardu powstała na bazie *Boost.Filesystem* uwzględniając kompatybilność z innymi elementami standardu oraz dostarczając
kilka brakujących elementów.

* Nagłówek ``<filesystem>``

Podstawowe pojęcia w bibliotece Filesystem
------------------------------------------

* **plik** (*file*) - obiekt systemu plików, który przechowuje dane, używany do odczytu i/lub zapisu. Plik ma nazwy i atrybuty. Jednym z atrybutów jest typ pliku:
  
  - **katalog** (*directory*) - plik, który jest kontenerem dla innych obiektów plikowych tzw. *directory entry* (plików, katalogów, itp.). W kontekście konkretnego pliku, 
    katalog, w którym znajduje się ten obiekt, to tzw. **katalog rodzica** (*parent directory*) i jest reprezentowany przez symbol ``..``)
  - **trwały link** (*hard link*) - obiekt katalogu, który wiąże nazwę z istniejącym plikiem. Jeśli system wspiera trwałe odnośniki, plik jest usuwany, jeśli zostaną usunięte wszystkie trwałe odnośniki
  - **link symboliczny** (*symbolic link*) - obiekt katalogowy, który wiąże nazwę ze ścieżką, która istnieje lub nie
  - **regularny plik** (*regular file*) - plik, który nie jest jednym z powyżej zdefiniowanych rodzajów plików

* **nazwa pliku** (*filename*) - ciąg znaków, który określa nazwę pliku. Nazwy ``.`` oraz ``..`` mają specjalne znaczenie w bibliotece
* **ścieżka** (*path*) - sekwencja elementów identyfikująca plik. Składa się z:

  - *root name* - ``C:`` lub ``//server``
  - *root directory* - ``/`` w Uniksie
  - *relative path* - sekwencji nazw plików, gdzie wszystkie poza ostatnią muszą być katalogami lub linkami do katalogów

**Separator katalogów** (*directory separator*) - '/` lub '\` lub '//` lub '\\`

Typy ścieżek:

* **absolutna** (*absolut path*) - ścieżka, która jednoznacznie identyfikuje lokalizację pliku
* **kanoniczna** (*canonical path*) - ścieżka absolutna, która nie zawiera linków symbolicznych, `.` lub ``..``
* **względna** (*relative path*) - ścieżka, która identyfikuje lokalizację pliku w odniesieniu do danej lokalizacji w systemie plików

Podstawowe obiekty biblioteki Filesystem
----------------------------------------

Klasa ``std::filesystem::path`` określa ścieżkę dostępu i definiuje kilka typów pomocniczych:

* ``value_type`` - określa typ znaku wykorzystanego do definicji ścieżki (``char`` w POSIX, ``wchar_t`` w systemie Windows)
* ``string_type`` - alias dla ``std::basic_string<value_type>``

Statyczna stała ``prefered_separartor`` określa typ separatora w ścieżkach (``/`` lub ``\``)

Najczęściej wykorzystywane metody klasy:

* Funkcje składowe dekompozycji ścieżki

  .. code-block:: c++

        #include <iostream>
        #include <filesystem>

        using namespace std;
        namespace fs = std::filesystem;

        int main()
        {                                               //  UNIX                      WINDOWS
            fs::path pth1 = fs::path{"foo"} / "bar"; 
            cout << pth1 << endl;                       //  "foo/bar"                 "foo\bar"

            fs::path p{"/foo/bar/data.txt"}; 
            cout << p << endl;                          //  "/foo/bar/data.txt"       "\foo\bar\data.txt"

            cout << "decomposition:\n";

            cout << p.root_name() << endl;              //  ""                        ""
            cout << p.root_directory() << endl;         //  "/"                       "\"
            cout << p.root_path() << endl;              //  "/"                       "\"
            cout << p.relative_path() << endl;          //  "foo/bar/data.txt"        "foo\bar\data.txt"
            cout << p.parent_path() << endl;            //  "/foo/bar"                "\foo\bar"
            cout << p.file_name() << endl;              //  "data.txt"                "data.txt"
            cout << p.stem() << endl;                   //  "data"                    "data"
            cout << p.extension() << endl;              //  ".txt"                    ".txt"
            cout << p.is_absolute() << endl;            //  1 (true)                  0 (false)
        }

* Operacje ``append()``, ``operator /()`` umożliwiają łączenie ścieżek wstawiając separator

  .. code-block:: c++

        path /= "Training";
        path = path / "Modern" / "Cpp17";
        path.append("Programming");
        // Windows: C:\Users\Infotraining\Documents\Training\Modern\Cpp17\Programming
        // POSIX:   /home/infotraining/docs/Training/Modern/Cpp17/Programming

* Operacje ``concat()``, ``operator +()`` - łączą elementy w ścieżkę, ale bez użycia separatora

Iteracja po elementach katalogu
-------------------------------

Iteracja może zostać zrealizowana przy pomocy *iteratorów katalogów* oraz 

* pętli *range-based-for*:

  .. code-block:: c++

        auto base_path = fs::current_path() / "temp";

        cout << "\nContent of: " << base_path << endl;
        for(const fs::directory_entry& dir_entry : fs::directory_iterator(base_path))
        {
            cout << dir_entry.path() << endl;
        }

* pętli *for* z iteratorami

  .. code-block:: c++

    string rwx(fs::perms p)
    {
        auto check = [p](fs::perms bit, char c) { return (p & bit) == fs::perms::none ? '-' : c; };

        return {
            check(fs::perms::owner_read, 'r'),
            check(fs::perms::owner_write, 'w'),
            check(fs::perms::owner_exec, 'x'),
            check(fs::perms::group_read, 'r'),
            check(fs::perms::group_write, 'w'),
            check(fs::perms::group_exec, 'x'),
            check(fs::perms::others_read, 'r'),
            check(fs::perms::others_write, 'w'),
            check(fs::perms::others_exec, 'x')};
    }

    //...

    cout << "\nRecursive content of: " << base_path << endl;
    for(const fs::directory_entry& dir_entry : fs::recursive_directory_iterator(base_path))
    {
        auto path = dir_entry.path();
        auto rwx_status = rwx(dir_entry.status().permissions());
        auto size = fs::is_regular_file(dir_entry.status()) ? fs::file_size(dir_entry.path()) : 0u;
        cout << rwx_status << " - "
             << setw(12) << right << size << " - "
             << path << endl;
    }

W powyższym przykładzie użyty został *iterator rekurencyjny*.

Modyfikacje struktury plików i katalogów
----------------------------------------

Biblioteka Filesystem zawiera zbiór funkcji umożliwiających modyfikację struktury plików:

* kopiowanie - ``std::filesystem::copy()``
* usuwanie - ``std::filesystem::remove()`` i ``std::filesystem::remove_all()``
* tworzenie katalogów - ``std::filesystem::create_directory()`` i ``std::filesystem::create_directories()``
* tworzenie linków - ``std::filesystem::create_symlink()`` i ``std::filesystem::create_directory_symlink()``
* zmiana nazwy - ``std::filesystem::rename()``

.. code-block:: c++

    #include <iostream>
    #include <fstream>
    #include <filesystem>
    namespace fs = std::filesystem;
    
    int main()
    {
        fs::create_directories("sandbox/dir/subdir");
        std::ofstream("sandbox/file1.txt").put('a');
        fs::copy("sandbox/file1.txt", "sandbox/file2.txt"); // copy file
        fs::copy("sandbox/dir", "sandbox/dir2"); // copy directory (non-recursive)
        
        // sandbox holds 2 files and 2 directories, one of which has a subdirectory
        // sandbox/file1.txt
        // sandbox/file2.txt
        // sandbox/dir2
        // sandbox/dir
        // sandbox/dir/subdir
        
        fs::copy("sandbox", "sandbox/copy", fs::copy_options::recursive);
        // sandbox/copy holds copies of the above files and subdirectories
        
        fs::remove_all("sandbox");
    }