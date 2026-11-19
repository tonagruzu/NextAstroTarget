---
applyTo: '**'
---
1. Purpose of the project is to create application for selecting next target for astrophotography session.
2. All necessary information including required input data, dependences and rules has been collected in the "D:\REPOS\NextAstroTarget\Imm Deep Sky Compendium - 2023 - rev4g.xlsm" xlsm file. 
3. In the first step application called "Database initialization" application should take all the data included in the aboce spreadsheet and uplad it into local SQLight database. 
4. Once completed application should move to the next step which is process of selecting next target for astrophotography session. 
5. As soon as database is present and loaded with data application should skip the "Database initialization" step and move directly to the target selection step. 
Database will be updated in the future versions of the application so the "Database initialization" step should be always available for user to re-initialize database with updated data.

6. Application should have clean and user friendly GUI interface.
7. Application should be developed using Python programming language.   
8. Application should use only free open source libraries and dependences.
9. Application should be developed using modular approach so in the future new features can be added easily.    
10. Application should have proper error handling and logging implemented.
11. Application should be run by user on his local machine so all necessary installation instructions should be provided.
12. Application should be compatible with Windows 10 and Windows 11 operating systems.
13. Application should be able to access and utilize external APIs for additional data and functionality.
14. Application should have icon shortcut created on the user's desktop after installation.




User Guide (Refer to yellow section numbers above)

Section 1 (Timing and Location)

The user input required is shown in the blue data cells:
Date/Time  - 2 buttons are provided to set the time to “now” or  to sunset of the current day.  The 5 spin buttons, for month/day/year/hour/minute, easily increment columns to see specific times.   
The date/time cell may also be edited directly.  
DST – Indicate whether Daylight Savings Time is currently in effect for your location.
GMT Offset – Indicate the number of hours that your location is off from Greenwich Mean Time (i.e., Universal Time - UTC).  Hours west of GMT are negative.
Latitude and Longitude – Enter your location in degrees, minutes and seconds.  North and East are positive.

Clicking the Alphabetical Sort button sorts the objects by Object Name (Column A) .
Clicking the Transit Sort button sorts the objects by Transit Time (Column AD), starting with the time shown in the Date/Time field.
Clicking the 3rd gray button takes you back up to the top of the sheet.

Section 2 (Sun Data) -  Sun data is shown here for your selected time and location.
 
Section 3 (Moon Data) - Moon data is shown here for your selected time and location, including a graphic depiction of the moon phase.

Section 4  (Filtering Buttons)
This section allows one-click filtering of the spreadsheet in 115 different ways.  The blue button applies user-specified declinations limits, the green button applies user-specified size limits, the red buttons filter out the best targets, the blue dropdown button filters out catalogues, and the brown buttons filter out various DSO features.  The black button clears all of the filters except the declination and size ranges.  Applied filters show up as a funnel symbol next to the down arrows in Row 9.

Section 5 (Object Data)

Column A – “Object Name” 
Each deep sky object (DSO) is represented by one (and only one) spreadsheet row. An object may have multiple designations and the name used in Column A is my view of the most common designation of that object,  typically a Messier, NGC, or IC designation.  If the object has no such designation, I use a catalogue designation based on object type (e.g., Sh2 or vdB) or a common name.  
A low resolution mouseover image is shown for each object, usually my image but sometimes a publicly available sky atlas image (DSS or SDSS).  If I have imaged the object, the object name in Column A is a blue hyperlink which takes you to my Astrobin image of that object. 

Column B – “SIMBAD Link “
This hyperlink takes you to the SIMBAD web site for this object, containing detailed technical information.

Column C – “ALADIN Link“
This hyperlink takes you to the ALADIN sky atlas image of this object.

Column D – “Type“
The type of the object, either Galaxy, Nebula, or Star-related.

Column E – “Sub“
The subtype of the object, as described in the "Type-Subtype-Class" tab of this spreadsheet.

Column F – “Class“
The class of the object, as described in the "Type-Subtype-Class" tab of this spreadsheet.

Column G – “Size”
Object size in arc-minutes in our apparent view.  For comparison, the full moon as seen from earth is about 31 arc-minutes in diameter and Jupiter averages about 0.6 arc-minutes in diameter.  

Column H – “Distance”
Distance Definitions: - For Galaxies, shown in millions of lightyears
- For Milky Way objects, shown in lightyears (displayed in brown italics)

"u" indicates that the object distance is unknown at this time. 

Column I – “Diameter“
The actual diameter of the object.  Diameter Definitions:
- For Galaxies, shown in thousands of lightyears
- For Milky Way objects, shown in lightyears (displayed in brown italics)
- For galaxy groups, clusters, and chains, the size is the group diameter (underlined).
- For galaxy trios and pairs, the size is the diameter of the largest member.

"u" indicates that the object diameter is unknown at this time. 

Column J – “Rating“
Rating of the imaging potential of the object.  Object rating definitions:
5 - Top 2% of All Objects (Showcase Object)        4 - Top 10% of All Objects (Excellent)
3 - Top 25% of All Objects (Good)                       2 - Majority of Objects
1 - Only for hardcore imagers                                0 - Not worth imaging

Column K – “Notes“
Brief description of each object

Columns L and M – “Right Ascension”
Right Ascension, in hours/minutes/seconds, ranging from 0 to 24 across the sky in the west-east direction.

Columns N and O – “Declination”
Declination, in degrees/minutes/seconds, ranging from +90 to -90 across the sky in the north-south direction.  Because of my location in the northern hemisphere (+31 degrees declination), I am able to image objects from +90 degrees down to about -53 degrees.  Objects below -30 degrees declination are hard for me to image clearly because of atmospheric distortion. 

Column P – “Constellation”
Constellation in the sky where the object is located.  

Column Q – “Nickname”
600 object nicknames are shown here, the largest list of DSO nicknames anywhere.

Column R – “Alternative ID”
Many objects have multiple designations.  The most common designation is shown in Column A, the rest are shown here in Column R.

Column S – “Nearby Objects”
Nearby objects are listed here, generally within 0.5 degrees of the primary object.  Combining these objects in a single FOV for shorter focal length systems can be effective.

Column T – “Visual Magnitude”
The visual magnitude of an object when available.  For some galaxy groups as noted, particularly Hickson groups, this is the magnitude of the group.

Column U – “Surface Brightness”
The surface brightness of an object, in magnitudes per square arc-second, when available.  Surface brightness values are the most uncertain of any DSO data parameter.For some galaxy groups as noted, particularly Hickson groups, this is the brightness of the group.

Column V – “Inclination”
For single galaxies. Definition:
Face-on = 0 deg
Edge-on = 90 deg

Section 6 (My Section)
The next 3 columns are for you to use to highlight object priority, flag imaging status, and write comments:

Column W – “Row Color”
Sets the color of the row:
"1" objects are marked with a light green fill.
"2" objects are marked with a light yellow fill.
"3" objects are marked with a light red fill.

Use this "stoplight" flag to indicate object priority, scope assignment, or whatever you choose.

Column X – “Imaging Status”
Sets the status of the imaged object:
"p" objects (planned) are marked with a dotted pattern.
"i" objects (in-progress) are marked with a diagonal line pattern.
"f" objects (finished) are marked with a gray fill.

Column Y – “Imaging Status”
Free-form column for anything you want to include about this object.

Section 7 (Altitude Next 6 Hours)
Columns Z thru AC:  The first column shows the altitude at the current time.  The next column to the right is 2 hours later, the next column is 4 hours later, and the final column of this subsection is 6 hours later.  Each cell is color coded to indicate altitude, ranging from high (green) to medium (yellow) to low (red).  Adjust the time by hour using the spin button to see how the altitude changes throughout the night and to plan on imaging the object at its highest value.
 
“Sun Status” - This bar shows the status of the sun for the next 6 hours.  Yellow means that the sun is up, grey means that the sun is between sunset and nautical twilight (-12 degrees), and black means that the sun is below nautical twilight.   Many imagers use nautical twilight as the time to start RGB imaging.

Section 8 (Object Transit)
Column AD - "Transit Time"
The transit time is the time of the evening when the object is at its maximum elevation.  

Column AE - "Transit Date"
The transit date is when the object transits (crosses the meridian) at midnight.  During daylight savings time, transit occurs at 1 a.m.  Objects imaged near transit have the least amount of intervening atmosphere.  

Column AF - "Transit Altitude"
The transit altitude is the maximum elevation of the object in the night sky.    CCP (Circumpolar) indicates that the object is always visible.

Section 9 (Moon)
Column AG - "Separation"
Moon separation is the distance in degrees between the moon and the object.  90 degrees is equivalent to halfway across the sky.

Column AH - "Index"
The index quantifies the effect of both moon separation and moon phase.  Blue indicates good RGB imaging conditions.  The use of narrowband filters allows imaging into red conditions.
 
Section 10 (Catalogues)
Columns AI thru BH:  The next 26 columns are cross-referenced DSO catalogues.  In row 8, a mouseover comment attached to each catalogue title provides a brief description of the catalogue.  Also in Row 8, hyperlinks take you to my AstroBin compilation poster for that column.  The number in row 9 is the number of objects contained in that column.  
