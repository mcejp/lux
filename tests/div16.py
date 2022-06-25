import sys

xs = [1, 2, 3, 4, 5]

for i in range(3, 17):
    # xs.append(2**i - 2)
    xs.append(2**i - 1)
    if i < 16:
        xs.append(2**i)
        # xs.append(2**i + 1)

OUT_TAL, OUT_EXP = sys.argv[1:]

with open(OUT_TAL, "wt") as tst, open(OUT_EXP, "wt") as exp:
    tst.write("""
%EMIT { #18 DEO }
%HALT { #010f DEO }

|0000

|0100
""")

    for num in [0] + xs:
        for den in xs:
            tst.write(f"    #{num:04x} #{den:04x} ;&div16 JSR2 SWP EMIT EMIT\n")
            exp.write(f"{num//den:04x}")

    tst.write("    HALT\n")
    tst.write("&div16\n")
    tst.write("~../fw/div16_body.tal\n")
    exp.write("\n")
