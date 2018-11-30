/*
Natasha Stallsmith
Purpose: To analyse occurances of theme words in the plays King Lear, As You Like It, and Antony & Cleopatra.
         Several of the methods print out tables which are meant to be copy and pasted into an Excel sheet and then made into a
            network using Google's Fusion Tables.
*/


import string

class Corpus:
    
    def __init__(self, filename, charlist):
        '''
        filename: a string input which is the name of the text file to be read
        charlist: a list of the characters in the play
        '''
        self.filename = filename
        self.charlist = charlist

        # Parts of this initializer are adapted from "King Lear Script Splitter" by Mario Nakazawa
        # The following code opens the text and associates each line with the appropriate speaker
        # This is done in the initilizer because it will need to be done for each object of the Corpus class before any 
        #     of the methods can be run

        phrases = open(self.filename + ".txt").read().lower().split("\n")
        splitScript = []
        # The meta information. The way the algorithm works is to keep the following three variable blank when there are 
        # no scene, act or stage directions. When these are NOT blank, they are added to the list of pairings.
        sceneInfo = ""
        actInfo = ""
        stageDirection = ""

        # Variables used to join a character with what s/he says in the play. We start with saying that no one has spoken yet.
        character = ""
        dialog = []
        for phrase in phrases:

            if phrase.upper() in self.charlist: 

                if character != "":    
                    splitScript.append( (character, dialog) )

                character = phrase.upper() # new character's name is stored for future.
                dialog = []         # reset the list of lines to empty

                # Put in the meta information, which is often embedded in the phrases after a character's name.
                if actInfo != "":
                    splitScript.append(("ACT", [actInfo]))
                    actInfo = ""        # RESET
                if sceneInfo != "":
                    splitScript.append(("SCENE", [sceneInfo]))
                    sceneInfo = ""      # RESET
                if stageDirection != "" :
                    splitScript.append(("STAGE", [stageDirection]))
                    stageDirection = "" # RESET

            # STAGE DIRECTION
            elif "exeunt" in phrase or "exit" in phrase or "enter" in phrase or "re-enter" in phrase:
                stageDirection = phrase

            # SCENE INFORMATION
            elif "scene" in phrase:
                sceneInfo = phrase

            # ACT INFORMATION
            elif "act" in phrase:
                actInfo = phrase

            # DIALOG
            else:
                dialog.append(phrase)
            

        # Clean the text up by removing blank spaces.

        fixedScript = []
        
        for quote in splitScript:
            (speaker, line) = quote   # We need to do this line to split the pairings

            if speaker in self.charlist: # We are looking only at dialog.
                fixedLine = []        # reset the dialog

                for phrase in line:

                    # Filter the blanks
                    if phrase != "":
                        fixedLine.append(phrase[4:])  # notice the "4" here... it is essentially saying "look at all the 
                                                      # characters from the 5'th one to the end"

                fixedQuote = "\n".join(fixedLine)
                fixedScript.append( (speaker, fixedQuote ) )    # now that we fixed the dialog, put the updated one into a new list

            else:                   # if we see anything else, then we simply copy it into the new list.
                fixedScript.append( (speaker, " ".join(line)))
        
        self.text = fixedScript

        wordsSection = []

        for speech in self.text:
            (speaker, quote) = speech
            translator = str.maketrans('', '', string.punctuation)   # https://stackoverflow.com/questions/34293875/how-to-remove-punctuation-marks-from-a-string-in-python-3-x-using-translate
            noPuncQuote = quote.translate(translator)  # strips punctuation

            wordsQuote = noPuncQuote.split() # splits into words
            wordsSection.append( (speaker, wordsQuote ) ) # formats back into list of tuples
        
        self.text = wordsSection
    
    
    def speaker_tally(self):
        '''to create a tally of the number of times each character speaks (and to whom)
           returns: matrix of speaker tallies and list of total times each character spoke
        '''
        tally = []

        # These loops make the matrix the right size
        # Help with bug: https://stackoverflow.com/questions/15988855/setting-values-in-matrices-python

        for item in range(len(self.charlist)):
            tallyRow = []
            tally.append(tallyRow)

            for num in range(len(self.charlist)):
                tallyRow.append(0)


        # Tallies the total number of times each character speaks and to whom
        lastSpoke = "STAGE"

        for speech in self.text:
            (speaker, quote) = speech

            current = self.charlist.index(speaker)
            prior = self.charlist.index(lastSpoke)
            tally[current][prior] += 1 # Add a tally in the appropriate section of the table, using the indexes

            lastSpoke = speaker # Moves current speaker to previous
            
        # Sums the prior matrix in to a list of total number of times each character speaks
        speakerSum = []
        for row in tally:
            total = sum(row)
            speakerSum.append(total)

        return tally, speakerSum
    
    
    def theme_tally(self, wordsList):
        """to create a tallies of the number of time specific words occur in the text, with the speaker in 
             the row and who they are speaking to in the column
           wordslist: a list of words to be found in the text
           returns: nested tables of word tallies and list of total occurances of each word
        """

        multitally = [] # This will be the final table with the appropiate number of rows and columns
        tally = []
        tallyRow = []

        # These loops make the list the right size
        # Help with bug: https://stackoverflow.com/questions/15988855/setting-values-in-matrices-python
        for table in range(len(wordsList)):
            tally = []

            for item in range(len(self.charlist)):
                tallyRow = []
                tally.append(tallyRow)

                for num in range(len(self.charlist)):
                    tallyRow.append(0)

            multitally.append(tally)


        # When a theme word occurs, the appropriate space in the matrix is incremented according to who is speaking and who is 
            # being spoken to
        lastSpoke = "STAGE"
        themeIndex = 0
        for item in wordsList:

            for speech in self.text:
                (speaker, quote) = speech

                for word in quote:

                    if item in word: # When the word is found, identify the indexes which match the current and previous speaker
                        current = self.charlist.index(speaker)
                        prior = self.charlist.index(lastSpoke)
                        multitally[themeIndex][current][prior] += 1 # Add a tally in the appropriate section of the table, using the indexes

                lastSpoke = speaker # Moves current speaker to previous

            themeIndex += 1 # Enters new matrix for each word

        # Sums the prior matrix into a list of the total times each word occured 
        themeSums = []    
        for table in multitally:
            count = 0
            for row in table:
                count += sum(row)
            themeSums.append(count)
        
        
        return multitally, themeSums
    
    
    def proportion(self, sums, num):
        """divides all integers in a list by the same number so they can be compared proportioanlly to another list
           sums: list of numerators (often sums of occurances)
           num: number to divide by (often total number of words)
           returns: list of floats"""
        
        prop = []
        for i in range(len(sums)):
            prop.append(sums[i] / num * 10000)   #10000 is an arbitrary number used to make sure the floats are not tiny decimals
        return prop

    
    def fusion_tables(self, tally_matrix, keywords):
        '''prints out three columns - the work, the word, and the number of occurances - to be copy and pasted 
              to make a network in fusion tables
           tally_matrix: list of occurances of each word (may be proportionalized)
           keywords: list of words in the order they were counted in the matrix
           returns: None
        '''      
        
        for item in range(len(tally_matrix)):
            print(self.filename + "   	" + str(keywords[item]) + "   	" + str(tally_matrix[item]))
        print()
     
    
    def fusion_tables_matrix(self, tally_matrix, char_list):
        '''prints out three columns - the speaker, spoken to, and the weight - to be copy and pasted 
              to make a network in fusion tables
           tally_matrix: 2D matrix counting occurances of speach by and to each person, generate using
              speaker_tally() method
           char_list: list of characters in the order they are in the matrix
           returns: None
        '''
        
        for row in range(len(tally_matrix)):
            for col in range(len(tally_matrix[row])):
                print(str(char_list[row] + "   	" + str(char_list[col]) + "   	" + str(tally_matrix[row][col])))
        print()
        
 def main():
    
    #TODO: Update word lists
    relationshipWords = ["father", "daughter", "son", "sister", "lord", "majesty", "sir", "madam"]  # list of relationship words
    sympathyWords = ["sorrow", "weep", "cause", "pity", "poor", "forlorn", "tears", "abused", "abuse", "old"]  # list of sympathy words
    
    
    learChars = ["KENT","GLOUCESTER","ALBANY","EDMUND","GONERIL","REGAN","CORDELIA","BURGUNDY", "KING OF FRANCE",
                 "KING LEAR", "LEAR", "FOOL","EDGAR","OSWALD","KNIGHT", "CORNWALL", "GENTLEMAN", "DOCTOR",
                 "STAGE", "ACT", "SCENE"]  # list of characters in King Lear
    learNum = 26145   # number of words in King Lear
    lear = Corpus("kinglear", learChars)  # creating object for King Lear
    
    
    cleoChars = ["ANTONY", "CLEOPATRA", "OCTAVIUS CAESAR", "OCTAVIA", "LEPIDUS", "ENOBARBUS", "DOMITIUS", "VENTIDIUS", 
                 "SILIUS", "EROS", "CANIDIUS", "SCARUS", "DERCETUS", "DEMETRIUS", "PHILO", "A SCHOOLMASTER", "CHARMIAN",
                 "IRAS", "ALEXAS", "MARDIAN", "SELEUCUS", "DIOMEDES", "MAECENAS", "AGRIPPA", "TAURUS", "THIDIAS", "DOLABELLA", 
                 "GALLUS", "PROCULEIUS", "SEXTUS POMPEIUS", "POMPEY", "MENAS", "MENECRATES", "VARRIUS", "MESSENGERS", 
                 "SOLDIERS", "SENTRIES", "GUARDSMEN", "A SOOTHSAYER", "SERVANTS", "A BOY", "A CAPTAIN", "AN EGYPTIAN", 
                 "A COUNTRYMAN", "Ladies", "Eunuchs", "Captains", "Officers", "Soldiers", "Attendants", "Servants",
                 "STAGE", "ACT", "SCENE"]  # list of characters in Antony and Cleopatra
    cleoNum = 24905   # number of words in Antony and Cleopatra
    cleo = Corpus("antonyandcleopatra", cleoChars)  # creating object for Antony and Cleopatra
    
    
    ayliChars = ["ORLANDO", "OLIVER", "SECOND BROTHER", "ADAM", "DENNIS", "ROSALIND", "CELIA", "TOUCHSTONE", 
                      "DUKE FREDERICK", "CHARLES", "LE BEAU", "FIRST LORD", "SECOND LORD", "DUKE SENIOR", "JAQUES", "AMIENS", 
                      "FIRST PAGE", "SECOND PAGE", "CORIN", "SILVIUS", "PHOEBE", "AUDREY", "WILLIAM", "SIR OLIVER MARTEXT",
                      "HYMEN", "Lords", "Attendants", "Musicians", "STAGE", "ACT", "SCENE"] # list of characters in As You Like It
    ayliNum = 21690   # number of words in As You Like It
    ayli = Corpus("asyoulikeit", ayliChars)  # creating object for As You Like It
    
    (learSpeakers, learSpeakersSum) = lear.speaker_tally()   # Counting who speaks how many times and to whom
    lear.fusion_tables_matrix(learSpeakers, learChars)  # Creating network of speakers and speaking to
    
    (ayliSpeakers, ayliSpeakersSum) = ayli.speaker_tally()  # Counting who speaks how many times and to whom
    ayli.fusion_tables_matrix(ayliSpeakers, ayliChars)   # Creating network of speakers and speaking to
    
    (cleoSpeakers, cleoSpeakersSum) = cleo.speaker_tally()  # Counting who speaks how many times and to whom
    cleo.fusion_tables_matrix(cleoSpeakers, cleoChars)  # Creating network of speakers and speaking to

    (learSymp, learSympSum) = lear.theme_tally(sympathyWords)  # Counting occurances of sympathy words and by/to whom
    learSympProp = lear.proportion(learSympSum, learNum)  # Proportionalizing word occurances by words in corpus
    (learRelat, learRelatSum) = lear.theme_tally(relationshipWords)  # Counting occurances of relationship words and by/to whom
    learRelatProp = lear.proportion(learRelatSum, learNum)  # Proportionalizing word occurances by words in corpus
    lear.fusion_tables(learSympProp, sympathyWords)  # Creating network of corpus and sympathy word occurances
    lear.fusion_tables(learRelatProp, relationshipWords)  # Creating network of corpus and relationship word occurances
    
    (ayliSymp, ayliSympSum) = ayli.theme_tally(sympathyWords)  # Counting occurances of sympathy words and by/to whom
    ayliSympProp = ayli.proportion(ayliSympSum, ayliNum)  # Proportionalizing word occurances by words in corpus
    (ayliRelat, ayliRelatSum) = ayli.theme_tally(relationshipWords)  # Counting occurances of relationship words and by/to whom
    ayliRelatProp = ayli.proportion(ayliRelatSum, ayliNum)  # Proportionalizing word occurances by words in corpus
    ayli.fusion_tables(ayliSympProp, sympathyWords)  # Creating network of corpus and sympathy word occurances
    ayli.fusion_tables(ayliRelatProp, relationshipWords)  # Creating network of corpus and relationship word occurances
    
    (cleoSymp, cleoSympSum) = cleo.theme_tally(sympathyWords)  # Counting occurances of sympathy words and by/to whom
    cleoSympProp = cleo.proportion(cleoSympSum, cleoNum)  # Proportionalizing word occurances by words in corpus
    (cleoRelat, cleoRelatSum) = cleo.theme_tally(relationshipWords)  # Counting occurances of relationship words and by/to whom
    cleoRelatProp = cleo.proportion(cleoRelatSum, cleoNum)  # Proportionalizing word occurances by words in corpus
    cleo.fusion_tables(cleoSympProp, sympathyWords)  # Creating network of corpus and sympathy word occurances
    cleo.fusion_tables(cleoRelatProp, relationshipWords)  # Creating network of corpus and relationship word occurances
 
 main()
