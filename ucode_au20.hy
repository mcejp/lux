; "SFT" -> "UI_ALU(ALU_OP_SFT)"
(defmacro alu [op] `(+ "UI_ALU(ALU_OP_" ~op ")"))

; implement ALU instruction using appropriate operation (dynamic width)
(defmacro make-alu [name] `(opcode '~name :s-mode 'auto
    pop-bs
    pop-as
    (alu ~(str name))
    push-alu-s
))

; implement ALU instruction using appropriate operation (byte result always)
(defmacro make-alu8 [name] `(opcode '~name :s-mode 'auto
    pop-bs
    pop-as
    (alu ~(str name))
    push-alu-l
))

(setv alu-pass-a                (uins :alu_op 'ALU_OP_PASS_OP0 :alu_sel0 'ALU_SEL0_A :alu_sel1 'ALU_SEL1_X))
(setv dev-ld-at-a               (uins :mem_op 'MEM_LD_AT_A :mem_sp 'MEM_SP_DEV))
(setv dev-st-bh-at-a            (uins :mem_op 'MEM_ST_BH_AT_A :mem_sp 'MEM_SP_DEV))
(setv dev-st-bl-at-a            (uins :mem_op 'MEM_ST_BL_AT_A :mem_sp 'MEM_SP_DEV))
(setv pc-incr                   (uins :pc_op 'PC_INCR))
(setv ram-ld-at-a               (uins :mem_op 'MEM_LD_AT_A :mem_sp 'MEM_SP_RAM))
(setv ram-ld-at-pc              (uins :mem_op 'MEM_LD_AT_PC :mem_sp 'MEM_SP_RAM))
(setv ram-st-bh-at-a            (uins :mem_op 'MEM_ST_BH_AT_A :mem_sp 'MEM_SP_RAM))
(setv ram-st-bl-at-a            (uins :mem_op 'MEM_ST_BL_AT_A :mem_sp 'MEM_SP_RAM))
(setv warp-alu                  (uins :pc_op 'PC_WARP_ALU))
(setv warp-alu-if-bl-nonzero    (uins :pc_op 'PC_WARP_ALU_IF_BL_NONZERO))
(setv warp-dvec-s               (uins :pc_op 'PC_WARP_DVEC_S))

; alignment:
; 2nd op @ col 25
; comment @ col 41

(make-alu ADD)
(make-alu AND)

(opcode 'DEO
    pop-a-u8
    pop-bs
    dev-st-bl-at-a
)

(opcode 'DEO2
    ; note that we don't *need* to have the full word in a contiguous register
    ; so it's not necessary for the memory multiplexer work in that specific way (same for ST*2)
    pop-a-u8
   [pop-bs              alu-a-plus-1]
   [dev-st-bh-at-a      alu-to-a]
    dev-st-bl-at-a
)

(opcode 'DEI
    pop-a-u8
    dev-ld-at-a
    mem-to-bl                           ; TODO: worth adding more direct path?
    push-bs
)

(opcode 'DEI2
    pop-a-u8
    dev-ld-at-a
   [mem-to-bh           alu-a-plus-1]
    alu-to-a
    dev-ld-at-a
    mem-to-bl
    push-bs
)

(opcode 'DIV :s-mode 'auto
    rpush-pc-w
    warp-dvec-s
)

(opcode 'DUP :s-mode 'auto
    pop-as
    push-as
    push-as
)

(make-alu EOR)
(make-alu8 EQU)
(make-alu8 GTH)

(opcode 'INC :s-mode 'auto
    pop-as
    alu-a-plus-1
    push-alu-s
)

(opcode 'JCN
    pop-a-s8
   [pop-bs              alu-pc-plus-a]
    warp-alu-if-bl-nonzero
)

(opcode 'JCN2
    pop-as
   [pop-b-u8            alu-pass-a]
    warp-alu-if-bl-nonzero
)

(opcode 'JMP
    pop-a-s8
    alu-pc-plus-a
    warp-alu
)

(opcode 'JMP2
    ; TODO: worth adding direct path?
    ; optimally would POP AL and then jump while simultaneously removing AH from the stacks
    pop-as
    alu-pass-a
    warp-alu
)

(opcode 'JSR
    ; TODO: probably some uinsns can be merged
    pop-a-s8
    rpush-pc-w
    alu-pc-plus-a
    warp-alu
)

(opcode 'JSR2
    ; TODO: probably some uinsns can be merged
    pop-as
    rpush-pc-w
    alu-pass-a                          ; TODO: worth adding more direct path?
    warp-alu
)

; TODO: LDA, LDA2 mostly identical with LDZ, LDZ2; should de-duplicate in ucode
;       dtto for STA, STA2 <-> STZ, STZ2

(opcode 'LDA
    ; TODO: probably some uinsns can be merged
    pop-aw
    ram-ld-at-a
    mem-to-bl
    push-bs                             ; TODO: worth adding more direct path?
)

(opcode 'LDA2
    ; TODO: probably some uinsns can be merged
    pop-aw
    ram-ld-at-a                         ; load 1st byte
   [mem-to-bh           alu-a-plus-1]   ; save fetched value to BH, compute (A + 1)
    alu-to-a                            ; A <= A + 1
    ram-ld-at-a                         ; load 2nd byte
    mem-to-bl
    push-bs
)

(opcode 'LDR
    pop-a-s8
    alu-pc-plus-a
    alu-to-a
    ram-ld-at-a
    mem-to-bl
    push-bs
)

(opcode 'LDR2
    pop-a-s8
    alu-pc-plus-a                       ; compute (PC + A)
    alu-to-a                            ; A <= PC + A
    ram-ld-at-a                         ; load 1st byte
   [mem-to-bh           alu-a-plus-1]   ; save fetched value to BH, compute (A + 1)
    alu-to-a                            ; A <= A + 1
    ram-ld-at-a                         ; load 2nd byte
    mem-to-bl
    push-bs
)

(opcode 'LDZ
    pop-a-u8
    ram-ld-at-a
    mem-to-bl
    push-bs                             ; TODO: worth adding more direct path?
)

(opcode 'LDZ2
    pop-a-u8
    ram-ld-at-a                         ; load 1st byte
   [mem-to-bh           alu-a-plus-1]   ; save fetched value to BH, compute (A + 1)
    alu-to-a                            ; A <= A + 1
    ram-ld-at-a                         ; load 2nd byte
    mem-to-bl
    push-bs
)

(opcode 'LIT
    ; TODO: worth bypassing Regfile for loads?
    ;       (would need to propagate stall flag to stacks)
   [ram-ld-at-pc        pc-incr]
    mem-to-a-u8
    push-as
)

(opcode 'LIT2
   [ram-ld-at-pc        pc-incr]
    mem-to-ah
    ; TODO: would be nice to start the 2nd load on the last cycle of 1st
   [ram-ld-at-pc        pc-incr]
    mem-to-al
    push-as
)

(make-alu8 LTH)
(make-alu MUL)
(make-alu8 NEQ)

(opcode 'NIP :s-mode 'auto
    pop-as
    pop-s
    push-as
)

(make-alu ORA)

(opcode 'OVR :s-mode 'auto
    pop-as
    pop-bs
    push-bs
    push-as
    push-bs
)

(opcode 'POP :s-mode 'auto
    pop-s
)

(opcode 'ROT :s-mode 'auto
    pop-as
    pop-bs
    pop-cs
    push-bs
    push-as
    push-cs
)

(opcode 'SFT :s-mode 'auto
    pop-b-u8
    pop-as
    (alu "SFT")
    push-alu-s
)

(opcode 'STA
    pop-aw
    pop-bs
    ram-st-bl-at-a
)

(opcode 'STA2
    pop-aw
   [pop-bs              alu-a-plus-1]
   [ram-st-bh-at-a      alu-to-a]
    ram-st-bl-at-a
)

(opcode 'STH :s-mode 'auto
    pop-as
    rpush-as
)

(opcode 'STR
    pop-a-s8
   [pop-bs              alu-pc-plus-a]
    alu-to-a
    ram-st-bl-at-a                      ; TODO: path from ALU->Fet would be useful here
)

(opcode 'STR2
    pop-a-s8                            ; pop A
   [pop-bs              alu-pc-plus-a]  ; pop BL, compute (PC + A)
    alu-to-a                            ; A <= PC + A
   [ram-st-bh-at-a      alu-a-plus-1]   ; begin store [A] <= BH, compute (A + 1)
    alu-to-a                            ; A <= A + 1
    ram-st-bl-at-a                      ; begin store [A] <= BL
)

(opcode 'STZ
    pop-a-u8
    pop-bs
    ram-st-bl-at-a
)

(opcode 'STZ2
    pop-a-u8
   [pop-bs              alu-a-plus-1]
   [ram-st-bh-at-a      alu-to-a]
    ram-st-bl-at-a
)

(make-alu SUB)

(opcode 'SWP :s-mode 'auto
    pop-as
    pop-bs
    push-as
    push-bs
)
