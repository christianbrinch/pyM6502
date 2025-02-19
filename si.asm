    .org $0000
A:
    .word $0000
DE:
    .word $0000
HL:
    .word $0000
BC:
    .word $0000
TMP:
    .word $0000

    .org $0060
SHFTAMNT:
    .byte $00
SHFTX:
    .byte $00
SHFTY:
    .byte $00

    .org $00a0
INP0:
    .byte $00
INP1:
    .byte $00
INP2:
    .byte $00


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
    LDA #$00
    STA A+1
    LDA A
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
    LDX #$08
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
    LDA #$00
    STA A+1
    ADC #$1a
    STA A
    JMP DrawChar

    .org $09d6
ClearPlayField:
    SEI             ; FIX THIS: the interupt fucks up the carry flag
    LDY #$00        ; Reset y register
    LDA #$02        ; Load
    STA HL          ; 0x2402 (top of video mem + offset)
    LDA #$24        ; into
    STA HL+1        ; HL
CPFloop:
    LDA #$00        ; Load a 0...
    STA (HL), Y     ; ...and store it in video mem

    CLC             ; Clear carry
    LDA HL          ; Load HL low byte
    ADC #$01        ; Move to next byte
    STA HL          ; and store it again
    BCC CPFskip1    ; If we cross the boundary...
    INC HL+1        ; ...increment high byte
CPFskip1:
    AND #$1f        ; Get x byte number...
    CMP #$1c        ; ...and compare to 28
    BNE CPFskip     ; If reached, move to next column
                    ; and otherwise check high byte
    LDA HL          ; Load low byte again
    CLC             ; Clear carry
    ADC #$06        ; Add 6 (4 byte in the top and 2 in the bottom)
    STA HL          ; Store it again
    BCC CPFskip     ; If we cross the byte boundary...  
    INC HL+1        ; ...increment high byte
CPFskip:    
    CLC
    LDA HL+1        ; Load high byte
    CMP #$40        ; Compare to 64
    BCC CPFloop     ; If reached, then out
    CLI             ; FIX THIS
    RTS


Animate:
; Start the ISR moving the sprite. Return when done.
    LDA #$02
    STA $20c1
Aniloop:
    LDA $20cb
    AND $20cb
    CMP #$00
    BEQ Aniloop
    LDA #$00
    STA $20c1
    RTS



PrintMessageDel:
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
    LDA #$07    ; A small delay between characters
    STA $20c0   ; this is controlled by the screen interrupt
PMDloop:
    LDA $20c0
    SBC #$01
    CMP #$00
    BNE PMDloop
    INC DE
    DEX
    CPX #$00
    BNE PrintMessageDel
    RTS

    .org $0ab1
OneSecDelay:
    LDA #$40
    JMP WaitOnDelay

TwoSecDelay:
    LDA #$80
    JMP WaitOnDelay

ISRSplTasks:
    LDA $20c1
    CLC
    ROR
    ;BCS SplashDemo
    ROR
    BCS SplashSpriteTrampoline
    ROR
    ;BCS SplashSquiggly
    RTS


PrintNearMidscreen:
; Message to center of screen.
; Only used in one place for "SPACE  INVADERS"
    LDA #$14
    STA HL
    LDA #$2b
    STA HL+1
    LDX #$0f
    JMP PrintMessageDel


WaitOnDelay:
    STA $20c0
WODloop:
    LDA $20c0
    AND $20c0
    CMP #$00
    BNE WODloop
    RTS

IniSplashAni:
    LDA #$c2
    STA HL
    LDA #$20
    STA HL+1
    LDX #$0c
    LDY #$00
    JMP BlockCopy

SplashSpriteTrampoline:
    JMP SplashSprite


SplashScreenloop:
    LDA #$00        ; for
    STA $20ec       ; debugging
    ;LDA #$02        ; purposes
    ;STA $20c1       ; only
; Splash screen loop
    LDA #$00
    ; STA SOUND1    Turn off sound
    ; STA SOUND2    Turn off sound
    CLI
    JSR OneSecDelay
    LDA #$17
    STA HL
    LDA #$30
    STA HL+1
    LDX #$04
    LDA $20ec   ; Load splashAnimate into A
    AND $20ec   ; Set flags based on type
    CMP #$00
    BNE OBE8            ; Not 0: print normal "PLAY"
    LDA #$fa
    STA DE
    LDA #$1c            ; Else: print "PLAupsidedown Y"
    STA DE+1
    JSR PrintMessageDel ; Print message with delay
    LDA #$af
    STA DE
    LDA #$1d
    STA DE+1
OBE8return:
    JSR PrintNearMidscreen
    JSR OneSecDelay
    JSR DrawAdvTable
    JSR TwoSecDelay
    LDA $20ec   ; Load splashAnimate into A
    AND $20ec   ; Set flags based on type
    CMP #$00
    BNE PlayDemo
    JMP AniRepY

OBE8:
    LDA #$ab
    STA DE
    LDA #$1d
    STA DE+1
    JSR PrintMessageDel
    JMP OBE8return

AniRepY:
; Animate alien replacing upside down Y with normal Y
    LDA #$95
    STA DE
    LDA #$1a
    STA DE+1
    JSR IniSplashAni
    JSR Animate         
 
    LDA #$b0
    STA DE
    LDA #$1b
    STA DE+1
    JSR IniSplashAni    
    JSR Animate
    JSR OneSecDelay
    
    LDA #$c9
    STA DE
    LDA #$1f
    STA DE+1
    JSR IniSplashAni
    JSR Animate         
    JSR OneSecDelay
    
    LDA #$d7                ; This should be 0xb7 according to SI code,
    STA HL                  ; but that does not quite match
    LDA #$33
    STA HL+1
    LDX #$0a
    LDY #$00
    JSR ClearSmallSprite
    JSR TwoSecDelay

PlayDemo:
    JSR ClearPlayField
    LDA $21ff
    AND $21ff
    CMP #$00
    BNE SkipShipReset    
    ;JSR GetShipsPerCred
    STA $21ff
    ;JSR RemoveShip
SkipShipReset:
    ;JSR CopyRAMMirror
    ;JSR InitAliens
    ;JSR DrawShieldPl1
    ;JSR RestoreShields1
    LDA #$01
    STA $20c1
    ;JSR DrawBottomLine

    brk
    sei



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

    .org $0c10
ScanLine224:
; end-of-screen interrupt (happens at line 224)
    SEI
    PHA             ; Push all hardware registers
    TXA
    PHA
    TYA
    PHA

    LDA DE          ; Push Software registers
    PHA
    LDA DE+1
    PHA
    LDA HL
    PHA
    LDA HL+1
    PHA
    LDA BC
    PHA
    LDA BC+1
    PHA



    DEC $20c0       ; Decrement general delay counter
    ; coin stuff goes here (0x0020 - 0x0041)
    LDA $20e9
    AND $20e9
    CMP #$00
    BEQ RestoreAndOut
    LDA $20ef
    AND $20ef
    CMP #$00
    BNE MainGamePLayTimingLoop
    LDA $20eb
    AND $20eb
    CMP #$00
    BNE CreditButNoGame
    JSR ISRSplTasks
    JMP RestoreAndOut

CreditButNoGame:


MainGamePLayTimingLoop:

RestoreAndOut:
    PLA
    STA BC+1
    PLA
    STA BC
    PLA
    STA HL+1
    PLA
    STA HL
    PLA
    STA DE+1
    PLA
    STA DE

    PLA             ; Pull all registers
    TAY
    PLA
    TAX
    PLA
    RTI

    .org $0c8c
; midscreen interupt continues here
    JMP RestoreAndOut


    .org $0cd9
AddDelta:
    INC HL          ; delta-x is in reg X. Move to delta-y
    LDA (HL), Y     ; load delta-y into A
    STA BC          ; store it in B
    INC HL          ; Go to x coordinate
    TXA             ; transfer delta-x to A
    ADC (HL), Y     ; add x coordinate to delta-x
    STA (HL), Y     ; and store it in x coordinate address
    INC HL          ; Go to y coordinate
    LDA BC          ; load delta-y into A
    ADC (HL), Y     ; add y coordinate
    STA (HL), Y     ; and store it back to y coordinate address
    RTS             ; out



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
DSSloop:
    LDA (DE), Y
    STA (HL), Y
    INC DE
    CLC
    LDA HL
    ADC #$20
    STA HL
    BCC DSSskip
    INC HL+1
DSSskip:
    DEX
    CPX #$00
    BNE DSSloop
    RTS

CnvtPixNumber:
; Convert pixel number in HL to screen coordinate and shift amount.
; HL gets screen coordinate.
    LDA HL+1
    AND #$07
    STA SHFTAMNT
    JMP ConvToScr

ClearSmallSprite:
; Clear a one byte sprite at HL. B=number of rows.
    LDA #$00
    STA (HL), Y
    LDA #$20
    CLC
    ADC HL
    STA HL
    BCC CSSskip
    INC HL+1
CSSskip:
    DEX
    CPX #$00
    BNE ClearSmallSprite
    RTS
    

ShiftSprite:
    LDY SHFTAMNT
ShfSloop:
    ASL SHFTX
    ROR SHFTY
    DEY
    BNE ShfSloop    
    RTS


    .org $15d3
DrawSprite:
    JSR CnvtPixNumber   ; I assume that this works.
    LDY #$00            ; Clear Y 
    LDA HL              ; Load
    PHA                 ; HL
    LDA HL+1            ; and
    PHA                 ; push to stack
DrSploop:
    LDA HL              ; Load
    PHA                 ; HL
    LDA HL+1            ; and   
    PHA                 ; push to stack
    LDA (DE), Y         ; Load sprite from DE

    LDA HL              ; This part is not
    CLC                 ; in the original
    ADC SHFTAMNT        ; SI code, but
    STA HL              ; it mimicks
    BCC teskip          ; hardware shift of sprites
    INC HL+1            ; to achieve smooth scrolling
teskip:                 ; Until here.

    LDA (DE),Y    
    STA (HL), Y

    INC HL              ; This is the part of the
    INC DE              ; original shift code
;    LDA #$00           ; which needs to be fixed 
;    STA SHFTY          ; once we do shots.
;    LDA SHFTX
;    STA (HL), Y
    PLA
    STA HL+1
    PLA
    STA HL
    
    LDA HL
    CLC
    ADC #$20
    STA HL
    BCC DrSpskip
    INC HL+1
DrSpskip:
    DEC BC
    BNE DrSploop
    PLA
    STA HL+1
    PLA
    STA HL
    RTS





    .org $1815
DrawAdvTable:
; Draw "SCORE ADVANCE TABLE"
    LDA #$10
    STA HL
    LDA #$28
    STA HL+1
    LDA #$a3
    STA DE
    LDA #$1c
    STA DE+1
    LDX #$15
    JSR PrintMessage
    LDA #$0a
    STA $206c
    LDA #$be
    STA BC
    LDA #$1d
    STA BC+1
DATloop:
    JSR ReadPriStruct
    BCS DATmoveon
    JSR Draw16ByteSprite
    JMP DATloop
;
    JSR OneSecDelay   ; This line of code is never reached
DATmoveon:
    LDA #$cf
    STA BC
    LDA #$1d
    STA BC+1
DATloop2:
    JSR ReadPriStruct
    BCS DATexit
    JSR PrintScoreMessage
    JMP DATloop2
DATexit:
    RTS

Draw16ByteSprite:
    LDX #$10
    JSR DrawSimpSprite
    RTS

PrintScoreMessage:
    LDX $206c
    JSR PrintMessageDel
    RTS



ReadPriStruct:
; Read a 4-byte print-structure pointed to by BC
; HL=Screen coordiante, DE=pointer to message
; If the first byte is FF then return with Carry Set, Carry Cleared otherwise.
    LDY #$00
    LDA (BC), Y
    CMP #$ff
    SEC
    BEQ RPSexit
    STA HL
    INC BC
    LDA (BC), Y
    STA HL+1
    INC BC
    LDA (BC), Y
    STA DE
    INC BC
    LDA (BC), Y
    STA DE+1
    INC BC
    CLC
RPSexit:
    RTS

SplashSprite:
; Move a sprite up and down in splash mode
    LDY #$00
    LDA #$c2        ; Load $20c2... 
    STA HL          ; ...  ($20c2 is the RAM location of 
    LDA #$20        ; ...   the animation structure)
    STA HL+1        ; ... into HL (low byte, hight byte)
    LDA (HL), Y     ; Increment...             
    ADC #$01        ; ... by 1
    STA (HL), Y     ; the value pointed to by HL
    INC HL          ; Increment the menory pointer 
    LDA (HL), Y     ; Load delta-x into A...
    TAX             ; and put it in X (it is zero, no movement in x-direction)
    JSR AddDelta    ; Calculate new coordinate (this has been tested and works)
    STA BC          ; A holds the new y coordinate. Put it in B
    LDA $20ca       ; load target y
    CMP BC          ; are we there yet?
    BEQ SplSexit    ; if yes... flag and out
    LDA $20cc       ; Load the address 0x1c20
    STA HL          ; into
    LDA $20cd       ; HL
    STA HL+1        ; so that HL is 201c (a word read from HL gives the right address)

    LDA $20c2       ; this code needs testing
    AND #$04        ;
    BNE SSnoflip    ;
    LDA HL          ;
    ADC #$30        ;
    STA HL          ; ...to here
SSnoflip:
    LDA HL          ; Load HL low byte
    STA $20c7       ; Store in animate struct
    LDA HL+1        ; Load HL high byte
    STA $20c8       ; Store in animate struct
    LDA #$c5        ; Load a word from animate struct
    STA HL          ; x and y coordinate address
    LDA #$20        ; into
    STA HL+1        ; HL (low byte, high byte: c520)
    JSR ReadDesc    ; Read the struct for plotting
    LDA DE          ; Exchange DE and HL
    STA TMP
    LDA DE+1
    STA TMP+1
    LDA HL
    STA DE
    LDA HL+1
    STA DE+1
    LDA TMP
    STA HL
    LDA TMP+1
    STA HL+1        ; Exchange done
    JMP DrawSprite

SplSexit:
    LDA #$01
    STA $20cb
    RTS



init:
    LDX #$00
    JSR $0de6                   ; This is the copy-rom-to-ram, but skipping the first insctruction
    JSR DrawStatus
    LDA #$08                    ; Load 8...
    STA $20cf                   ; ...into aShotReloadRate variable
    JMP SplashScreenloop        ; Jump to top of splash screen loop




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

PrintCreditLabel:
; Print message "CREDIT "
    LDX #$07
    LDA #$01
    STA HL
    LDA #$35
    STA HL+1
    LDA #$a9
    STA DE
    LDA #$1f
    STA DE+1
    JMP PrintMessage

DrawNumCredits:
    LDA $20eb
    LDA #$01
    STA HL
    LDA #$3c
    STA HL+1
    JMP DrawHexByte

PrintHiScore:
    LDA #$f4
    STA HL
    LDA #$20
    STA HL+1
    JMP DrawScore

DrawStatus:
; Draw score and credits
    JSR ClearScreen
    JSR DrawScoreHead
    JSR DrawPlayer1Score
    JSR DrawPlayer2Score
    JSR PrintHiScore
    JSR PrintCreditLabel
    JMP DrawNumCredits


    .org $1a00
BlockCopy:
    LDA (DE), Y
    STA (HL), Y
    INY
    DEX
    CPX #$00
    BNE BlockCopy
    RTS

ReadDesc:
    LDY #$00        ; Reset Y
    LDA (HL), Y     ; Load the x coordinate (0x20c5)
    STA DE          ; Store x coordinate into high byte of DE
    INC HL          ; Next address (0x20c6)
    LDA (HL), Y     ; Load the y coordinate
    STA DE+1        ; Store y coordinate into low byte of DE
    INC HL          ; go to low byte of image         
    LDA (HL), Y     ; load low byte of image
    STA TMP         ; store in tmp (tmp holds low byte)
    INC HL          ; go to high byte of image
    LDA (HL), Y     ; load the value
    TAX             ; Move high byte of image into X
    INC HL          ; Next byte
    LDA (HL), Y     ; Load a with size of image
    STA BC          ; into B
    TXA             ; High image byte back to A
    STA HL+1        ; Store into high byte of HL
    LDA TMP         ; Load low byte of image address
    STA HL          ; and put it into low byte of HL
    RTS

ConvToScr:
; The screen is organized as one-bit-per-pixel.
; In: HL contains pixel number (bbbbbbbbbbbbbppp)
; Convert from pixel number to screen coordinates (without shift)
; Shift HL right 3 bits (clearing the top 2 bits)
; and set the third bit from the left.; Convert pixel number in HL to screen coordinate
    LDX #$03
CTSloop:
    LDA HL+1
    ROR 
    STA HL+1
    LDA HL
    ROR
    STA HL
    DEX
    BNE CTSloop

    LDA HL+1
    AND #$3f
    ORA #$20
    STA HL+1
    RTS



ClearScreen:
    LDY #$00
    LDA #$00
    STA HL
    LDA #$24
    STA HL+1
CSstart:
    LDA #$00
    STA (HL),Y
    INY
    CPY $00
    BNE CSskip ; skip two instructions ahead
    INC HL+1
CSskip:
    LDA HL+1
    CMP #$40
    BNE CSstart   ; jump to CleanScreen line 2
    RTS


















; Static DATA ROM area below

    .org $1a93
    .byte $00, $00
; Splash screen animation (replacing y)
    .byte $00, $00, $FF, $B8, $FE, $20, $1C, $10, $9E, $00, $20, $1C


    .org $1ae4
    ; " SCORE<1> HI-SCORE SCORE<2>"
    .byte $26, $12, $02, $0E, $11, $04, $24, $1B, $25, $26, $07, $08
    .byte $3F, $12, $02, $0E, $11, $04, $26, $12, $02, $0E, $11, $04
    .byte $24, $1C, $25, $26

    .org $1c99
Message10Pts:
    ; Ran out of space at 1DFE
    .byte $27, $1B, $1A, $26, $0F, $0E, $08, $0D, $13, $12    ; "=10 POINTS"

MessageAdv:
    .byte $28, $12, $02, $0E, $11, $04, $26, $00
    .byte $03, $15, $00, $0D, $02, $04, $26, $13
    .byte $00, $01, $0B, $04, $28


    .org $1cfa
MessagePlayUY:
    .byte $0F, $0B, $00, $29    ; "PLAy" with an upside down 'Y' for splash screen

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
; Splash screen animation (replacing y)
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

    .org $1c00
AlienImages:
; Alien sprite type A,B, and C at positions 0
    .byte $00, $00, $39, $79, $7A, $6E, $EC, $FA, $FA, $EC, $6E, $7A, $79, $39, $00, $00
    .byte $00, $00, $00, $78, $1D, $BE, $6C, $3C, $3C, $3C, $6C, $BE, $1D, $78, $00, $00
    .byte $00, $00, $00, $00, $19, $3A, $6D, $FA, $FA, $6D, $3A, $19, $00, $00, $00, $00
; Alien sprite type A,B, and C at positions 1
    .byte $00, $00, $38, $7A, $7F, $6D, $EC, $FA, $FA, $EC, $6D, $7F, $7A, $38, $00, $00
    .byte $00, $00, $00, $0E, $18, $BE, $6D, $3D, $3C, $3D, $6D, $BE, $18, $0E, $00, $00
    .byte $00, $00, $00, $00, $1A, $3D, $68, $FC, $FC, $68, $3D, $1A, $00, $00, $00, $00

    .org $1d64
SpriteSaucer:
    .byte $00, $00, $00, $00, $04, $0C, $1E, $37, $3E, $7C, $74, $7E
    .byte $7E, $74, $7C, $3E, $37, $1E, $0C, $04, $00, $00, $00, $00


    .org $1dab
MessagePlayY:
    .byte $0F, $0B, $00, $18   ; "PLAY" with normal Y

MessageInvaders:
; "SPACE  INVADERS"
    .byte $12, $0F, $00, $02, $04, $26, $26, $08, $0D, $15, $00, $03, $04, $11, $12

; Tables used to draw "SCORE ADVANCE TABLE" information
    .byte $0E, $2C, $68, $1D           ; Flying Saucer
    .byte $0C, $2C, $20, $1C           ; Alien C, sprite 0
    .byte $0A, $2C, $40, $1C           ; Alien B, sprite 1
    .byte $08, $2C, $00, $1C           ; Alien A, sprite 0
    .byte $FF                          ; End of list

AlienScoreTable:
    .byte $0E, $2E, $E0, $1D           ; "=? MYSTERY"
    .byte $0C, $2E, $EA, $1D           ; "=30 POINTS"
    .byte $0A, $2E, $F4, $1D           ; "=20 POINTS"
    .byte $08, $2E, $99, $1C           ; "=10 POINTS"
    .byte $FF                          ; End of list

MessageMyst:
    .byte $27, $38, $26, $0C, $18, $12, $13, $04, $11, $18   ; "=? MYSTERY"

Message30Pts:
    .byte $27, $1D, $1A, $26, $0F, $0E, $08, $0D, $13, $12   ; "=30 POINTS"

Message20Pts:
    .byte $27, $1C, $1A, $26, $0F, $0E, $08, $0D, $13, $12   ; "=20 POINTS"

    .byte $00, $00 ; Padding to have char table start at 0x1e00

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

    .org $1f80
; small alien bringing y - animation 1
    .byte $60, $10, $0f, $10, $60, $30, $18, $1a, $3d, $68, $fc, $fc, $68, $3d, $1a, $00

    .org $1fa9
MessageCredit:
    .byte $02, $11, $04, $03, $08, $13, $26       ; "CREDIT " (with space on the end)

    .org $1fb0
; small alien bringing y - animation 2
    .byte $00, $60, $10, $0f, $10, $60, $38, $19, $3a, $6d, $fa, $fa, $6d, $3a, $19, $00


    .org $1fc0
    .byte $00, $20, $40, $4d, $50, $20, $00, $00  ; "?"

    .byte $00
; Splash animation (Replacing y)
    .byte $00, $00, $FF, $B8, $FF, $80, $1F, $10, $97, $00, $80, $1F

; RAM
; Starting at 0x2000



    .org $fffc
    .word $0c00
    .word $0000
