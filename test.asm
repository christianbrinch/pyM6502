    .org $0100
START:
; Print line 1 of welcome message
    LDA #$00            ; Load low bit of message address...
    STA MESSAGE_PTR     ; ... into zp variable
    LDA #$07            ; Load high bit of message address...
    STA MESSAGE_PTR+1   ; ... into zp vaiable
    LDA #31             ; Load message length...
    STA MESSAGE_LEN     ; ... into zp variable
    LDA #$45            ; Load low bit of screen coordinates...
    STA SCREEN_PTR      ; ... into zp variable
    LDA #$e1            ; Load high bit of screen coordinates...
    STA SCREEN_PTR+1    ; ... into zp variable
    JSR PRINTMESSAGE    ; Go print the message

    LDA #$1f
    STA MESSAGE_PTR
    LDA #26
    STA MESSAGE_LEN
    LDA #$87
    STA SCREEN_PTR
    LDA #$e2
    STA SCREEN_PTR+1
    JSR PRINTMESSAGE

    LDA #$39
    STA MESSAGE_PTR
    LDA #5
    STA MESSAGE_LEN
    LDA #$40
    STA SCREEN_PTR
    LDA #$e6
    STA SCREEN_PTR+1
    JSR PRINTMESSAGE

    LDA #$80
    STA SCREEN_PTR
    LDA #$e7
    STA SCREEN_PTR+1

; INPUT STARTS HERE
    LDA #0
    STA POS

INPUT:
    LDA #$3e
    STA MESSAGE_PTR
    LDA #$07
    STA MESSAGE_PTR+1
    LDA #1
    STA MESSAGE_LEN
    JSR PRINTMESSAGE

    LDA #$ff
    STA $0600
    LDA #$00
    STA MESSAGE_PTR
    LDA #$06
    STA MESSAGE_PTR+1
IDLE:
    ; Wait for input
    LDX #0
    LDA (MESSAGE_PTR, X)
    NOP
    NOP
    NOP
    NOP
    CMP #$ff                ; Test for input
    BEQ IDLE                ; No? Keep waiting
    CMP #$aa                ; Test for return
    BEQ RETURN              ; Yes? Execute return

; Put char in input buffer
    LDY POS
    STA (IP_PTR), Y
    INY
    STY POS
; Print char on screen
    LDA #1
    STA MESSAGE_LEN
    DEC SCREEN_PTR
    JSR PRINTMESSAGE

    JMP INPUT


RETURN:
    LDA #1
    STA MESSAGE_LEN
    DEC SCREEN_PTR
    LDA #26
    JSR PRINTMESSAGE
    LDX #0
    LDA SCREEN_PTR+1
    SBC #$e0
    STA SCREEN_PTR+1
    CLC

DIVIDE:
    LDA SCREEN_PTR+1
    CMP #$00
    BEQ DIV_DONE
    INX
    SBC #$01
    CMP #$00
    BEQ DIV_DONE
    STA SCREEN_PTR+1
    LDA SCREEN_PTR
    SBC #$41
    STA SCREEN_PTR
    LDA SCREEN_PTR+1
    SBC #$00
    STA SCREEN_PTR+1
    JMP DIVIDE
DIV_DONE:
    INX
    LDA #$e0
    STA SCREEN_PTR+1
    LDA #$00

MULTIPLY:
    CPX #$00
    BEQ MUL_DONE
    DEX
    CLC
    ADC #$a0
    BCC M_NOCARRY
    INC SCREEN_PTR+1
    CLC
M_NOCARRY:
    ADC #$a0
    BCC MULTIPLY

    INC SCREEN_PTR+1
    JMP MULTIPLY
MUL_DONE:
    STA SCREEN_PTR

; Parse input buffer here
    LDA #0
    CLC
    ADC $0610
    ADC $0611
    ADC $0612
    CMP #$17
    BEQ PEEK
    JMP BAILOUT

RESET_IP:
; Reset input buffer
    LDA #0
    STA POS
    JMP INPUT


PEEK:
    LDA $0613
    CMP #$0a
    BNE BAILOUT
    LDA $0614
    CMP #$24
    BNE BAILOUT
    LDA $0615
    LDX #0
    STA (MESSAGE_PTR, X)
    LDA #1
    STA MESSAGE_LEN
    ;DEC SCREEN_PTR
    JSR PRINTMESSAGE
    JMP RESET_IP

BAILOUT:
    BRK









PRINTMESSAGE:
    LDY #0
PMLOOP:
    LDA (MESSAGE_PTR), Y
    STY $aaaa
    JSR GET_CHAR
    LDY $aaaa
    INY
    CPY MESSAGE_LEN
    BNE PMLOOP
    RTS

GET_CHAR:
    STA CHAR_PTR
    LDA #$08
    STA CHAR_PTR+1
    LDA CHAR_PTR
    CLC
    ADC CHAR_PTR
    STA CHAR_PTR
    ADC CHAR_PTR
    STA CHAR_PTR
    ADC CHAR_PTR
    STA CHAR_PTR
    BCC DRAW_CHAR
    INC CHAR_PTR+1
    JMP DRAW_CHAR


DRAW_CHAR:
    LDX #0
    LDY #0
    LDA SCREEN_PTR+1
    PHA
LOOP:
    LDA (CHAR_PTR,X)
    STA (SCREEN_PTR),Y

    INX
    CPX #8
    BEQ DONE

    TYA
    CLC
    ADC #$28
    TAY
    BCC LOOP

    INC SCREEN_PTR+1
    JMP LOOP
DONE:
    PLA
    STA SCREEN_PTR+1
    INC SCREEN_PTR
    RTS

    .org $0000
    JMP START

MESSAGE_PTR:
    .byte $00, $00

MESSAGE_LEN:
    .byte $00

SCREEN_PTR:
    .byte $00, $00

CHAR_PTR:
    .byte $00, $00

IP_PTR:
    .byte $10, $06

POS:
    .byte $00

    .org $0600
    .byte $ff
    .org $0610
INPUTBUFFER:
    .byte $aa, $00, $00, $00, $00, $00, $00, $00
    .byte $00, $00, $00, $00, $00, $00, $00, $00

    .org $0700
MESSAGES:
    .byte $02, $07, $11, $08, $12, $13, $08, $00 ; CHRISTIA
    .byte $0d, $12, $24, $0f, $11, $0e, $06, $11 ; NS PROGR
    .byte $00, $0c, $00, $01, $0b, $04, $24, $02 ; AMABLE C
    .byte $0e, $0c, $0f, $14, $13, $04, $11      ; OMPUTER

    .byte $04, $0c, $14, $0b, $00, $13, $04, $03 ; EMULATED
    .byte $24, $20, $1f, $1a, $1c, $24, $00, $11 ;  6502 AR
    .byte $02, $07, $08, $13, $04, $02, $13, $14 ; CHITECTU
    .byte $11, $04                               ; RE


    .byte $11, $04, $00, $03, $18                ; ready
    .byte $25


    .org $0800
Characters:
    .byte $00, $10, $28, $44, $44, $7C, $64, $64 ; A: 0
    .byte $00, $78, $44, $44, $78, $64, $64, $78 ; B: 1
    .byte $00, $38, $44, $40, $60, $60, $64, $38 ; C: 2
    .byte $00, $78, $44, $44, $64, $64, $64, $78 ; D: 3
    .byte $00, $7c, $40, $40, $78, $60, $60, $7c ; E: 4
    .byte $00, $7c, $40, $40, $78, $60, $60, $60 ; F: 5
    .byte $00, $3c, $40, $40, $60, $6c, $64, $3c ; G: 6
    .byte $00, $44, $44, $44, $7c, $64, $64, $64 ; H: 7
    .byte $00, $38, $10, $10, $18, $18, $18, $38 ; I: 8
    .byte $00, $04, $04, $04, $04, $04, $64, $38 ; J: 9
    .byte $00, $44, $48, $50, $60, $70, $68, $64 ; K: a
    .byte $00, $40, $40, $40, $40, $60, $60, $7c ; L: b
    .byte $00, $44, $6c, $54, $54, $64, $64, $64 ; M: c
    .byte $00, $44, $44, $64, $74, $6c, $64, $64 ; N: d
    .byte $00, $38, $44, $44, $44, $64, $64, $38 ; O: e
    .byte $00, $78, $44, $44, $78, $60, $60, $60 ; P: f
    .byte $00, $38, $44, $44, $44, $74, $68, $34 ; Q: 10
    .byte $00, $78, $44, $44, $78, $70, $68, $64 ; R: 11
    .byte $00, $38, $44, $40, $38, $04, $44, $38 ; S: 12
    .byte $00, $7c, $10, $10, $18, $18, $18, $18 ; T: 13
    .byte $00, $44, $44, $44, $44, $64, $64, $38 ; U: 14
    .byte $00, $44, $44, $44, $44, $64, $28, $10 ; V: 15
    .byte $00, $44, $44, $44, $54, $74, $6c, $44 ; W: 16
    .byte $00, $44, $44, $28, $10, $28, $64, $64 ; X: 17
    .byte $00, $44, $44, $28, $10, $10, $10, $10 ; Y: 18
    .byte $00, $7c, $04, $08, $10, $20, $60, $7c ; Z: 19
    .byte $00, $38, $44, $4c, $54, $64, $44, $38 ; 0: 1a
    .byte $00, $10, $30, $10, $10, $10, $10, $38 ; 1: 1b
    .byte $00, $38, $44, $04, $18, $20, $40, $7c ; 2: 1c
    .byte $00, $7c, $04, $08, $18, $04, $44, $38 ; 3: 1d
    .byte $00, $08, $18, $28, $48, $7c, $08, $08 ; 4: 1e
    .byte $00, $7c, $40, $78, $04, $04, $44, $38 ; 5: 1f
    .byte $00, $1c, $20, $40, $78, $44, $44, $38 ; 6: 20
    .byte $00, $7c, $04, $08, $10, $20, $20, $20 ; 7: 21
    .byte $00, $38, $44, $44, $38, $44, $44, $38 ; 8: 22
    .byte $00, $38, $44, $44, $3c, $04, $08, $10 ; 9: 23
    .byte $00, $00, $00, $00, $00, $00, $00, $00 ; ' ': 24
    .byte $00, $7c, $7c, $7c, $7c, $7c, $7c, $7c ; cursor: 25

    .org $fffc
    .word $8000
