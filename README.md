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
Wskazanie ścieżki do zapisu spowoduje nieskończoną pętlę.

Najłatwiejszym sposobem na naprawę było wyłączenie zapisywania po zakończeniu edycji.

Funkcja FUN_00405158 ustawia flagę DAT_004ce167 na 1, co oznacza, że tabelka została zmodyfikowana.
DAT_004ce167 nie jest nigdzie indziej używana, więc możemy zamienić 0x1 na 0x0. Wtedy funkcja będzie zawsze
ustawiała tę flagę na fałsz, dzięki czemu program nie będzie prosić o zapis pliku po zakończeniu edycji tabelki.

Oryginał:
```                           
                             undefined __stdcall FUN_00405158(void)
             undefined         AL:1           <RETURN>
             undefined4        Stack[-0x8]:4  local_8                                 XREF[1]:     00405164(W)  
             undefined4        Stack[-0xc]:4  local_c                                 XREF[1]:     00405161(W)  
             undefined4        Stack[-0x10]:4 local_10                                XREF[1]:     0040515e(W)  
                             FUN_00405158
        00405158 55              PUSH       EBP
        00405159 8b ec           MOV        EBP,ESP
        0040515b 83 c4 f4        ADD        ESP,-0xc
        0040515e 89 4d f4        MOV        dword ptr [EBP + local_10],ECX
        00405161 89 55 f8        MOV        dword ptr [EBP + local_c],EDX
        00405164 89 45 fc        MOV        dword ptr [EBP + local_8],EAX
        00405167 c6 05 67        MOV        byte ptr [DAT_004ce167],0x1
                 e1 4c 00 01
        0040516e 8b e5           MOV        ESP,EBP
        00405170 5d              POP        EBP
        00405171 c2 08 00        RET        0x8
```

Po spatchowaniu:
```
                             undefined __stdcall FUN_00405158(void)
             undefined         AL:1           <RETURN>
             undefined4        Stack[-0x8]:4  local_8                                 XREF[1]:     00405164(W)  
             undefined4        Stack[-0xc]:4  local_c                                 XREF[1]:     00405161(W)  
             undefined4        Stack[-0x10]:4 local_10                                XREF[1]:     0040515e(W)  
        00405158 55              PUSH       EBP
        00405159 8b ec           MOV        EBP,ESP
        0040515b 83 c4 f4        ADD        ESP,-0xc
        0040515e 89 4d f4        MOV        dword ptr [EBP + local_10],ECX
        00405161 89 55 f8        MOV        dword ptr [EBP + local_c],EDX
        00405164 89 45 fc        MOV        dword ptr [EBP + local_8],EAX
        00405167 c6 05 67        MOV        byte ptr [DAT_004ce167],0x0
                 e1 4c 00 00
        0040516e 8b e5           MOV        ESP,EBP
        00405170 5d              POP        EBP
        00405171 c2 08 00        RET        0x8

```

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