####################################
## info regarding Data_Raw folder ##
####################################

Date of creation: 2018-02-27
Author: Guillaume Dauphin

Last Edit: July 15 2021

# This file makes reference to older masterfiles mot present on W:/
# contact G. Dauphin for copies of older versions

## Discharge Data

01BC001_KED
01BD009_MAT
01BE001_UPS
01BJ007_MAin

For 01BC001_KED,01BE001_UPS and 01BE001_UPS
 data for 2016,2017 is not final (cf Michel Desjardins email)

MAT_discharge.csv the discharge data comes from whoever was running the wheel , not environment canada






##### FULL DATA


##### 
smolts_trapdata_master.csv

RPMs for Butters in 2021 /4. numbers provided were not actual RPMs but counts of drum support (x4)


master_smolt_data_GD_Jul_2021.csv

Found an issue in the script where non-RT fish with a frequency >1 were not accounted for
changing script and making sure that all fields have a frequency

Littlemain: 2003 
removed unecessary 'last tag' column info


Upsalquitch:
on may 14th, two fish indicated as RR (B98351 & B98372) Guillaume was present on the day, fish likely going through the buckets holes when stored
in the box of the RST. 
decided to remove this tag from the analysis since it was probably released downstream

may 1st: tag number wrong corrected B99813 -> B97813
may 14th: fish sampled for scales were entered twice, fixed the entry

FL 11 -> 110 (May 18th)

Kedgwick: 
FL 12.9 -> 129 (May 19th)
FL 230 -> 130 (May 25th)

Butters: converted FL and total length from cm to mm


Moses:
Found an issue with a fish from 2019 (24th may) that had no status and in comment was listed as tag broken. (removed the tag number B87765)
and listed it as R (released unasampled)


corrected frequencies for Kedgwick may 13th, Upsalquitch may 12th, 14th and 18th



##### 

master_smolt_data_GD_Nov_2019.csv

entering the smolt (MZ and MR)taken for cindy's project
On the 12th of June 16 fish with no info on their provenance so randomly attributed to Moses and Butters


#####

master_smolt_data_GD_june_2019.csv

Adding 2019 Data to the database
for Moses a couple of species codes duplicated in the first_tag column for RR fish
changed a couple of frequencies

in upsalquitch on may 21st changed the last tag to B91715 because the starting tag the following day is B91716
in upsalquitch on may 29th changed the last tag to B97355 because the starting tag the following day is B97356

changed total length from cm to mm for the time period 2002->2006
attempted to change species code for lampreys 140 ->150(adult)
						  ->151(amnocoete)
						  ->152(silver)


##########
master_smolt_data_GD_Fev_2019.csv

Upsalquitch
30/05 replacing B91xxx with B92xxx to match data sheets
31/05 RR B92524-> B92527

Moses
31/05 changing B89161 -> B89181
01/06 changing last tag B89233 -> B89232

Butters
02/06 changing the starting tag B89252 ->B89253

##########
master_smolt_data_GD_Apr_2018.csv

+ adding 2018 data

+ Looking at size frequency I found a number of 'smolts' that were very small (<80mm)
  Seems to occur only for Moses data in 2003 and 2017 -> 15 fish changed from 1732 to 1731 species code
  
##########
master_smolt_data_GD_Mar_2018.csv

+ Added the Matapedia data (2016 & 2017)
+ Added the Little Main data (2003; there was no warks used in 2002 from what I could salvage)
  Also since a mix of streamer and fin clips were used I created a tag ID for clipped fish (C3xxx or C4xxx)
  using the size to determine which were recaptured. it works to get the captures and recaptures but I wouldn't
  use this wheel to calculate any duration of the time between recaptures. 
  Also this wheel is a bit tricky since there are a lot of marked fish that are RS



##########
master_smolt_data_GD_Fev_2018.csv
Contains an edited version of the original Master file that was provided by DFO:
Major modification: add a tags removed column, listing all the tags removed with a standardized format

"minor errors" such as (Line numbers are incorrects because reported from some filtered datasets, my bad !):

L413 added the Tag #A56013 to the "first tag" collumn (MR)
L1064 tag mortality
L1413-1418 copied the coments to the Scale ID  
L10241 Freq changed from 1 to 36
L12566 comment "cancel tag" but smolt still listed as RT should it be listed as "R"
L13879 what is RRL ?
L14727 end tag changed from A133412 to A13412
L22446-48,22489-90.22633-34,22763 different TAG# in the comment collum not sure what it means,	
				They tried the tag in the comment collumn and it was deffective?
L22801-02,22829
L32889-90,32898.32901,32918,32920,32923-24,32929,32935,32935,32945,
L33240,33242,33277,33314,33370,33527,33536,33686-7,33838-9,33957,
L34307-8,35154,35399,35528,35674   
-> TAG ID have a 'O' instead of '0', all changed

L37328 tag end changed to B06310 fromB062310
L49198 added a line to split the series in two continuous tag series numbers: B15993-B16000 and B44001-B44378
L54435 tag end changed to B64690 from B644690
L61337 tag end changed to B71049 from B701049
L62310 tag end changed to B71329 from B713299
 
