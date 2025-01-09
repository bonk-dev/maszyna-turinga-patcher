# Łatki do symulatora maszyny turinga

W tym repozytorium znajduje się patcher służący do poprawy dwóch bugów uniemożliwiających wygodne 
korzystanie z symulatora maszyny Turinga, stworzonego 
przez autorów [www.MaszynaTuringa.info](https://web.archive.org/web/20090214013001/http://www.maszynaturinga.info/).

## Przygotowanie pliku exe
Symulator jest spakowany przy użyciu packera [UPX](https://github.com/upx/upx).
Aby go spatchować, należy go najpierw wypakować:
```
upx.exe -d maszyna_turinga.exe
```

## Użycie patchera
Po wypakowaniu pliku exe:
```
python3 main.py maszyna_turinga.exe maszyna_turinga_poprawiona.exe
```

## Opis łatek
### Zawieszenie przy wykonywaniu tabelki:
    
Funkcja FUN_00401ef4 wpada w nieskończoną pętlę dokładnie w 0x00401efe, gdy local_8 jest mniejsze od 0x15.
Nie wiem czemu miało to służyć, ale rozwiązaniem jest wyNOPowanie instrukcji. 

Oryginał:
```
                     undefined __cdecl FUN_00401ef4(int param_1)
     undefined         AL:1           <RETURN>
     int               Stack[0x4]:4   param_1                                 XREF[1]:     00401f07(R)  
     undefined4        Stack[-0x8]:4  local_8                                 XREF[3]:     00401ef8(R), 
                                                                                           00401efe(R), 
                                                                                           00401f04(RW)  
                     FUN_00401ef4                                    XREF[1]:     FUN_00401bd8:00401d88(c)  
00401ef4 55              PUSH       EBP
00401ef5 8b ec           MOV        EBP,ESP
00401ef7 51              PUSH       ECX
00401ef8 83 7d fc 14     CMP        dword ptr [EBP + local_8],0x14
00401efc 7f 06           JG         LAB_00401f04
                     LAB_00401efe                                    XREF[1]:     00401f02(j)  
00401efe 83 7d fc 14     CMP        dword ptr [EBP + local_8],0x14
00401f02 7e fa           JLE        LAB_00401efe
                     LAB_00401f04                                    XREF[1]:     00401efc(j)  
00401f04 ff 45 fc        INC        dword ptr [EBP + local_8]
00401f07 8b 45 08        MOV        EAX,dword ptr [EBP + param_1]
00401f0a b9 0a 00        MOV        ECX,0xa
         00 00
00401f0f 99              CDQ
00401f10 f7 f9           IDIV       ECX
00401f12 50              PUSH       EAX
00401f13 e8 c0 b4        CALL       KERNEL32.DLL::Sleep                              void Sleep(DWORD dwMilliseconds)
         0c 00
00401f18 a1 98 de        MOV        EAX,[PTR_DAT_004dde98]                           = 004e04f4
         4d 00
00401f1d 8b 00           MOV        EAX=>DAT_004e04f4,dword ptr [EAX]
00401f1f e8 a8 8b        CALL       FUN_0044aacc                                     undefined FUN_0044aacc(int param
         04 00
00401f24 59              POP        ECX
00401f25 5d              POP        EBP
00401f26 c3              RET
```

Po spatchowaniu:
```
                     undefined __cdecl inf_loop_start(int param_1)
     undefined         AL:1           <RETURN>
     int               Stack[0x4]:4   param_1                                 XREF[1]:     00401f07(R)  
     undefined4        Stack[-0x8]:4  local_8
                     inf_loop_start                                  XREF[1]:     FUN_00401bd8:00401d88(c)  
00401ef4 55              PUSH       EBP
00401ef5 8b ec           MOV        EBP,ESP
00401ef7 90              NOP
00401ef8 90              NOP
00401ef9 90              NOP
00401efa 90              NOP
00401efb 90              NOP
00401efc 66 90           NOP
00401efe 90              NOP
00401eff 90              NOP
00401f00 90              NOP
00401f01 90              NOP
00401f02 66 90           NOP
00401f04 90              NOP
00401f05 90              NOP
00401f06 90              NOP
00401f07 8b 45 08        MOV        EAX,dword ptr [EBP + param_1]
00401f0a b9 0a 00        MOV        ECX,0xa
         00 00
00401f0f 99              CDQ
00401f10 f7 f9           IDIV       ECX
00401f12 50              PUSH       EAX
00401f13 e8 c0 b4        CALL       KERNEL32.DLL::Sleep                              void Sleep(DWORD dwMilliseconds)
         0c 00
00401f18 a1 98 de        MOV        EAX,[PTR_DAT_004dde98]                           = 004e04f4
         4d 00
00401f1d 8b 00           MOV        EAX=>DAT_004e04f4,dword ptr [EAX]
00401f1f e8 a8 8b        CALL       FUN_0044aacc                                     undefined FUN_0044aacc(int param
         04 00
00401f24 90              NOP
00401f25 5d              POP        EBP
00401f26 c3              RET
```

### Zawieszanie przy zakończeniu edycji tabelki
Jeżeli przed zapisem pliku, naciśniemy "Zakończ edycję", program będzie chciał, żebyśmy zapisali nasz projekt. 
Wskazanie ścieżki do zapisu spowoduje nieskończoną pętlę, a anulowanie spowoduje użycie starej wersji tabelki.

Rozwiązaniem było wyNOPowanie powtórzonej części handlera przycisku "Zakończ edycję" 
odpowiedzialnej za zapis i wczytanie tabelki po jej modyfikacji. Następnie potrzebne było zastąpienie tej części
kodem wywołującym handlera akcji zapisu z menu Plik (wtedy dialog o zapis wyświetli się tylko raz), po czym kod
kopiuje wskaźnik do nazwy pliku do zapisu do miejsca na wskaźnik do nazwy pliku do odczytu.

Jeżeli użytkownik nie wskazał pliku do zapisu, kod skacze do sekcji BŁĄD, która wyświetla komunikat
błędu (treść jest alokowana na stosie za pomocą wartości natychmiastowych) a tryb edycji tabelki nie kończy się.

Natomiast jeśli użytkownik wybrał plik do zapisu, to plik jest wczytywany na nowo (tak program oryginalnie odczytywał 
zmiany w tabelce).

Cała łatka zmieściła się w oryginalnej funkcji, ale jest trochę za duża na README.md.
Jest ona dostępna do wglądu w [main.py](main.py).

### Branding
Zamieniłem "2OO1" na "bonk" w okienku "O programie" :)

Oryginał:
```
00115F50 43 61 70 74 69 6F 6E 06 04 32 4F 4F 31 0C 46 6F Caption..2OO1.Fo
```

Po spatchowaniu:
```
00115F50 43 61 70 74 69 6F 6E 06 04 62 6F 6E 6B 0C 46 6F Caption..bonk.Fo
```