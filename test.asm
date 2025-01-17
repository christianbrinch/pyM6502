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

    LDA #$80            ; Place the low bit of the cursor position ...
    STA SCREEN_PTR      ; ... at the right spot on the screen
    LDA #$e7            ; Place the high bit of the cursor position ...
    STA SCREEN_PTR+1    ; ... at the right spot on the screen

; INPUT STARTS HERE
RESET_IP:
    LDA #0
    STA POS

INPUT:
    LDA #$25            ; Load cursor character code ...
    JSR GET_CHAR        ; ...and draw it on the screen

    LDA #$ff            ; Initialise
    STA $0600           ; the keyboard buffer with ff

IDLE:
; Wait for input
    LDA $0600           ; Load the keyboard buffer
    NOP                 ; Wait a bit
    NOP                 ; Wait a bit
    CMP #$ff            ; Test for input
    BEQ IDLE            ; No? Keep waiting
    CMP #$ab            ; Test for backspace
    BEQ BACKSPACE       ; Yes? Execute backspace
    CMP #$aa            ; Test for return
    BEQ RETURN          ; Yes? Execute return

; Put char in input buffer
    LDY POS
    STA (IP_PTR), Y
    INY
    STY POS
; Print char on screen
    DEC SCREEN_PTR
    JSR GET_CHAR
    JMP INPUT           ; Loop back to wait for more input

BACKSPACE:
    LDY POS
    DEY
    LDA #$00
    STA (IP_PTR), Y
    STY POS
    DEC SCREEN_PTR
    LDA #$24
    JSR GET_CHAR
    DEC SCREEN_PTR
    DEC SCREEN_PTR
    JMP INPUT


RETURN:
    DEC SCREEN_PTR     ; Move cursor back
    LDA #$24           ; Load space
    JSR GET_CHAR       ; Erase cursor
    JSR CARRIAGERETURN ; Move cursor to next line

; Parse input buffer here
    LDA #0
    CLC
    ADC $0610
    ADC $0611
    ADC $0612
    CMP #$17
    BEQ PEEK
    CMP #$27
    BEQ POKE
    CMP #$3c
    BEQ GOSYS
    JMP BAILOUT

GOSYS:
    JMP SYS

PEEK:
    LDA $0613       ; load character
    CMP #$0a        ; should be k
    BNE BAILOUT     ; if not, syntax error
    LDA $0614       ; load character
    CMP #$24        ; should be blank space
    BNE BAILOUT     ; if not, syntax error
    
    LDA $0615       ; load character, should be high nibble of high byte
    TAX             ; move to X
    LDA (CHAR2VALUE_PTR, X) ; convert character to number 
    ASL
    ASL
    ASL
    ASL
    STA TMP         ; Save for later
    LDA $0616
    TAX
    LDA (CHAR2VALUE_PTR, X)
    ADC TMP
    STA TMP+1
    LDA $0617
    TAX
    LDA (CHAR2VALUE_PTR, X)
    ASL
    ASL
    ASL
    ASL
    STA TMP
    LDA $0618
    TAX
    LDA (CHAR2VALUE_PTR, X)
    ADC TMP
    STA TMP
    LDX #0
    LDA (TMP, X)
    LSR
    LSR
    LSR
    LSR
    TAY
    LDA (VALUE2CHAR_PTR), Y
    JSR GET_CHAR
    LDX #0
    LDA (TMP, X)
    STA $0620
    AND #$0f
    STA $0621
    TAY
    LDA (VALUE2CHAR_PTR), Y
    JSR GET_CHAR
    JSR CARRIAGERETURN
    JMP RESET_IP

BAILOUT:
    BRK

POKE:
    LDA $0613
    CMP #$04
    BNE BAILOUT
    LDA $0614
    CMP #$24
    BNE BAILOUT
    LDA $0615
    TAX
    LDA (CHAR2VALUE_PTR, X)
    STA TMP
    LDA $0616
    TAX
    LDA (CHAR2VALUE_PTR, X)
    ADC TMP
    STA TMP+1
    LDA $0617
    TAX
    LDA (CHAR2VALUE_PTR, X)
    STA TMP
    LDA $0618
    TAX
    LDA (CHAR2VALUE_PTR, X)
    ADC TMP
    STA TMP
    LDA $0619
    CMP #$24
    BNE BAILOUT
    LDA $061a
    TAX
    LDA (CHAR2VALUE_PTR, X)
    ASL
    ASL
    ASL
    ASL
    STA TMP2
    LDA $061b
    TAX
    LDA (CHAR2VALUE_PTR, X)
    ADC TMP2
    LDX #0
    STA (TMP,X)
    JSR CARRIAGERETURN
    JMP RESET_IP

SYS:
    LDA $0613
    CMP #$24
    BNE BAILOUT
    LDA $0614
    TAX
    LDA (CHAR2VALUE_PTR, X)
    STA TMP
    LDA $0615
    TAX
    LDA (CHAR2VALUE_PTR, X)
    ADC TMP
    STA TMP+1
    LDA $0616
    TAX
    LDA (CHAR2VALUE_PTR, X)
    STA TMP
    LDA $0617
    TAX
    LDA (CHAR2VALUE_PTR, X)
    ADC TMP
    STA TMP
    LDX #0
    JMP (TMP)


CARRIAGERETURN:
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
    RTS







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

CHAR2VALUE_PTR:
    .byte $00, $0a

VALUE2CHAR_PTR:
    .byte $00, $0b

IP_PTR:
    .byte $10, $06

POS:
    .byte $00

TMP:
    .byte $00, $00
TMP2:
    .byte $00, $00

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

; Table for converting character codes to its numeric values
    .org $0a1a
    .byte $00, $01, $02, $03, $04, $05, $06, $07
    .byte $08, $09
    .org $0a00
    .byte $0a, $0b, $0c, $0d, $0e, $0f
; Table for converting numeric values to character codes
    .org $0b00
    .byte $1a, $1b, $1c, $1d, $1e, $1f, $20, $21
    .byte $22, $23, $00, $01, $02, $03, $04, $05

    .org $fffc
    .word $8000
