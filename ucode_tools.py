def iterate_uprog(UCODE_ROM, uaddr):
    while True:
        uins = UCODE_ROM[uaddr]
        yield uaddr, uins

        # hack for bad model in ucodecompiler
        if isinstance(uins, str):
            if "last=True" in uins:
                break
            else:
                uaddr += 1
                continue

        if uins.last:
            break
        else:
            uaddr += 1


def iterate_uprogs(UCODE_LUT, UCODE_ROM):
    for opcode, (uaddr, _) in sorted(UCODE_LUT.items()):
        yield opcode, iterate_uprog(UCODE_ROM, uaddr)
