#format:

# Empty values are just "Z"
# In the example, X is just a placeholder for a number

#Pattern Examples: 
#00_[C_2_0D_ZZ_ZZZZ][ZZ_Z_ZZ_ZZ_ZZZZ][C_2_11_20_ZZZZ][ZZ_Z_ZZ_ZZ_ZZZZ][ZZ_Z_ZZ_ZZ_ZZZZ]
#01_[ZZ_Z_ZZ_ZZ_ZZZZ][C_2_0D_ZZ_ZZZZ][ZZ_Z_ZZ_ZZ_ZZZZ][ZZ_Z_ZZ_ZZ_ZZZZ][ZZ_Z_ZZ_ZZ_ZZZZ]
# And so on...

#line 1: aam
#line 2: name_author_album_tuning (Example: TheAntiAuto_Antiblue_Z_440)

# The next lines are for the subsongs

#line X: separator(~~~~~~~...)
#line X: subsongX_bpm_tempo_speeds(separate by -)_numberOrders_patternLength (Example: subsong0_150_8-6_4_64)
#line X: orderArrangement (Example: 00E00-01E00-02B00A01B00-03B00A01B00)
#line X: separator (*********...)
#line X: orderNumber
#line X-X: patternData (XX_[note_oct_ins_vol_effect][channel2data][channel3data][channel4data][beeperdata])
#This repeats for the other orders
#line X (after last order): separator(~~~~~~...)

#end of subsong lines

#Supported effects:
#0DZZ: jump to next pattern
#0BXX: jump to pattern
#04XY: vibrato (X: speed, Y: Depth)
#03XX: portamento
#01XX: pitch slide up
#02XX: pitch slide down
#ECXX: note cut

#Instruments 1D-20 are for the beeper only.
# 1D is a simple beeper on
# 1E is a kick (play C4, C3, F#2, E2, D2, G#1, F#1, D#1 really quickly)
# 1F is a snare (play C3, C2, C2, C3 really quickly and stop after 7 frames)
# 20 is a hit (play C4, F#6 really quickly and stop after 2 frames)

# special notes:
# REL for release
# OFF for cutting the note
# if there is no REL in the column where a note is playing, make the duration really long

# Instrument, sample, chip, and wavetable data can be ignored.


# Coming soon!!

print("Not right now.")