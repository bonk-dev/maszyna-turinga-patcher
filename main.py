import hashlib
import sys


class ExeMd5Sum:
    UPX_PACKED = '0c1acd5ef5dcdc39656bfff63e9296a6'
    UNPACKED_ORIGINAL = '1228242632b6c88a9a1035f1f6f20b88'
    PATCHED = '891436d7c3847aa6fb382608df185d5d'


class ExitCodes:
    SUCCESS = 0
    BAD_USAGE = 1
    UPX_PACKED = 2
    ALREADY_PATCHED = 3
    INVALID_DIGEST_AFTER_PATCH = 4
    INVALID_FILE = 5


def patch_execute_loop(exe: bytearray):
    print("Patchowanie nieskończonej pętli przy wykonywaniu")
    nops = b"\x90\x90\x90\x90\x90\x66\x90\x90\x90\x90\x90\x66\x90\x90\x90\x90"
    offset = 0x14F7

    for b in nops:
        exe[offset] = b
        offset += 1

    exe[0x1524] = 0x90  # NOP the POP ECX, since we nopped PUSH ECX earlier


def patch_no_save_after_edit(exe: bytearray):
    print("Wyłączanie zapisu po kliknięciu \"zakończ edycję\" (naprawa pętli przy zapisie)")
    exe[0x476D] = 0x00  # always setting the dirty_file flag to false (it's not used anywhere else)


def patch_branding(exe: bytearray):
    print("Dodawanie brandingu :*")
    exe[0x115F59] = 0x62  # b
    exe[0x115F5A] = 0x6F  # o
    exe[0x115F5B] = 0x6E  # n
    exe[0x115F5C] = 0x6B  # k


def main():
    if len(sys.argv) <= 2:
        print("Użycie: main.py <ścieżka do maszyna_turinga.exe> <ścieżka do zapisu spatchowanego exe>")
        exit(ExitCodes.BAD_USAGE)

    exe_path = sys.argv[1]
    with open(exe_path, 'rb') as exe_file:
        exe_data = exe_file.read()
    exe_md5 = hashlib.md5(exe_data).hexdigest()

    print(f"MD5: {exe_md5}")

    match exe_md5:
        case ExeMd5Sum.UPX_PACKED:
            print('Najpierw musić wypakować maszyna_turinga.exe za pomocą UPX')
            exit(ExitCodes.UPX_PACKED)
        case ExeMd5Sum.PATCHED:
            print('Ten plik został już spatchowany')
            exit(ExitCodes.ALREADY_PATCHED)
        case ExeMd5Sum.UNPACKED_ORIGINAL:
            print('Plik poprawny, patchowanie w toku')
            exe_data_array = bytearray(exe_data)
            patch_execute_loop(exe_data_array)
            patch_no_save_after_edit(exe_data_array)
            patch_branding(exe_data_array)

            patched_md5 = hashlib.md5(exe_data_array).hexdigest()
            print(f"MD5 po patchu: {patched_md5}")

            if patched_md5 != ExeMd5Sum.PATCHED:
                print(f"MD5 powinno być: {ExeMd5Sum.PATCHED}. Coś poszło nie tak!")
                exit(ExitCodes.INVALID_DIGEST_AFTER_PATCH)

            exe_save_path = sys.argv[2]
            print(f"Zapisywanie do {exe_save_path}")
            with open(exe_save_path, 'wb') as exe_save_file:
                exe_save_file.write(exe_data_array)
                exe_save_file.flush()
            print("Sukces")
        case _:
            print("Nieprawidłowy plik (albo inna wersja - wspierana jest tylko v1.5)")
            exit(ExitCodes.INVALID_FILE)


if __name__ == "__main__":
    main()
