import hashlib
import sys


class ExeMd5Sum:
    UPX_PACKED = '0c1acd5ef5dcdc39656bfff63e9296a6'
    UNPACKED_ORIGINAL = '1228242632b6c88a9a1035f1f6f20b88'
    PATCHED = 'c7fc05a1c1bbabc29f4fa331a850ffb4'


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
    print("Patchowanie zakończenia edycji tabelki")

    func_start = 0x44A4
    patch_body_address = func_start + 0x99

    # NOP patch_body area
    for i in range(patch_body_address, patch_body_address + 165):
        exe[i] = 0x90

    patch_body = bytes([
        # PATCH_BODY_START:
        0xE8, 0x5E, 0xF9, 0xFF, 0xFF,  # CALL context_menu_save_handler
        0xA1, 0x10, 0xE3, 0x4D, 0x00,  # MOV EAX, dword ptr [_Form1]
        0x8B, 0x80, 0xB4, 0x03, 0x00, 0x00,  # MOV EAX, dword ptr [EAX + 0x3B4]
        0x8B, 0x40, 0x78,  # MOV EAX, dword ptr [EAX + 0x78],
        0x85, 0xC0,  # TEST EAX, EAX
        0x89, 0x45, 0xB0,  # MOV dword ptr [EBP-0x50], EAX
        0x74, 0x48,  # JZ ERROR
        0x0F, 0xB6, 0x05, 0x66, 0xE1, 0x4C, 0x00,  # MOVZX EAX, byte ptr [last_file_valid]
        0x84, 0xC0,  # TEST AL, AL
        0x74, 0x3D,  # JZ ERROR
        0xA1, 0x10, 0xE3, 0x4D, 0x00,  # MOV EAX, dword ptr [_Form1]
        0x8B, 0x80, 0x78, 0x03, 0x00, 0x00,  # MOV EAX, dword ptr [EAX + 0x378]
        0x83, 0xC0, 0x78,  # ADD EAX, 0x78
        0x8D, 0x55, 0xB0,  # LEA EDX, dword ptr [EBP-0x50]
        0xE8, 0xF8, 0x02, 0x0A, 0x00,  # CALL (this is a __fastcall) copy_dialog_fname
        0x8B, 0x0D, 0x10, 0xE3, 0x4D, 0x00,  # MOV ECX, dword ptr [_Form1]
        0xE9, 0x3A, 0xFF, 0xFF, 0xFF,  # JMP IN_IF_BLOCK
        # PATCH_EPILOGUE:
        0xA1, 0x10, 0xE3, 0x4D, 0x00,  # MOV EAX, dword ptr [_Form1]
        0x8B, 0x80, 0x78, 0x03, 0x00, 0x00,  # MOV EAX, dword ptr [EAX + 0x378]
        0x8B, 0x40, 0x78,  # MOV EAX, dword ptr [EAX + 0x78],
        0x85, 0xC0,  # TEST EAX, EAX
        0x74, 0x45,  # JZ FUNCTION_EPILOGUE
        0xE8, 0xCE, 0xD4, 0xFF, 0xFF,  # CALL wczytaj_plik
        0xEB, 0x46,  # JMP FUNCTION_EPILOGUE
        0xCC, 0xCC, 0xCC,  # INT3, INT3, INT3 (leftovers, padding, could not be bothered to remove)
        # ERROR:
        0x83, 0xEC, 0x7C,  # SUB ESP, 0x7C
        0xC7, 0x45, 0x90, 0x4D, 0x75, 0x73, 0x69,  # MOV DWORD PTR [EBP-0x70], 0x6973754D
        0xC7, 0x45, 0x94, 0x73, 0x7A, 0x20, 0x7A,  # MOV DWORD PTR [EBP-0x6C], 0x7A207A73
        0xC7, 0x45, 0x98, 0x61, 0x70, 0x69, 0x73,  # MOV DWORD PTR [EBP-0x68], 0x73697061
        0xC7, 0x45, 0x9C, 0x61, 0x63, 0x20, 0x70,  # MOV DWORD PTR [EBP-0x64], 0x70206361
        0xC7, 0x45, 0xA0, 0x6C, 0x69, 0x6B, 0x21,  # MOV DWORD PTR [EBP-0x60], 0x216B696C
        0xC6, 0x45, 0xA4, 0x00,  # MOV byte ptr [EBP-0x5C], 0x00
        0x8D, 0x45, 0x90,  # LEA EAX, dword ptr [EBP-0x70]
        0x6A, 0x10,  # PUSH 0x10
        0x50,  # PUSH EAX
        0x50,  # PUSH EAX
        0x6A, 0x00,  # PUSH 0x00
        0xE8, 0xA7, 0x89, 0x0C, 0x00,  # CALL JMP.&MessageBoxA
        0x83, 0xC4, 0x7C  # ADD ESP, 0x7C
    ])

    i = 0
    for b in patch_body:
        exe[patch_body_address + i] = b
        i += 1

    if_block_end_address = func_start + 0x94
    if_block_end_patch = bytes([
        0xEB, 0x49,  # JMP PATCH_EPILOGUE
        0x90,  # NOP
        0x90,  # NOP
        0x90  # NOP
    ])

    i = 0
    for b in if_block_end_patch:
        exe[if_block_end_address + i] = b
        i += 1


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
