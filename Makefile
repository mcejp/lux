all: all_runtime ucode_au20.html
all_runtime: fw/fw.rom ucode_au20_gen.py

fw/fw.rom: fw/fw.tal fw/div16_body.tal
	cd fw ; uxnasm $(notdir $<) $(notdir $@)

ucode_au20_gen.py: ucode_au20.hy ucodecompiler2.py
	./ucodecompiler2.py $< $@

ucode_au20.html: ucode_au20_gen.py aurora_doc_html.py
	./aurora_doc_html.py $<

.PHONY: test
test: all_runtime tests/div_instr.rom tests/hello2.rom
	$(MAKE) -C uxn-instruction-tests

	./expect tests/div_instr.exp ./aurora_sim.py -hex tests/div_instr.rom
	./expect tests/hello2.exp ./aurora_sim.py -hex tests/hello2.rom

	./expect tests/arithmetic.exp ./aurora_sim.py -hex uxn-instruction-tests/arithmetic.rom
	./expect tests/jumps.exp ./aurora_sim.py -hex uxn-instruction-tests/jumps.rom
	./expect tests/literals.exp ./aurora_sim.py -hex uxn-instruction-tests/literals.rom
	./expect tests/memory.exp ./aurora_sim.py -hex uxn-instruction-tests/memory.rom
	./expect tests/stack.exp ./aurora_sim.py -hex uxn-instruction-tests/stack.rom

tests/div16_gen.tal: tests/div16.py
	python3 $< tests/div16_gen.tal tests/div16_gen.exp

tests/%.rom: tests/%.tal
	cd tests ; uxnasm $(notdir $<) $(notdir $@)

# slow, so a separate target
.PHONY: test_div16
test_div16: all_runtime tests/div16_gen.rom
	./expect tests/div16_gen.exp ./aurora_sim.py -hex tests/div16_gen.rom
