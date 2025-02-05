    .org $0000

MesLen:
    .byte $00       ; Message length
MesAddr:
    .word $0000     ; Message address

SPRITE_PTR:
    .word $1e00

DE:
    .word $0000
HL:
    .word $0000

    .org $08f3
PrintMessage:
    LDX #$00
    LDA (MesAddr,X)
    STA SPRITE_PTR
    LDA #$1e
    STA SPRITE_PTR+1
    JSR DrawChar
    INC MesAddr
    DEC MesLen
    LDA MesLen
    CMP #$00
    BNE PrintMessage
    RTS

DrawChar:
; Determine the character's address from the character pointer
    LDX #$03
DCloop:
    LDA SPRITE_PTR
    CLC
    ADC SPRITE_PTR
    STA SPRITE_PTR
    BCC DCskip
    INC SPRITE_PTR+1
DCskip:
    DEX
    CPX #$00
    BNE DCloop
    JMP DrawSimpSprite

    .org $09ad
Print4Digits:
    LDA DE
    JSR DrawHexByte
    LDA DE+1

DrawHexByte:
; Display 2 digits in A to the screen at HL
    PHA
    ROR ; <-- this fucks up
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
    JMP DrawChar


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

    .org $1439
DrawSimpSprite:
    LDY #$00
    LDA (SPRITE_PTR), Y
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
    .byte $ea, $ea, $ea, $ea, $ea, $ea, $ea, $ea
    JSR DrawStatus



    .org $191a
DrawScoreHead:
    LDA #$1c
    STA MesLen
    LDA #$1e
    STA HL
    LDA #$24
    STA HL+1
    LDA #$e4
    STA MesAddr
    LDA #$1a
    STA MesAddr+1
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
    STA HL
    STX HL+1
    JMP Print4Digits







DrawStatus:
; Draw score and credits
    ;JSR ClearScreen
    JSR DrawScoreHead
    brk
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

; DATA

    .org $1ae4
    ; " SCORE<1> HI-SCORE SCORE<2>"
    .byte $26, $12, $02, $0E, $11, $04, $24, $1B, $25, $26, $07, $08
    .byte $3F, $12, $02, $0E, $11, $04, $26, $12, $02, $0E, $11, $04
    .byte $24, $1C, $25, $26



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
