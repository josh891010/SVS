from os import close
import re
import py_midicsv as pm
import sys
#input file name
print('midi file:')
filename = input()
csv_string = pm.midi_to_csv(filename)
filename = filename.strip(".mid")

# Load the MIDI file and parse it into CSV format
with open("%s_converted.csv"%(filename), "w") as f:
    f.writelines(csv_string)

print('lyrics file:')
#get lyrics from file
lyrics_file = input()
lyrics_input = []
with open(lyrics_file, encoding='utf-8') as f:
    while 1:
        c = f.read(1)
        if not c: break
        if c == '\n' or c == ' ': continue
        lyrics_input.append(c)
        
#.csv to prepocess file
with open("%s_converted.csv"%(filename)) as f:
    notes_duration = []
    notes_pitch = []
    lyrics = []
    division = 1 
    note_on = -1
    note_off = -1
    pitch = '0'
    key = []
    time = []
    tempo = 0
    #lyric_check = False
    for line in f:
        line = line.strip('\n')
        per_line = line.split(', ')
        
        #the first line, get division(quarter note lenghth)
        if(per_line[2]=='Header'):
            division = int(per_line[5])

        #get tempo
        elif per_line[2]=='Tempo':
            tempo = round(60000000/int(per_line[3]),0)
            print(tempo)

        #get time signature
        elif per_line[2]=='Time_signature':
            time.append((int(per_line[3]), pow(2,int(per_line[4]))))
            print(time[0])

        #get key
        elif per_line[2]=='Key_signature':
            key.append((per_line[3],per_line[4]))
            print(key[0])

        #get lyrics
        elif(per_line[2]=='Lyric_t'):
            lyric = re.sub(r'\s+','',per_line[3]) #remove \n
            lyric = lyric.strip("\"")
            lyrics.append(lyric)
            lyric_check = True

        #get note on
        elif(per_line[2]=='Note_on_c'):
            #check if this note has lyric
            '''
            if lyric_check == False:
                print("Error! Some notes don't have its own lyric.")
                exit()
            '''

            #velocity = 0 as note off
            if(per_line[5]=='0\n'):
                if not lyrics_input:
                    print("Error! lyrics and melody are not the same length")
                    exit()
                note_off = int(per_line[1])
                duration = round((note_off - note_on)/division, 2)
                pitch = per_line[4]
                notes_duration.append(duration)
                notes_pitch.append(pitch)
                lyrics.append(lyrics_input.pop(0))
                note_on = -1
                #lyric_check = False

            else:
                if(note_on == -1): #if there are note_on before, than there is polyphony
                    note_on = int(per_line[1])

                    #silence between notes, output sil
                    if(note_on != note_off and note_off != -1): #silence between notes, output sil
                        duration = round((note_on - note_off)/division, 2)
                        pitch = '1'
                        notes_duration.append(duration)
                        notes_pitch.append(pitch)
                        lyrics.append('sil')

                else:
                    print("Error! Some notes are overlapping.")
                    exit()
                        


        #get note off
        elif(per_line[2]=='Note_off_c'):
            if not lyrics_input:
                print("Error! lyrics and melody are not the same length")
                exit()
            note_off = int(per_line[1])
            duration = round((note_off - note_on)/division, 2)
            pitch = per_line[4]
            notes_duration.append(duration)
            notes_pitch.append(pitch)
            lyrics.append(lyrics_input.pop(0))
            note_on = -1
            #lyric_check = False

    #check if lyrics are longer than melody
    if lyrics_input:
        print("Error! lyrics and melody are not the same length")
        exit()

    #output text
    with open('text.txt','w') as output:
        while(1):
            #output lyrics
            output.write('|')
            for i in range(10):
                if(not(lyrics)): break
                if(lyrics[0]=='sil'):
                    if(i==0): 
                        output.write("%s "%(lyrics.pop(0)))
                    elif(i==9 or len(lyrics)==1):
                        output.write(" %s"%(lyrics.pop(0)))
                    else:
                        output.write(" %s "%(lyrics.pop(0)))
                else:
                    output.write(lyrics.pop(0))

            #output notes pitch
            output.write('|')
            for i in range(10): #10 notes per line
                if(not(notes_pitch)): break
                if(i!=0): output.write(' ')
                output.write(notes_pitch.pop(0))

            #output notes duration
            output.write('|')
            for i in range(10):#10 notes per line
                if(not(notes_duration)): break
                if(i!=0): output.write(' ')
                output.write(str(notes_duration.pop(0)))

            if(not(notes_pitch)): break
            output.write('\n')