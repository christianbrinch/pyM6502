    .org $0000
A:
    .word $0000
DE:
    .word $0000
HL:
    .word $0000

    .org $08f3
PrintMessage:
    LDY #$00
    TXA
    PHA
    LDA DE
    PHA
    LDA DE+1
    PHA
    LDA (DE),Y
    JSR DrawChar
    PLA
    STA DE+1
    PLA
    STA DE
    PLA
    TAX
    INC DE
    DEX
    CPX #$00
    BNE PrintMessage
    RTS

DrawChar:
; Determine the character's address from the character pointer
    LDY #$03
    STA A
DCloop:
    CLC
    ADC A
    STA A
    BCC DCskip
    INC A+1
DCskip:
    DEY
    CPY #$00
    BNE DCloop
    STA DE
    LDA A+1
    ADC #$1e
    STA DE+1

    JMP DrawSimpSprite

    .org $09ad
Print4Digits:
    LDA DE
    JSR DrawHexByte
    LDA DE+1

DrawHexByte:
; Display 2 digits in A to the screen at HL
    PHA
    ROR
    ROR
    ROR
    ROR
    AND #$0f
    JSR Bump2NumberChar
    PLA
    AND #$0f
    JSR Bump2NumberChar
    RTS

Bump2NumberChar:
    ADC #$1a
    STA A
    LDA #$1e
    STA A+1
    JMP DrawChar

    .org $0ab1
OneSecDelay:
    LDA #$40
    JMP WaitOnDelay

    .org $0ad7
WaitOnDelay:
    brk

    .org $0aea
; Splash screen loop
    LDA #$00
    ; STA SOUND1    Turn off sound
    ; STA SOUND2    Turn off sound
    ; Enable interupt here
    JSR OneSecDelay


    .org $0c00
Reset:
    NOP
    NOP
    NOP
    JMP init
    byte $00, $00

ScanLine96:
; midscreen interrupt (happens at scanline 128)
    PHA
    TXA
    PHA
    TYA
    PHA
    JMP $0c8c   ; adjust to actual address

ScanLine224:
; end-of-screen interrupt (happens at line 224)
    SEI
    PHA
    TXA
    PHA
    TYA
    PHA

    PLA
    TAY
    PLA
    TAX
    PLA
    RTI

    .org $0c8c
    JMP $0c82

    .org $0d00
; z80's $0100 has been moved here
    .org $0de4
CopyRAMMirror:
    LDX #$c0
    LDY #$00
    LDA #$00
    STA DE
    LDA #$1b
    STA DE+1
    LDA #$00
    STA HL
    LDA #$20
    STA HL+1
    JMP BlockCopy





    .org $1439
DrawSimpSprite:
    LDY #$00
    LDX #$00
    LDA (DE), Y
    STA (HL, X)
    CLC
    LDA HL
    ADC #$20
    STA HL
    BCC DSSskip
    INC HL+1
DSSskip:
    INY
    CPY #$08
    BNE $143b
    RTS



    .org $18D4
init:
    LDX #$00
    JSR $0de6       ; This is the copy-rom-to-ram, but skipping the first insctruction
    JSR DrawStatus
    LDA #$08        ; Load 8...
    STA $20cf       ; ...into aShotReloadRate variable
    JMP $0aea       ; Jump to top of splash screen loop




    .org $191a
DrawScoreHead:
    LDX #$1c
    LDA #$1e
    STA HL
    LDA #$24
    STA HL+1
    LDA #$e4
    STA DE
    LDA #$1a
    STA DE+1
    JMP PrintMessage

DrawPlayer1Score:

    LDA #$f8
    STA HL
    LDA #$20
    STA HL+1
    JMP DrawScore

DrawPlayer2Score:
    LDA #$fc
    STA HL
    LDA #$20
    STA HL+1
    JMP DrawScore

DrawScore:
    LDY #$00
    LDA (HL),Y
    STA DE+1
    INC HL
    LDA (HL),Y
    STA DE
    INC HL
    LDA (HL),Y
    TAX
    INC HL
    LDA (HL),Y
    STA HL+1
    STX HL
    JMP Print4Digits


    .org $1a32
BlockCopy:
    LDA (DE), Y
    STA (HL), Y
    INY
    DEX
    CPX #$00
    BNE BlockCopy
    RTS


DrawStatus:
; Draw score and credits
    ;JSR ClearScreen
    JSR DrawScoreHead
    JSR DrawPlayer1Score
    JSR DrawPlayer2Score

    .org $1A5c
ClearScreen:
    LDY #$00
    LDA #$00
    STA ($00),Y
    INY
    CPY $00
    BNE $1a69 ; skip two instructions ahead
    INC $01
    LDA $01
    CMP #$40
    BNE $1a5e   ; jump to CleanScreen line 2
    LDA #$24
    STA $01
    RTS

; Static DATA ROM area below

    .org $1ae4
    ; " SCORE<1> HI-SCORE SCORE<2>"
    .byte $26, $12, $02, $0E, $11, $04, $24, $1B, $25, $26, $07, $08
    .byte $3F, $12, $02, $0E, $11, $04, $26, $12, $02, $0E, $11, $04
    .byte $24, $1C, $25, $26

    .org $1b00
;-------------------------- RAM initialization -----------------------------
; Coppied to RAM (2000) C0 bytes as initialization.
    .byte $01, $00, $00, $10, $00, $00, $00, $00, $02, $78, $38, $78, $38, $00, $F8, $00
    .byte $00, $80, $00, $8E, $02, $FF, $05, $0C, $60, $1C, $20, $30, $10, $01, $00, $00
    .byte $00, $00, $00, $BB, $03, $00, $10, $90, $1C, $28, $30, $01, $04, $00, $FF, $FF
    .byte $00, $00, $02, $76, $04, $00, $00, $00, $00, $00, $04, $EE, $1C, $00, $00, $03
    .byte $00, $00, $00, $B6, $04, $00, $00, $01, $00, $1D, $04, $E2, $1C, $00, $00, $03
    .byte $00, $00, $00, $82, $06, $00, $00, $01, $06, $1D, $04, $D0, $1C, $00, $00, $03
    .byte $FF, $00, $C0, $1C, $00, $00, $10, $21, $01, $00, $30, $00, $12, $00, $00, $00
    .org $1b70
MesssageP1:
; "PLAY PLAYER<1>"
    .byte $0F, $0B, $00, $18, $26, $0F, $0B, $00, $18, $04, $11, $24, $1B, $25, $FC, $00

    .byte $01, $FF, $FF, $00, $00, $00, $20, $64, $1D, $D0, $29, $18, $02, $54, $1D, $00
    .byte $08, $00, $06, $00, $00, $01, $40, $00, $01, $00, $00, $10, $9E, $00, $20, $1C

AlienSprCYA:
; Alien sprite type C pulling upside down Y
    .byte $00, $03, $04, $78, $14, $13, $08, $1A, $3D, $68, $FC, $FC, $68, $3D, $1A, 00

    .byte $00, $00, $01, $B8, $98, $A0, $1B, $10, $FF, $00, $A0, $1B, $00, $00, $00, $00

; Shot descriptor for splash shooting the extra "C"
    .byte $00, $10, $00, $0E, $05, $00, $00, $00, $00, $00, $07, $D0, $1C, $C8, $9B, $03

AlienSprCYB:
; Alien sprite type C pulling upside down Y - alternate
    .byte $00, $00, $03, $04, $78, $14, $0B, $19, $3A, $6D, $FA, $FA, $6D, $3A, $19, $00

; More RAM initialization copied by 18D9
    .byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $01, $00, $00, $01, $74, $1F, $00
    .byte $80, $00, $00, $00, $00, $00, $1C, $2F, $00, $00, $1C, $27, $00, $00, $1C, $39
;--------------------------- End of RAM initialization copy -------------------------

    .org $1E00
Characters:
    .byte $00, $1F, $24, $44, $24, $1F, $00, $00
    .byte $00, $7F, $49, $49, $49, $36, $00, $00
    .byte $00, $3E, $41, $41, $41, $22, $00, $00
    .byte $00, $7F, $41, $41, $41, $3E, $00, $00
    .byte $00, $7F, $49, $49, $49, $41, $00, $00
    .byte $00, $7F, $48, $48, $48, $40, $00, $00
    .byte $00, $3E, $41, $41, $45, $47, $00, $00
    .byte $00, $7F, $08, $08, $08, $7F, $00, $00

    .byte $00, $00, $41, $7F, $41, $00, $00, $00
    .byte $00, $02, $01, $01, $01, $7E, $00, $00
    .byte $00, $7F, $08, $14, $22, $41, $00, $00
    .byte $00, $7F, $01, $01, $01, $01, $00, $00
    .byte $00, $7F, $20, $18, $20, $7F, $00, $00
    .byte $00, $7F, $10, $08, $04, $7F, $00, $00
    .byte $00, $3E, $41, $41, $41, $3E, $00, $00
    .byte $00, $7F, $48, $48, $48, $30, $00, $00

    .byte $00, $3E, $41, $45, $42, $3D, $00, $00
    .byte $00, $7F, $48, $4C, $4A, $31, $00, $00
    .byte $00, $32, $49, $49, $49, $26, $00, $00
    .byte $00, $40, $40, $7F, $40, $40, $00, $00
    .byte $00, $7E, $01, $01, $01, $7E, $00, $00
    .byte $00, $7C, $02, $01, $02, $7C, $00, $00
    .byte $00, $7F, $02, $0C, $02, $7F, $00, $00
    .byte $00, $63, $14, $08, $14, $63, $00, $00

    .byte $00, $60, $10, $0F, $10, $60, $00, $00
    .byte $00, $43, $45, $49, $51, $61, $00, $00
    .byte $00, $3E, $45, $49, $51, $3E, $00, $00
    .byte $00, $00, $21, $7F, $01, $00, $00, $00
    .byte $00, $23, $45, $49, $49, $31, $00, $00
    .byte $00, $42, $41, $49, $59, $66, $00, $00
    .byte $00, $0C, $14, $24, $7F, $04, $00, $00
    .byte $00, $72, $51, $51, $51, $4E, $00, $00

    .byte $00, $1E, $29, $49, $49, $46, $00, $00
    .byte $00, $40, $47, $48, $50, $60, $00, $00
    .byte $00, $36, $49, $49, $49, $36, $00, $00
    .byte $00, $31, $49, $49, $4A, $3C, $00, $00
    .byte $00, $08, $14, $22, $41, $00, $00, $00
    .byte $00, $00, $41, $22, $14, $08, $00, $00
    .byte $00, $00, $00, $00, $00, $00, $00, $00
    .byte $00, $14, $14, $14, $14, $14, $00, $00

    .byte $00, $22, $14, $7F, $14, $22, $00, $00
    .byte $00, $03, $04, $78, $04, $03, $00, $00

; RAM
; Starting at 0x2000



    .org $fffc
    .word $0c00
    .word $0000
